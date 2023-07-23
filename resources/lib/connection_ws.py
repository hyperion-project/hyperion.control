import json

from resources.lib.logger import Logger
import websocket


class Connection:
    def __init__(self, logger: Logger) -> None:
        # self._url = "ws://192.168.0.11:19446"
        # self._url = "ws://192.168.0.12:19444"
        self._logger = logger
        self._url = "ws://192.168.0.13:19444"
        self._ip = "127.0.0.1"
        # self._port = "19446"
        self._port = "19444"
        self._connected = False
        self._ws: websocket.WebSocketApp | None = None
        self.connect()

    def connect(self) -> None:
        self._ws = websocket.WebSocketApp(
            url=self._url,
            on_message = self.on_message,
            on_error = self.on_error,
            on_close = self.on_close,
            on_open = self.on_open,
        )
        self._ws.run_forever()

    def __del__(self):
        if self._ws:
            self._ws.shutdown()

    def on_message(self, message):
        self._logger.log(message)

    def on_error(self, error):
        self._logger.error(error)

    def on_close(self):
        self._connected = False
        self._logger.log("### closed ###")

    def on_open(self):
        self._connected = True
        self._logger.log("CONNECTION OPEN")

    def update_url(self, ip, port):
        if self._ip != ip or self._port != port:
            self._logger.log(f"updateURL required:{str(ip)}")
            self._url = f"ws://{ip}:{str(port)}"
            self._ip = ip
            self._port = port

            del self._ws
            self.connect()

    def _send(self, data):
        if self._connected:
            self._logger.log(f"send DATA:{data}")
            self._ws.send(json.dumps(data))

    def send_component_state(self, comp, state):
        self._logger.log(f"sendComponentState:{comp}{str(state)}")
        data = {
            "command":"componentstate",
            "componentstate": {"component": comp, "state": str(state).lower()},
            "tan": 1,
        }
        self._send(data)

    def send_video_mode(self, mode):
        data = {"command": "videoMode", "videoMode": mode, "tan":1}
        self._send(data)
