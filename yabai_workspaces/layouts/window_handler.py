import json
import os
import re
import subprocess
from abc import ABC, abstractmethod
from typing import Any

from ..models import Window


class WindowHandler(ABC):
    name: str

    @abstractmethod
    def will_save(self, win: Window) -> dict[str, Any] | None:
        pass

    # TODO: is this right interface? Does handler just assume the
    # window is focused when called? Should it have access to Yabai
    # and be expected to focus the window it's returning?
    @abstractmethod
    def will_restore(self, saved: dict[str, Any]) -> None:
        pass


class ChromeHandler(WindowHandler):
    # TODO: don't set up shell stuff in multiple places
    def __init__(self):
        self.name = "ChromeHandler"
        self.env = {
            **os.environ,
            "PATH": f"/bin:/usr/bin:/usr/local/bin:/opt/homebrew/bin",
        }

    def will_save(self, win: Window) -> dict[str, Any] | None:
        if win.app != "Google Chrome":
            return None
        return {"tabs": self.capture_tabs(win)}

    def will_restore(self, saved: dict[str, Any]) -> None:
        # TODO: handle case where window already has open tabs. Need to first
        # determine what contract between handler and layout is regarding
        # reusing existing windows.
        open_commands = "\n".join([f'open location "{t}"' for t in saved["tabs"]])
        restore_tabs = f"""\
            tell application "Google Chrome"
                make new window
                activate
                {open_commands}
            end tell
        """
        subprocess.check_call(["osascript", "-e", restore_tabs], env=self.env)

    def capture_tabs(self, win: Window):
        # Window titles are <Title> — Google Chrome — <Profile|(Incognito)>
        # but Chrome reports them without the app and profile in osacript.
        win_title = re.sub(r" - Google Chrome.+$", "", win.title)
        fetch_tabs = f"""\
            JSON.stringify(Application("Google Chrome")
                .windows()
                .find(w => w.title() === "{win_title}")
                .tabs()
                .map(t => ({{title: t.title(), url: t.url()}})));
        """
        return json.loads(
            subprocess.check_output(
                ["osascript", "-l", "JavaScript", "-e", fetch_tabs],
                env=self.env,
            )
        )
