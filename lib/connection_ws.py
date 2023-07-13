from lib.utils import log
import websocket

class Connection:
    def __init__(self):
        # self._url = "ws://192.168.0.11:19446"
        # self._url = "ws://192.168.0.12:19444"
        self._url = "ws://192.168.0.13:19444"
        self._ip = "127.0.0.1"
        # self._port = "19446"
        self._port = "19444"
        self._connected = False
        self._ws = websocket.WebSocketApp(url=self._url, on_message = self.on_message, on_error = self.on_error, on_close = self.on_close, on_open = self.on_open)
        self._ws.run_forever()

    def __del__(self):
        self._ws.shutdown()
        del self._ws

    def on_message(self, message):
        log(message)

    def on_error(self, error):
        log(error)

    def on_close(self):
        self._connected = False
        log("### closed ###")

    def on_open(ws):
        self._connected = True
        log("CONNECTION OPEN")

    def updateURL(self, ip, port):
        if self._ip != ip or self._port != port:
            log(f"updateURL required:{str(ip)}")
            self._url = f"ws://{ip}:{str(port)}"

            del self._ws
            self.connect()

    def send(self, data):
        if self._connected:

            log(f"send DATA:{data}")
            self._ws.send(data)

    def sendComponentState(self, comp, state):
        log(f"sendComponentState:{comp}{str(state)}")
        data = f'{{"command":"componentstate", "componentstate":{{"component": "{comp}", "state": "{str(state).lower()}" }}, "tan":1}}'
        self.send(data)

    def sendVideoMode(self, mode):
        data = f'{{"command":"videoMode", "videoMode":"{mode}' + '", "tan":1}}'
        self.send(data)
