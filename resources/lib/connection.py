import contextlib
from resources.lib.utils import log, bytes_decode_utf8
from resources.lib.gui import notify_user
import httplib2
import simplejson as json

class Connection:
    def __init__(self):
        self.__http = httplib2.Http()
        self._headers = {'Content-type': 'application/json'}
        self.__url = "http://127.0.0.1:8090/json-rpc"

    def __del__(self):
        del self.__http

    def update_header(self, auth_token):
        if auth_token == "" and not self._headers.key('Authorization'):
            self._headers.pop('Authorization')
        elif 'Authorization' not in self._headers:
            self._headers = self._headers.update({'Authorization': f'token {auth_token}'})

    def update_url(self, ip, port):
        self.__url = f"http://{ip}:{str(port)}/json-rpc"

    def send(self, body):
        log(f"Send to: {self.__url} payload: {body}")
        with contextlib.suppress(Exception):
            response, content = self.__http.request(self.__url, 'POST', headers=self._headers, body=body)
            json_content = json.loads(bytes_decode_utf8(content))
            if not json_content["success"]:
                if json_content["error"] == "No Authorization":
                    notify_user("Error: No Authorization, API Token required")
                log("Error: "+json_content["error"])

    def send_component_state(self, comp, state):
        body = '{"command":"componentstate", "componentstate":{"component": "'+comp+'", "state": '+str(state).lower()+' }, "tan":1}'
        self.send(body)

    def send_video_mode(self, mode):
        body = '{"command":"videoMode", "videoMode":"'+mode+'", "tan":1}'
        self.send(body)
