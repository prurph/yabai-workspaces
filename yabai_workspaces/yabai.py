from __future__ import annotations

import json
import socket
import struct
from enum import Enum
from pathlib import Path
from typing import List

from .models import Display, Space, Window, Workspace


class DirSel(str, Enum):
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"


class Yabai:
    def __init__(self):
        try:
            self.socket, *_ = map(str, Path("/tmp").glob("yabai_*.socket"))
        except ValueError as e:
            raise RuntimeError(
                f"No yabai socket found in /tmp. Is yabai running?"
            ) from e

    def call(self, cmd: List[str]):
        return self.using_socket(cmd)

    # TODO: opts to minimize vs close
    def clean_slate(self):
        for s in self.spaces():
            if len(s.label) > 0:
                self.call(["space", f"{s.index}", "--label"])
            self.call(["space", f"{s.index}", "--destroy"])
        self.call(["display", "--focus", "1"])

    def balance(self, space_idx: int) -> None:
        self.call(["space", str(space_idx), "--balance"])

    def displays(self) -> List[Display]:
        return [Display.parse_obj(d) for d in self.call(["query", "--displays"])]

    def spaces(self) -> List[Space]:
        return [Space.parse_obj(s) for s in self.call(["query", "--spaces"])]

    def windows(self) -> List[Window]:
        return [Window.parse_obj(w) for w in self.call(["query", "--windows"])]

    def create_space(self, display_idx: int | None = None):
        if display_idx is not None:
            self.call(["display", "--focus", str(display_idx)])
        self.call(["space", "--create"])

    def move_space_to_display(self, space_idx: int, display_idx: int):
        self.call(["space", str(space_idx), "--display", str(display_idx)])

    def move_window_to_space(self, window_id: int, space_idx: int):
        self.call(["window", str(window_id), "--space", str(space_idx)])

    def set_insert_dir(self, window_id: int, direction: DirSel) -> None:
        self.call(["window", str(window_id), "--insert", direction.value])

    def stack_windows(self, window_ids: List[int]) -> None:
        for w1, w2 in zip(window_ids[:-1], window_ids[1:]):
            self.call(["window", str(w1), "--stack", str(w2)])

    def warp_window(self, warp: int, onto: int) -> None:
        self.call(["window", str(warp), "--warp", str(onto)])

    def using_socket(self, command: List[str], ignore_error: bool = True):
        # Yabai message format: https://github.com/koekeishiya/yabai/issues/1372
        # A byte array where the first 4 bytes are the length of the message
        # that follows in big endian, then the message is sent with a NUL byte
        # between terms, and two trailing NUL bytes.
        command_bytes = ("\0".join(command) + "\0\0").encode()
        sock_msg = struct.pack("<I", len(command_bytes)) + command_bytes

        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.connect(self.socket)
            sock.send(sock_msg)
            sock.shutdown(socket.SHUT_WR)

            resp: List[str] = []
            while len(recv := str(sock.recv(4096), "utf-8")) > 0:
                resp.append(recv)

        if not resp:
            return
        try:
            return json.loads("".join(resp))
        except json.JSONDecodeError as e:
            if not ignore_error:
                raise RuntimeError(f"Yabai command {command} failed: {resp}") from e
            pass
