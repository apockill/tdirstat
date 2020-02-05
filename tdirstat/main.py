import sys
import os
from argparse import ArgumentParser
from pathlib import Path

from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError, StopApplication

from .crawler import DirectoryStat, get_mounts
from .view import TDirStatView


def main():
    parser = ArgumentParser()
    parser.add_argument("root_dir", default=Path.cwd(), nargs="?",
                        type=Path,
                        help="The directory to analyze")
    args = parser.parse_args()

    dirstat = None

    def demo(screen: Screen, old_scene):
        nonlocal dirstat
        on_stats_change = lambda *args, **kwargs: screen.force_update()
        if dirstat is None:
            dirstat = DirectoryStat(
                path=str(args.root_dir.absolute()),
                on_stats_change=on_stats_change,
                mounts_to_ignore=get_mounts())
        # Make sure this gets set each time the screen resizes
        dirstat._on_stats_change = on_stats_change
        screen.play(
            [Scene([TDirStatView(screen, dirstat)], duration=-1)],

            stop_on_resize=True,
            start_scene=old_scene)

    last_scene = None
    while True:
        try:
            Screen.wrapper(demo, catch_interrupt=True, arguments=[last_scene])
            sys.exit(0)
        except ResizeScreenError as e:
            last_scene = e.scene


if __name__ == "__main__":
    main()
