
#   Copyright 2014 Dan Krause
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# All credits to Dan Krause at Github: https://gist.github.com/dankrause/6000248
#

import http.client
import socket
from io import BytesIO


class _FakeSocket(BytesIO):
    def makefile(self, *args, **kw):
        return self

class SSDPResponse:

    def __init__(self, response):
        r = http.client.HTTPResponse(_FakeSocket(response))
        r.begin()
        self.location = r.getheader("location")
        self.usn = r.getheader("usn")
        self.st = r.getheader("st")
        self.cache = r.getheader("cache-control").split("=")[1]

    def __repr__(self):
        return "<SSDPResponse({location}, {st}, {usn})>".format(**self.__dict__)

def discover(service, timeout=3, retries=1, mx=2):
    group = ("239.255.255.250", 1900)
    lines = [
        'M-SEARCH * HTTP/1.1',
        f'HOST: {group[0]}:{group[1]}',
        'MAN: "ssdp:discover"',
        f'ST: {service}',
        f'MX: {mx}',
        '',
        ''
    ]
    message = "\r\n".join(lines).encode("utf-8")
    socket.setdefaulttimeout(timeout)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    responses = []
    for _ in range(retries):
        sock.sendto(message, group)
        while True:
            try:
                response, address = sock.recvfrom(1024)
                res_data = SSDPResponse(response)
                if res_data.st != service:
                    continue
                responses.append(
                    {"ip": address[0], "port": address[1], "usn": res_data.usn}
                )
            except socket.timeout:
                break
    sock.close()
    return responses
