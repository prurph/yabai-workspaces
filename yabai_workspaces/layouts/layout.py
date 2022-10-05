import logging
from abc import ABC, abstractmethod
from enum import Enum
from itertools import pairwise, zip_longest
from typing import List

from pydantic import BaseModel, PositiveInt

from ..models import Space
from ..types import NonEmptyStr
from ..utils import partition
from ..yabai import DirSel, Yabai


class LayoutName(str, Enum):
    managed = "managed"
    noop = "noop"
    columns = "columns"
    stack_beside_rows = "stack_beside_rows"


class Layout(BaseModel, ABC):
    layout: LayoutName
    yabai: Yabai

    class Config:
        arbitrary_types_allowed = True
        use_enum_values = True

    @abstractmethod
    def apply(self, space: Space) -> None:
        pass


class Columns(Layout):
    layout = LayoutName.columns
    col_count: PositiveInt

    def apply(self, space: Space) -> None:
        self.yabai.call(
            ["-m", "config", "--space", str(space.index), "split_type", "vertical"]
        )
        # TODO: this unstacks stuff. Maybe we shouldn't do this? Maybe have a ColumnsStacks
        # layout?
        self.yabai.call(["-m", "config", "--space", str(space.index), "layout", "bsp"])

        rows = list(zip_longest(*[iter(space.windows)] * self.col_count))

        for west, east in pairwise(rows[0]):
            if not east:
                continue
            self.yabai.set_insert_dir(west, DirSel.EAST)
            self.yabai.warp_window(east, west)
        for r1, r2 in pairwise(rows):
            for north, south in zip(r1, r2):
                if not south:
                    continue
                self.yabai.set_insert_dir(north, DirSel.SOUTH)
                self.yabai.warp_window(south, north)

        self.yabai.balance(space.index)


class StackBesideRows(Layout):
    layout = LayoutName.stack_beside_rows
    app_stack_priority: List[NonEmptyStr]
    secondary_row_count: PositiveInt

    def apply(self, space: Space) -> None:
        self.yabai.call(["-m", "config", "--space", str(space.index), "layout", "bsp"])

        windows = [w for w in self.yabai.windows() if w.id in space.windows]
        other_ws, main_ws = partition(
            lambda x: x.app in self.app_stack_priority, windows
        )

        if not main_ws:
            logging.warn("No matching windows for stack")
            main_ws, *other_ws = other_ws
            main_ws = [main_ws]

        main_ws.sort(key=lambda x: self.app_stack_priority.index(x.app))
        main_ws, other_ws = ([w.id for w in ws] for ws in (main_ws, other_ws))

        self.yabai.stack_windows(main_ws)
        self.yabai.call(["-m", "window", str(main_ws[-1]), "--swap", "first"])

        if not other_ws:
            return
        self.yabai.set_insert_dir(main_ws[-1], DirSel.EAST)

        rows, overflow = (
            other_ws[0 : self.secondary_row_count],
            other_ws[self.secondary_row_count :],
        )
        if rows:
            self.yabai.warp_window(rows[0], main_ws[-1])
        for north, south in pairwise(rows):
            self.yabai.set_insert_dir(north, DirSel.SOUTH)
            self.yabai.warp_window(south, north)
        self.yabai.stack_windows([w for w in (rows[-1], *overflow)])

        self.yabai.balance(space.index)


class ManagedLayout(Layout):
    layout = LayoutName.managed

    def apply(self, space: Space) -> None:
        for layout in ("float", "bsp"):
            self.yabai.call(
                ["-m", "config", "--space", str(space.index), "layout", layout]
            )


class NoopLayout(Layout):
    layout = LayoutName.noop

    def apply(self, space: Space) -> None:
        pass
