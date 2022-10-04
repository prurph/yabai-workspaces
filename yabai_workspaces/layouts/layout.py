from abc import ABC, abstractmethod
from enum import Enum
from itertools import pairwise, zip_longest

from pydantic import BaseModel, Field

from ..models import Space
from ..types import DecimalPercent
from ..yabai import DirSel, Yabai


class LayoutName(str, Enum):
    managed = "managed"
    noop = "noop"
    columns = "columns"
    main_stack = "main_stack"


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
    col_count: int = Field(..., gt=1)

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


class MainStack(Layout):
    layout = LayoutName.main_stack
    width: DecimalPercent

    def apply(self, space: Space) -> None:
        pass


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
