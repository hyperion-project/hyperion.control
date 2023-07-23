import contextlib
import random
import string
from typing import Any

import requests
import json

from resources.lib.gui import GuiHandler
from resources.lib.logger import Logger
from resources.lib.settings_manager import SettingsManager


class ApiClient:
    def __init__(self, logger: Logger, gui: GuiHandler, settings: SettingsManager) -> None:
        self._settings = settings
        self._logger = logger
        self._gui = gui

    @property
    def headers(self) -> dict[str, str]:
        headers = {'Content-type': 'application/json'}
        if self._settings.auth_token:
            headers['Authorization'] = f'token {self._settings.auth_token}'
        return headers

    def _send(self, body: dict[str, Any]) -> dict[str, Any]:
        url = self._settings.base_url
        logger = self._logger
        logger.log(f"Send to: {url} payload: {body}")
        with contextlib.suppress(Exception):
            response, content = requests.post(
                url, json.dumps(body), headers=self.headers
            )
            json_content = json.loads(content)
            if json_content["success"]:
                return json_content
            if json_content["error"] == "No Authorization":
                self._gui.notify_text("Error: No Authorization, API Token required")
                logger.error(json_content["error"])

    def needs_auth(self) -> bool:
        if res := self._send({"command": "authorize", "subcommand": "tokenRequired"}):
            return res["info"]["required"]

    def get_token(self) -> str:
        pool = string.ascii_uppercase + string.ascii_lowercase + string.digits
        control_code = ''.join(random.choice(pool) for _ in range(16))
        message = {
            "command": "authorize",
            "subcommand": "requestToken",
            "comment": "Kodi Hyperion Control",
            "id": control_code
        }
        # TODO: set timeout to 180 seconds
        if res := self._send(message):
            return res["info"]["token"]


    def send_component_state(self, component: str, state: bool) -> None:
        body = {
            "command": "componentstate",
            "componentstate": {"component": component, "state": state},
        }
        self._send(body)

    def send_video_mode(self, mode: str) -> None:
        self._send({"command": "videoMode", "videoMode": mode})
