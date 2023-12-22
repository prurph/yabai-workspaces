import asyncio
import json
from contextlib import asynccontextmanager
from typing import Callable, Literal, Type

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

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

current_workspace = Workspace(displays=[], spaces=[], windows=[])


@asynccontextmanager
async def lifespan(app: FastAPI):
    await initialize_signals()
    yield
    await clear_signals()
    return


app = FastAPI(lifespan=lifespan)
yabai = Yabai()


async def refresh_workspace():
    global current_workspace
    current_workspace = Workspace(
        displays=[
            WorkspaceDisplay(**(d.model_dump()), layout=NoLayout())
            for d in await yabai.adisplays()
        ],
        spaces=[
            WorkspaceSpace(**(s.model_dump()), layout=NoLayout())
            for s in await yabai.aspaces()
        ],
        windows=await yabai.awindows(),
    )
    return current_workspace


async def initialize_signals() -> None:
    await refresh_workspace()
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
            for name, field in s.model_fields.items()
        }
        action = f"/usr/bin/curl -s -X POST -H 'Content-Type: application/json' -d '{json.dumps(params)}' localhost:8000/signal"
        await yabai.aregister_signal(
            params["event_name"],
            action,
            f"yabai-spaces-server-py-{params['event_name']}",
        )
    proc = await asyncio.create_subprocess_exec(
        *[
            "/usr/bin/osascript",
            "-e",
            'tell application id "tracesOf.Uebersicht" to refresh',
        ],
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    await proc.wait()


async def clear_signals() -> None:
    for s in signal_handlers.keys():
        await yabai.aremove_signal(
            f"yabai-spaces-server-py-{s.model_fields['event_name'].default}"
        )


@app.get("/workspace", response_model=Workspace)
async def workspace() -> Workspace:
    return await refresh_workspace()


class SpacesUpdated(BaseModel):
    type: Literal["SPACES_UPDATED"] = "SPACES_UPDATED"
    content: Workspace


# https://fastapi.tiangolo.com/advanced/websockets/#handling-disconnections-and-multiple-clients
class ConnectionManager:
    def __init__(self):
        self.clients: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.clients.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.clients.remove(websocket)

    async def broadcast(self, workspace: Workspace):
        for client in self.clients:
            await client.send_text(
                SpacesUpdated(content=workspace).model_dump_json(by_alias=True)
            )


manager = ConnectionManager()


@app.post("/signal")
async def signal(signal: YabaiSignal):
    await refresh_workspace()
    await manager.broadcast(current_workspace)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    print("Client connected")
    await websocket.send_text(
        SpacesUpdated(content=current_workspace).model_dump_json(by_alias=True)
    )
    try:
        while True:
            await asyncio.sleep(0)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
