from fastapi import FastAPI

from ..models import NoLayout, Workspace, WorkspaceDisplay, WorkspaceSpace
from ..yabai import Yabai

app = FastAPI()

yabai = Yabai()


@app.get("/", response_model=Workspace)
async def root() -> Workspace:
    return Workspace(
        displays=[
            WorkspaceDisplay(**(d.dict()), layout=NoLayout()) for d in yabai.displays()
        ],
        spaces=[
            WorkspaceSpace(**(s.dict()), layout=NoLayout()) for s in yabai.spaces()
        ],
        windows=yabai.windows(),
    )
