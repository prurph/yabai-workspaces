from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import List

from ..models import Window, Workspace, WorkspaceMeta
from ..yabai import Yabai
from .window_handler import WindowHandler

ENV = {**os.environ, "PATH": "/opt/homebrew/bin:"}


class BaseLayout:
    def __init__(self, handlers: List[WindowHandler] = []):
        self.yabai = Yabai(ENV)
        self.handlers: dict[str, WindowHandler] = {}
        for handler in handlers:
            self.register_handler(handler)

    def read_current(self) -> Workspace:
        return Workspace(
            displays={d.index: d for d in self.yabai.displays()},
            spaces={s.index: s for s in self.yabai.spaces()},
            windows={w.id: w for w in self.yabai.windows()},
        )

    def save(self, name: str, description: str, path=Path) -> None:
        ws = self.read_current()
        ws.meta = WorkspaceMeta(name=name, description=description)
        for win in ws.windows.values():
            self.will_save(win)
        return path.write_text(ws.json(ensure_ascii=False, indent=2, sort_keys=True))

    def register_handler(self, handler: WindowHandler):
        if handler.name in self.handlers:
            logging.warn("Duplicate handler registered for name %s", handler.name)
        self.handlers[handler.name] = handler

    def will_save(self, win: Window) -> None:
        for name, handler in self.handlers.items():
            if data := handler.will_save(win):
                if not win.yabai_workspaces:
                    win.yabai_workspaces = {}
                win.yabai_workspaces[name] = data
