from __future__ import annotations

from enum import Enum
from typing import Any, List

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
        allow_population_by_field_name = True
        use_enum_values = True


class Window(BaseModel):
    id: PositiveInt
    pid: PositiveInt
    app: str
    title: str
    frame: Frame
    role: str
    subrole: str
    tags: str
    display: PositiveInt
    space: PositiveInt
    level: NonNegativeInt
    opacity: DecimalPercent
    split_type: SplitType = Field(..., alias="split-type")
    stack_index: NonNegativeInt = Field(..., alias="stack-index")
    can_move: bool = Field(..., alias="can-move")
    can_resize: bool = Field(..., alias="can-resize")
    has_focus: bool = Field(..., alias="has-focus")
    has_shadow: bool = Field(..., alias="has-shadow")
    has_border: bool = Field(..., alias="has-border")
    has_parent_zoom: bool = Field(..., alias="has-parent-zoom")
    has_fullscreen_zoom: bool = Field(..., alias="has-fullscreen-zoom")
    is_native_fullscreen: bool = Field(..., alias="is-native-fullscreen")
    is_visible: bool = Field(..., alias="is-visible")
    is_minimized: bool = Field(..., alias="is-minimized")
    is_hidden: bool = Field(..., alias="is-hidden")
    is_floating: bool = Field(..., alias="is-floating")
    is_sticky: bool = Field(..., alias="is-sticky")
    is_topmost: bool = Field(..., alias="is-topmost")
    is_grabbed: bool = Field(..., alias="is-grabbed")
    yws_data: dict[str, Any] | None = None

    class Config:
        allow_population_by_field_name = True


class WorkspaceMeta(BaseModel):
    name: NonEmptyStr
    description: NonEmptyStr | None = None


class Workspace(BaseModel):
    meta: WorkspaceMeta | None = None
    displays: List[Display]
    spaces: List[Space]
    windows: List[Window]
