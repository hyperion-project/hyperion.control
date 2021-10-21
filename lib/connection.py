from lib.utils import log, bytesDecodeUtf8
from lib.gui import notifyUser
import httplib2
import simplejson as json

class Connection:
    def __init__(self):
        self.__http = httplib2.Http()
        self.__headers = {'Content-type': 'application/json'}
        self.__url = "http://127.0.0.1:8090/json-rpc"

    def __del__(self):
        del self.__http

    def updateHeader(self, authToken):
        if authToken == "" and not self.__headers.key('Authorization'):
            self.__headers.pop('Authorization')
        elif not self.__headers.key('Authorization'):
            self.__headers = self.__headers.update({'Authorization' : 'token '+authToken})

    def updateURL(self, ip, port):
        self.__url = "http://"+ip+":"+str(port)+"/json-rpc"

    def send(self, body):
        log("Send to: "+self.__url+" payload: "+body)
        try:
            response, content = self.__http.request(self.__url, 'POST', headers=self.__headers, body=body)
            jsonContent = json.loads(bytesDecodeUtf8(content))
            if not jsonContent["success"]:
                if jsonContent["error"] == "No Authorization":
                    notifyUser("Error: No Authorization, API Token required")
                log("Error: "+jsonContent["error"])
        except:
            pass

    def sendComponentState(self, comp, state):
        body = '{"command":"componentstate", "componentstate":{"component": "'+comp+'", "state": '+str(state).lower()+' }, "tan":1}'
        self.send(body)

    def sendVideoMode(self, mode):
        body = '{"command":"videoMode", "videoMode":"'+mode+'", "tan":1}'
        self.send(body)
