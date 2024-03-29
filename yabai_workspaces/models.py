from __future__ import annotations

from enum import Enum
from typing import Any, Literal, Union

from pydantic import BaseModel, Field, NonNegativeInt, PositiveInt

from .types import DecimalPercent, NonEmptyStr


class SpaceType(str, Enum):
    bsp = "bsp"
    float = "float"
    stack = "stack"


class SplitType(str, Enum):
    auto = "auto"
    horizontal = "horizontal"
    none = "none"
    vertical = "vertical"


class Frame(BaseModel):
    x: float
    y: float
    w: float
    h: float


class ColumnsLayout(BaseModel):
    layout_type: Literal["columns"] = "columns"
    col_count: PositiveInt


class NoLayout(BaseModel):
    layout_type: Literal["no_layout"] = "no_layout"


class StackBesideRowsLayout(BaseModel):
    layout_type: Literal["stack_beside_rows"] = "stack_beside_rows"
    app_stack_priority: list[NonEmptyStr]
    secondary_row_count: PositiveInt


class YabaiManagedLayout(BaseModel):
    layout_type: Literal["yabai_managed"] = "yabai_managed"


Layout = Union[ColumnsLayout, NoLayout, StackBesideRowsLayout, YabaiManagedLayout]


class Display(BaseModel):
    id: PositiveInt
    # Yabai UUIDs don't always seem to match a defined spec, so just use str
    uuid: str
    index: PositiveInt
    frame: Frame
    spaces: set[PositiveInt]


class Space(BaseModel):
    id: PositiveInt
    # Yabai UUIDs don't always seem to match a defined spec, so just use str
    uuid: str
    index: PositiveInt
    label: str
    type: SpaceType
    display: PositiveInt
    windows: set[PositiveInt]
    first_window: NonNegativeInt = Field(..., alias="first-window")  # 0 if no windows
    last_window: NonNegativeInt = Field(..., alias="last-window")  # 0 if no windows
    has_focus: bool = Field(..., alias="has-focus")
    is_visible: bool = Field(..., alias="is-visible")
    is_native_fullscreen: bool = Field(..., alias="is-native-fullscreen")

    class Config:
        populate_by_name = True
        use_enum_values = True


class Window(BaseModel):
    id: PositiveInt
    pid: PositiveInt
    app: str
    title: str
    frame: Frame
    role: str
    subrole: str
    display: PositiveInt
    space: PositiveInt
    level: int
    layer: Literal["normal", "below", "above"]
    opacity: DecimalPercent
    split_type: SplitType = Field(..., alias="split-type")
    stack_index: NonNegativeInt = Field(..., alias="stack-index")
    can_move: bool = Field(..., alias="can-move")
    can_resize: bool = Field(..., alias="can-resize")
    has_focus: bool = Field(..., alias="has-focus")
    has_shadow: bool = Field(..., alias="has-shadow")
    has_parent_zoom: bool = Field(..., alias="has-parent-zoom")
    has_fullscreen_zoom: bool = Field(..., alias="has-fullscreen-zoom")
    is_native_fullscreen: bool = Field(..., alias="is-native-fullscreen")
    is_visible: bool = Field(..., alias="is-visible")
    is_minimized: bool = Field(..., alias="is-minimized")
    is_hidden: bool = Field(..., alias="is-hidden")
    is_floating: bool = Field(..., alias="is-floating")
    is_sticky: bool = Field(..., alias="is-sticky")
    is_grabbed: bool = Field(..., alias="is-grabbed")
    yws_data: dict[str, Any] | None = None

    class Config:
        populate_by_name = True


class WorkspaceDisplay(Display):
    layout: Layout | None = None


class WorkspaceSpace(Space):
    layout: Layout | None = None


class Workspace(BaseModel):
    displays: list[WorkspaceDisplay]
    spaces: list[WorkspaceSpace]
    windows: list[Window]
