from fastapi import FastAPI
import json

from typing import Callable, Type

from ..models import NoLayout, Workspace, WorkspaceDisplay, WorkspaceSpace
from ..yabai import Yabai
from .yabai_events import (
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
    YabaiSignal,
)

app = FastAPI()
yabai = Yabai()

signal_handlers: dict[Type[YabaiSignal], list[Callable[..., None]]] = {
    k: []
    for k in (
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
    )
}


@app.on_event("startup")
async def initialize_signals() -> None:
    for s in signal_handlers.keys():
        # JSON POST data (-d) will be in single-quotes, but we need to interpolate the
        # env variable values provided by yabai at call time, so we need:
        #
        # -d '{"yabai_display_id": "'$YABAI_DISPLAY_ID'"}'
        #
        # the single quotes around $YABAI_DISPLAY_ID close the outer single quotes,
        # causing the shell to substitute in the env variable. json.dumps automatically
        # escapes the double quotes so they become part of the generated JSON body.
        params = {
            name: field.default if name == "event_name" else f"'${name.upper()}'"
            for name, field in s.__fields__.items()
        }
        action = f"/usr/bin/curl -s -X POST -H 'Content-Type: application/json' -d '{json.dumps(params)}' localhost:8000/signal"
        yabai.register_signal(
            params["event_name"],
            action,
            f"yabai-spaces-server-py-{params['event_name']}",
        )


@app.on_event("shutdown")
def clear_signals() -> None:
    for s in signal_handlers.keys():
        yabai.remove_signal(
            f"yabai-spaces-server-py-{s.__fields__['event_name'].default}"
        )


@app.get("/workspace", response_model=Workspace)
async def workspace() -> Workspace:
    return Workspace(
        displays=[
            WorkspaceDisplay(**(d.dict()), layout=NoLayout()) for d in yabai.displays()
        ],
        spaces=[
            WorkspaceSpace(**(s.dict()), layout=NoLayout()) for s in yabai.spaces()
        ],
        windows=yabai.windows(),
    )


@app.post("/signal")
async def signal(signal: YabaiSignal):
    print(f"Received signal {signal.event_name}: {signal}")
