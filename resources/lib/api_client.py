"""Hyperion JSON RPC/HTTP(S) API client."""
from __future__ import annotations

import contextlib
import json
import random
import string
from typing import Any

import requests

from resources.lib.interfaces import GuiHandler
from resources.lib.interfaces import Logger
from resources.lib.interfaces import SettingsManager


class ApiClient:
    """Manages the request to the hyperion server."""

    def __init__(
        self, logger: Logger, gui: GuiHandler, settings: SettingsManager
    ) -> None:
        self._settings = settings
        self._logger = logger
        self._gui = gui

    @property
    def headers(self) -> dict[str, str]:
        """Request headers."""
        headers = {"Content-type": "application/json"}
        if self._settings.auth_token:
            headers["Authorization"] = f"token {self._settings.auth_token}"
        return headers

    def _send(self, body: dict[str, Any]) -> dict[str, Any] | None:
        url = self._settings.base_url
        logger = self._logger
        logger.log(f"Send to: {url} payload: {body}")
        with contextlib.suppress(Exception):
            response, content = requests.post(  # noqa: S113
                url, json.dumps(body), headers=self.headers
            )
            json_content = json.loads(content)
            if json_content["success"]:
                return json_content
            if json_content["error"] == "No Authorization":
                self._gui.notify_text("Error: No Authorization, API Token required")
                logger.error(json_content["error"])
        return None

    def needs_auth(self) -> bool:
        """Whether the hyperion server needs API authentication."""
        if res := self._send({"command": "authorize", "subcommand": "tokenRequired"}):
            return res["info"]["required"]
        return False

    def get_token(self) -> str:
        """Requests the authentication token."""
        pool = string.ascii_uppercase + string.ascii_lowercase + string.digits
        control_code = "".join(random.choice(pool) for _ in range(16))
        message = {
            "command": "authorize",
            "subcommand": "requestToken",
            "comment": "Kodi Hyperion Control",
            "id": control_code,
        }
        # TODO: set timeout to 180 seconds
        return res["info"]["token"] if (res := self._send(message)) else ""

    def send_component_state(self, component: str, state: bool) -> None:
        """Sends the component state."""
        body = {
            "command": "componentstate",
            "componentstate": {"component": component, "state": state},
        }
        self._send(body)

    def send_video_mode(self, mode: str) -> None:
        """Sends the current video mode."""
        self._send({"command": "videoMode", "videoMode": mode})
