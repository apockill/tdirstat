import os
import math
import logging
from queue import Queue
from threading import Event, Thread
from typing import List, Union, Optional
from pathlib import Path
from collections import namedtuple

_worker = None
_work_queue: Queue = Queue()


def _worker():
    while True:
        work_fn, output_queue = _work_queue.get(block=True)
        out = work_fn()
        output_queue.put(out)


def _submit_work(func) -> Queue:
    output_queue = Queue()
    _work_queue.put((func, output_queue))
    return output_queue


def fmt_bytes(size_bytes):
    """Return a nice 'total_size' string with Gb, Mb, Kb, and Byte ranges"""
    units = ["Bytes", "kB", "MB", "GB"]
    if size_bytes == 0:
        return f"{0} Bytes"
    for unit in units:
        digits = int(math.log10(size_bytes)) + 1
        if digits < 4:
            return f"{round(size_bytes, 1)} {unit}"
        size_bytes /= 1024
    return f"{size_bytes} TB"


class NodeStat:
    path: Path
    size: float
    """Size is in Gigabytes"""

    def __init__(self, path: Union[str, os.DirEntry]):
        if isinstance(path, os.DirEntry):
            self._path = path.path
            self.size = path.stat().st_size

        elif isinstance(path, str):
            self._path = path
            self.size = os.stat(path).st_size
        else:
            raise RuntimeError(f"Invalid type for path: {type(path)} {path}")

    @property
    def path(self) -> Path:
        if not isinstance(self._path, Path):
            self._path = Path(self._path)
        return self._path

    def __repr__(self):
        return f"NodeStat(path={self.path}, size={self.size_pretty})"

    @property
    def size_pretty(self) -> str:
        return fmt_bytes(size_bytes=self.size)


class DirectoryStat(NodeStat):
    """Crawl a filesystem in parallel and get statistics about structure and
    size of directories."""

    def __init__(self,
                 path: Union[str, os.DirEntry],
                 executor: Optional[Thread] = None,
                 on_stats_change=None,
                 parent: 'DirectoryStat' = None):
        super().__init__(path=path)
        self.finished: Event = Event()
        self.parent = parent
        self._on_stats_change = on_stats_change

        # Statistics
        """This is turned true when all children have finished scanning"""
        self.total_items = 0
        self.total_size = 0

        self.worker_thread = executor
        if self.worker_thread is None:
            self.worker_thread = Thread(target=_worker, daemon=True)
            self.worker_thread.start()
        self._future = _submit_work(self._get_children)

    def __repr__(self):
        return f"{self.__class__.__name__}(" \
               f"directory='{str(self.path)}', " \
               f"total_items={self.total_items}, " \
               f"total_size={self.total_size_pretty}, " \
               f"finished={self.finished.is_set()})"

    def __iter__(self):
        for child in self.children:
            yield child

    @property
    def children(self) -> List['DirectoryStat']:
        return sum(self._scan_result())

    @property
    def directories(self) -> List['DirectoryStat']:
        return self._scan_result()[0]

    @property
    def files(self) -> List['NodeStat']:
        return self._scan_result()[1]

    def _scan_result(self):
        if isinstance(self._future, Queue):
            self._future = self._future.get()
        return self._future

    @property
    def total_size_pretty(self):
        return fmt_bytes(size_bytes=self.total_size)

    def _get_children(self):
        try:
            try:
                entries = os.scandir(self._path)
            except (PermissionError, FileNotFoundError):
                entries = []

            child_directories = []
            child_files = []

            for entry in entries:
                try:
                    self.total_items += 1
                    if not entry.is_symlink():
                        if entry.is_dir() and not os.path.ismount(entry):
                            dirstat = DirectoryStat(
                                path=entry,
                                executor=self.worker_thread,
                                parent=self,
                                on_stats_change=self.add_items)
                            child_directories.append(dirstat)
                        else:
                            child_files.append(NodeStat(path=entry))

                except (PermissionError, FileNotFoundError) as e:
                    pass
                except Exception as e:
                    logging.critical("Unexpected error scanning file "
                                     f"{entry.path}: {type(e)} {e}")
            if len(child_directories) == 0:
                self.finished.set()

            # Get information about child folders
            # child_files = [NodeStat(path=entry) for entry in child_files]
            for node in child_files + child_directories:
                self.total_size += node.size

            if self._on_stats_change is not None:
                self._on_stats_change(self)

            return child_directories, child_files
        except Exception as e:
            logging.critical(f"Error: {e} {type(e)}")

    def add_items(self, changed_dirstat: 'DirectoryStat'):
        """Children nodes call this on parent methods so that parents can
        reflect the sum of items that children have found."""

        self.total_items += changed_dirstat.total_items
        self.total_size += changed_dirstat.total_size
        assert not self.finished.is_set(), \
            "How can a child update a parent if the parent has already been" \
            "marked as 'finished'?"

        # Check if this node is ready to be 'finished' as well
        if (changed_dirstat.finished.is_set()
                and all(dir.finished.is_set() for dir in self.directories)):
            self.finished.set()

        if self._on_stats_change is not None:
            # Optimization: Make sure there re changes that actually need to be
            # passed up the chain
            if changed_dirstat.total_items > 0 or self.finished.is_set():
                self._on_stats_change(changed_dirstat)
