from abc import ABC, abstractmethod
from enum import Enum
from pydantic import BaseModel

from ..models import Space
from ..yabai import Yabai


class LayoutName(str, Enum):
    managed = "managed"
    noop = "noop"


class Layout(BaseModel, ABC):
    layout: LayoutName
    yabai: Yabai

    class Config:
        arbitrary_types_allowed = True
        use_enum_values = True

    @abstractmethod
    def apply(self, space: Space) -> None:
        pass


class NoopLayout(Layout):
    layout = LayoutName.noop

    def apply(self, space: Space) -> None:
        pass


class ManagedLayout(Layout):
    layout = LayoutName.managed

    def apply(self, space: Space) -> None:
        for layout in ("float", "bsp"):
            self.yabai.call(
                ["-m", "config", "--space", str(space.index), "layout", layout]
            )
