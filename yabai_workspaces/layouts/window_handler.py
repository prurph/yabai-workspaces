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

    def capture_tabs(self, win: Window):
        # Yabai sees Window titles as <Title> — Google Chrome — <Profile|(Incognito)>
        # but Chrome reports them without the app and profile.
        win_title = re.sub(r" - Google Chrome.+$", "", win.title)
        jxa = f"""\
            JSON.stringify(Application("Google Chrome")
                .windows()
                .find(w => w.title() === "{win_title}")
                .tabs()
                .map(t => ({{title: t.title(), url: t.url()}})));
        """
        return json.loads(
            subprocess.check_output(
                ["osascript", "-l", "JavaScript", "-e", jxa],
                env=self.env,
            )
        )
