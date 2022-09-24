from __future__ import annotations

from .models import Display, Space, Window

from enum import Enum
from typing import List
import json
import subprocess
import logging


class DirSel(str, Enum):
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"


class Yabai:
    def __init__(self, env: dict[str, str]):
        self.env = env
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

    def set_insert_dir(self, window: Window, direction: DirSel) -> None:
        self.call(["-m", "window", f"{window.id}", "--insert", direction.value])

    def stack_windows(self, windows: List[Window]) -> None:
        for w1, w2 in zip(windows[:-1], windows[1:]):
            self.call(["-m", "window", f"{w1.id}", "--stack", f"{w2.id}"])
