import shutil
from typing import Optional
from enum import Enum, auto

from asciimatics.event import KeyboardEvent
from asciimatics.widgets import (
    Frame, Layout,
    MultiColumnListBox,
    Widget,
    Label,
    Button,
    RadioButtons,
    PopUpDialog,
    Text,
    Divider)
from asciimatics.screen import Screen
from asciimatics.exceptions import StopApplication

from .crawler import DirectoryStat, NodeStat, fmt_bytes
from .progress_bar import generate_progress_bar, spinner

spinner = spinner(delay_seconds=0.25)


class PercentMode(Enum):
    rel_to_drive_usage = "% of Drive"
    rel_to_dir = "% of Directory"


class TDirStatView(Frame):
    def __init__(self, screen, dirstat: DirectoryStat):
        super(TDirStatView, self).__init__(
            screen, screen.height, screen.width,
            has_border=True,
            name="My Form")
        # Model
        self.dirstat: DirectoryStat = dirstat
        self.disk_usage = shutil.disk_usage(str(self.dirstat.path)).used

        # Settings
        self.percent_mode = PercentMode.rel_to_dir

        # Create layouts
        layout_1 = Layout([1], fill_frame=True)
        layout_2 = Layout([1, 1])
        self.add_layout(layout_1)
        self.add_layout(layout_2)

        titles = [("Name", 0), ("%", "20>"), ("Size", "15>"), ("Items", "15>")]
        self._list = MultiColumnListBox(
            height=Widget.FILL_FRAME,
            columns=[c[1] for c in titles],
            titles=[c[0] for c in titles],
            options=[],
            name="qdirstat_list",
            on_select=self.enter_directory,
            on_change=self.details)

        self._details = Text()
        self._details.disabled = True
        self._details.custom_colour = "field"

        percent_mode_radio_btn = RadioButtons(
            [("% Relative to Directory", PercentMode.rel_to_dir),
             ("% Relative to Drive", PercentMode.rel_to_drive_usage)],
            on_change=lambda: self.set_percent_mode(
                percent_mode_radio_btn.value))

        layout_1.add_widget(Label("TDirStat"))
        layout_1.add_widget(Divider())
        layout_1.add_widget(self._list)
        layout_1.add_widget(Divider())

        layout_2.add_widget(self._details, column=0)
        layout_2.add_widget(
            column=1,
            widget=percent_mode_radio_btn)

        layout_2.add_widget(Label("Press Enter to select or `q` to quit."))
        # Prepare the Frame for use
        self.fix()

    def update(self, frame_no):
        prev_value = self._list.value

        options = []
        dirstats = list(self.dirstat.directories)
        dirstats.sort(key=lambda dirstat: dirstat.total_size, reverse=True)
        files = self.dirstat.files
        files.sort(key=lambda file: file.size, reverse=True)

        # Populate the first item on the list with a special case
        options = [(
            ["/" if self.dirstat.parent is None else "../",
             "",
             str(self.dirstat.total_size_pretty),
             str(round(self.dirstat.total_items, 2))],
            self.dirstat.parent)
        ]
        spin = next(spinner) + ' '

        # Adjust the percenage bars based on the "% mode" setting
        if self.percent_mode == PercentMode.rel_to_dir:
            total_size = self.dirstat.total_size
        else:
            total_size = self.disk_usage

        for dirstat in dirstats:
            pathname = dirstat.path.name
            columns = [
                f"{spin if not dirstat.finished.is_set() else ''}{pathname}/",
                generate_progress_bar(dirstat.total_size, total_size, 15),
                str(dirstat.total_size_pretty),
                str(round(dirstat.total_items, 2))
            ]
            options.append((columns, dirstat))

        for file in files:
            columns = [
                file.path.name,
                generate_progress_bar(file.size, total_size, 15),
                str(file.size_pretty),
                ""
            ]
            options.append((columns, file))
        self._list.options = options
        self._list.value = prev_value
        super().update(frame_no)

    def enter_directory(self):
        if not isinstance(self._list.value, DirectoryStat):
            return
        self.dirstat = self._list.value

    def prompt_delete(self):
        # Just confirm whenever the user actually selects something.
        item: Optional[NodeStat, DirectoryStat] = self._list.value
        if item is None:
            return

        def maybe_delete_directory(should_delete):
            if should_delete:
                try:
                    self.dirstat.delete_child(item)
                except Exception as e:
                    self.display_error(e)

        popup = PopUpDialog(
            self._screen,
            f"Are you sure you want to delete {self._list.value.path}",
            ["No", "Yes"],
            theme="tlj256",
            on_close=maybe_delete_directory)

        self._scene.add_effect(popup)

    def set_percent_mode(self, percent_mode: PercentMode):
        self.percent_mode = percent_mode
        self._list._titles[1] = percent_mode.value
        self.screen.force_update()

    def display_error(self, exception):
        error_popup = PopUpDialog(
            self._screen,
            f"{type(exception).__name__}, {exception}",
            ["Ok"],
            theme="tlj256")
        self._scene.add_effect(error_popup)

    def details(self):
        if self._list.value is None:
            self._details.value = ""
        else:
            self._details.value = f"Selected {str(self._list.value.path)}"

    def process_event(self, event):
        # Do the key handling for this Frame.
        if isinstance(event, KeyboardEvent):
            DEL_KEY = -102
            if event.key_code in [ord('q'), ord('Q'), Screen.ctrl("c")]:
                raise StopApplication("User quit")
            if event.key_code == DEL_KEY:
                self.prompt_delete()
        # Now pass on to lower levels for normal handling of the event.
        return super().process_event(event)
