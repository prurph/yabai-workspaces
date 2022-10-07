import logging
from itertools import pairwise, zip_longest

from ..models import (
    ColumnsLayout,
    Layout,
    NoLayout,
    Space,
    StackBesideRowsLayout,
    YabaiManagedLayout,
)
from ..utils import partition
from ..yabai import DirSel, Yabai


class LayoutHandler:
    def __init__(self, yabai: Yabai):
        self.yabai = yabai

    def apply(self, layout: Layout, space: Space):
        # TODO: is this better style or is functools.singledispatch?
        match layout:
            case ColumnsLayout():
                self._apply_columns(layout, space)
            case NoLayout():
                pass
            case StackBesideRowsLayout():
                self._apply_stack_beside_rows(layout, space)
            case YabaiManagedLayout():
                self._apply_yabai_managed(layout, space)

    def _apply_columns(self, layout: ColumnsLayout, space: Space):
        self.yabai.call(
            ["-m", "config", "--space", str(space.index), "split_type", "vertical"]
        )
        # TODO: this unstacks stuff. Maybe we shouldn't do this? Maybe have a ColumnsStacks
        # layout?
        self.yabai.call(["-m", "config", "--space", str(space.index), "layout", "bsp"])

        rows = list(zip_longest(*[iter(space.windows)] * layout.col_count))

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

    def _apply_stack_beside_rows(self, layout: StackBesideRowsLayout, space: Space):
        self.yabai.call(["-m", "config", "--space", str(space.index), "layout", "bsp"])

        windows = [w for w in self.yabai.windows() if w.id in space.windows]
        other_ws, main_ws = partition(
            lambda x: x.app in layout.app_stack_priority, windows
        )

        if not main_ws:
            logging.warn("No matching windows for stack")
            main_ws, *other_ws = other_ws
            main_ws = [main_ws]

        main_ws.sort(key=lambda x: layout.app_stack_priority.index(x.app))
        main_ws, other_ws = ([w.id for w in ws] for ws in (main_ws, other_ws))

        self.yabai.stack_windows(main_ws)
        self.yabai.call(["-m", "window", str(main_ws[-1]), "--swap", "first"])

        if not other_ws:
            return
        self.yabai.set_insert_dir(main_ws[-1], DirSel.EAST)

        rows, overflow = (
            other_ws[0 : layout.secondary_row_count],
            other_ws[layout.secondary_row_count :],
        )
        if rows:
            self.yabai.warp_window(rows[0], main_ws[-1])
        for north, south in pairwise(rows):
            self.yabai.set_insert_dir(north, DirSel.SOUTH)
            self.yabai.warp_window(south, north)
        self.yabai.stack_windows([w for w in (rows[-1], *overflow)])

        self.yabai.balance(space.index)

    def _apply_yabai_managed(self, layout: YabaiManagedLayout, space: Space):
        for l in ("float", "bsp"):
            self.yabai.call(["-m", "config", "--space", str(space.index), "layout", l])
