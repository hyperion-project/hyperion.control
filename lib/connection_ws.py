from lib.utils import log
import websocket

class Connection:
    def __init__(self):
        # self.__url = "ws://192.168.0.11:19446"
        # self.__url = "ws://192.168.0.12:19444"
        self.__url = "ws://192.168.0.13:19444"
        self.__ip = "127.0.0.1"
        # self.__port = "19446"
        self.__port = "19444"
        self.__connected = False
        self.__ws = websocket.WebSocketApp(url=self.__url , on_message = self.on_message, on_error = self.on_error, on_close = self.on_close, on_open = self.on_open)
        self.__ws.run_forever()

    def __del__(self):
        self.__ws.shutdown()
        del self.__ws

    def on_message(self, message):
        log(message)

    def on_error(self, error):
        log(error)

    def on_close(self):
        self.__connected = False
        log("### closed ###")

    def on_open(ws):
        self.__connected = True
        log("CONNECTION OPEN")

    def updateURL(self, ip, port):
        if self.__ip != ip or self.__port != port:
            log("updateURL required:"+str(ip))
            self.__url = "ws://"+ip+":"+str(port)

            del self.__ws
            self.connect()

    def send(self, data):
        if self.__connected:

            log("send DATA:"+data)
            self.__ws.send(data)

    def sendComponentState(self, comp, state):
        log("sendComponentState:"+comp+str(state))
        data = '{"command":"componentstate", "componentstate":{"component": "'+comp+'", "state": "'+str(state).lower()+'" }, "tan":1}'
        self.send(data)

    def sendVideoMode(self, mode):
        data = '{"command":"videoMode", "videoMode":"'+mode+'", "tan":1}'
        self.send(data)
