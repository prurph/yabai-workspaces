from pydantic import BaseModel, PositiveInt, Field

from typing import Annotated, Literal, Union


class ApplicationActivated(BaseModel):
    event_name: Literal["application_activated"] = "application_activated"
    yabai_process_id: PositiveInt


class ApplicationDeactivated(BaseModel):
    event_name: Literal["application_deactivated"] = "application_deactivated"
    yabai_process_id: PositiveInt


class ApplicationFrontSwitched(BaseModel):
    event_name: Literal["application_front_switched"] = "application_front_switched"
    yabai_process_id: PositiveInt
    yabai_recent_process_id: PositiveInt


class ApplicationHidden(BaseModel):
    event_name: Literal["application_hidden"] = "application_hidden"
    yabai_process_id: PositiveInt


class ApplicationLaunched(BaseModel):
    event_name: Literal["application_launched"] = "application_launched"
    yabai_process_id: PositiveInt


class ApplicationTerminated(BaseModel):
    event_name: Literal["application_terminated"] = "application_terminated"
    yabai_process_id: PositiveInt


class ApplicationVisible(BaseModel):
    event_name: Literal["application_visible"] = "application_visible"
    yabai_process_id: PositiveInt


class DisplayAdded(BaseModel):
    event_name: Literal["display_added"] = "display_added"
    yabai_display_id: PositiveInt


class DisplayChanged(BaseModel):
    event_name: Literal["display_changed"] = "display_changed"
    yabai_display_id: PositiveInt
    yabai_recent_display_id: PositiveInt


class DisplayMoved(BaseModel):
    event_name: Literal["display_moved"] = "display_moved"
    yabai_display_id: PositiveInt


class DisplayRemoved(BaseModel):
    event_name: Literal["display_removed"] = "display_removed"
    yabai_display_id: PositiveInt


class DisplayResized(BaseModel):
    event_name: Literal["display_resized"] = "display_resized"
    yabai_display_id: PositiveInt


class SpaceChanged(BaseModel):
    event_name: Literal["space_changed"] = "space_changed"
    yabai_space_id: PositiveInt
    yabai_recent_space_id: PositiveInt


class WindowCreated(BaseModel):
    event_name: Literal["window_created"] = "window_created"
    yabai_window_id: PositiveInt


class WindowDeminimized(BaseModel):
    event_name: Literal["window_deminimized"] = "window_deminimized"
    yabai_window_id: PositiveInt


class WindowDestroyed(BaseModel):
    event_name: Literal["window_destroyed"] = "window_destroyed"
    yabai_window_id: PositiveInt


class WindowFocused(BaseModel):
    event_name: Literal["window_focused"] = "window_focused"
    yabai_window_id: PositiveInt


class WindowMinimized(BaseModel):
    event_name: Literal["window_minimized"] = "window_minimized"
    yabai_window_id: PositiveInt


class WindowMoved(BaseModel):
    event_name: Literal["window_moved"] = "window_moved"
    yabai_window_id: PositiveInt


class WindowResized(BaseModel):
    event_name: Literal["window_resized"] = "window_resized"
    yabai_window_id: PositiveInt


class WindowTitleChanged(BaseModel):
    event_name: Literal["window_title_changed"] = "window_title_changed"
    yabai_window_id: PositiveInt


# I wanted to make this a base class with ClassVar as an abstract property
# because then you can reference it directly from the class instead of
# needing to do klass.__fields__["event_name"].default. However I couldn't
# figure out how do to that _and_ let that field be the discriminator for
# the tagged union. Maybe it is possible with two separate fields, one
# ClassVar and then the actual pydantic Field that uses that ClassVar for
# its default value.
YabaiSignal = Annotated[
    Union[
        ApplicationActivated,
        ApplicationDeactivated,
        ApplicationFrontSwitched,
        ApplicationHidden,
        ApplicationLaunched,
        ApplicationTerminated,
        ApplicationVisible,
        DisplayAdded,
        DisplayChanged,
        DisplayMoved,
        DisplayRemoved,
        DisplayResized,
        SpaceChanged,
        WindowCreated,
        WindowDeminimized,
        WindowDestroyed,
        WindowFocused,
        WindowMinimized,
        WindowMoved,
        WindowResized,
        WindowTitleChanged,
    ],
    Field(discriminator="event_name"),
]
