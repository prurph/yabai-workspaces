from __future__ import annotations

import logging
from pathlib import Path
from typing import List

from .models import Window, Workspace
from .utils import ordered_groupby
from .yabai import Yabai
from .layouts.window_handler import WindowHandler


class WorkspaceManager:
    def __init__(self, yabai: Yabai, handlers: List[WindowHandler] = []):
        self.yabai = yabai
        self.handlers: dict[str, WindowHandler] = {}
        for handler in handlers:
            self.register_handler(handler)

    def save(self, workspace: Workspace, path: str) -> None:
        outfile = Path(path)
        outfile.parent.mkdir(exist_ok=True, parents=True)

        for win in workspace.windows:
            self.will_save(win)

        outfile.write_text(
            workspace.json(by_alias=True, ensure_ascii=False, indent=2, sort_keys=True)
        )

    # TODO: options to not reuse windows, to close stuff beforehand, to hide or minimize, etc
    def restore(self, workspace: Workspace) -> None:
        self.yabai.clean_slate()
        connected_displays = {d.index for d in self.yabai.displays()}

        for display, spaces in ordered_groupby(
            workspace.spaces,
            sortkeyby=lambda x: x.display,
            sortvaluesby=lambda x: x.index,
        ).items():
            missing_display = display not in connected_displays
            if missing_display:
                logging.warn("Workspace defines unknown display index %d", display)

            for i, space in enumerate(spaces):
                if i > 0 or missing_display:
                    self.yabai.create_space(display)
                for window in space.windows:
                    self.yabai.move_window_to_space(window, space.index)

    def register_handler(self, handler: WindowHandler):
        if handler.name in self.handlers:
            logging.warn("Replacing previously registered handler for %s", handler.name)
        self.handlers[handler.name] = handler

    def will_restore(self, win: Window) -> None:
        if not win.yws_data:
            return
        for name, handler in self.handlers.items():
            handler.will_restore(win.yws_data[name])

    def will_save(self, win: Window) -> None:
        for name, handler in self.handlers.items():
            if data := handler.will_save(win):
                if not win.yws_data:
                    win.yws_data = {}
                win.yws_data[name] = data
