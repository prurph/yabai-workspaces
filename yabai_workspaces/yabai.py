from __future__ import annotations

from .models import Display, Space, Window, Workspace

from enum import Enum
from typing import List
import json
import subprocess
import logging
import os

ENV = {**os.environ, "PATH": "/opt/homebrew/bin:"}


class DirSel(str, Enum):
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"


class Yabai:
    def __init__(self, env: dict[str, str] = ENV):
        self.env = env.copy()
        try:
            subprocess.check_call(
                ["yabai", "--version"],
                env=self.env,
                stderr=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError as e:
            logging.error(f"Error locatinng yabai: {e.stderr}")
            raise RuntimeError from e

    def call(self, cmd: List[str]):
        subprocess.call(["yabai", *cmd], env=self.env)

    # TODO: opts to minimize vs close
    def clean_slate(self):
        for s in self.spaces():
            if len(s.label) > 0:
                self.call(["-m", "space", f"{s.index}", "--label"])
            self.call(["-m", "space", f"{s.index}", "--destroy"])
        self.call(["-m", "display", "--focus", "1"])

    def balance(self, space_idx: int) -> None:
        self.call(["-m", "space", str(space_idx), "--balance"])

    def get_workspace(self) -> Workspace:
        return Workspace(
            displays=self.displays(), spaces=self.spaces(), windows=self.windows()
        )

    def displays(self) -> List[Display]:
        return [
            Display.parse_obj(d) for d in self.output(["-m", "query", "--displays"])
        ]

    def spaces(self) -> List[Space]:
        return [Space.parse_obj(s) for s in self.output(["-m", "query", "--spaces"])]

    def windows(self) -> List[Window]:
        return [Window.parse_obj(w) for w in self.output(["-m", "query", "--windows"])]

    def output(self, cmd: List[str]):
        return json.loads(subprocess.check_output(["yabai", *cmd], env=self.env))

    def create_space(self, display_idx: int | None = None):
        if display_idx is not None:
            self.call(["-m", "display", "--focus", str(display_idx)])
        self.call(["-m", "space", "--create"])

    def move_space_to_display(self, space_idx: int, display_idx: int):
        self.call(["-m", "space", str(space_idx), "--display", str(display_idx)])

    def move_window_to_space(self, window_id: int, space_idx: int):
        self.call(["-m", "window", str(window_id), "--space", str(space_idx)])

    def set_insert_dir(self, window_id: int, direction: DirSel) -> None:
        self.call(["-m", "window", str(window_id), "--insert", direction.value])

    def stack_windows(self, window_ids: List[int]) -> None:
        for w1, w2 in zip(window_ids[:-1], window_ids[1:]):
            self.call(["-m", "window", str(w1), "--stack", str(w2)])

    def warp_window(self, warp: int, onto: int) -> None:
        self.call(["-m", "window", str(warp), "--warp", str(onto)])
