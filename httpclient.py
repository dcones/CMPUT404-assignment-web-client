#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Daniel Cones, Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import sys, socket, re
from urllib.parse import urlparse, urlencode

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(2)
        self.socket.connect((host, port))
        return self.socket

    def recvall(self, socket):
        buffer = bytearray()
        part = True
        while part:
            try:    part = socket.recv(1024)
            except: break
            else:   buffer.extend(part)
        return buffer.decode('utf-8')

    def make_request(self, url, args, request_type):
        parse_result = urlparse(url)
        netloc = parse_result.netloc

        try:    host, port = netloc.rsplit(":",1)
        except: host, port = (netloc, "80")

        path = parse_result.path
        if not path: path = "/"

        body = ""
        if args: body = urlencode(args, encoding='utf-8')
        header_lines = []
        header_lines.append(request_type.format(path))
        header_lines.append("Host: {}".format(host))
        header_lines.append("Content-Length: {}".format(len(body)))
        header_lines.append("\r\n")
        header = "\r\n".join(header_lines)

        with self.connect(host, int(port)) as socket:
            socket.sendall((header+body).encode('utf-8'))
            result = self.recvall(socket)

        response_headers, response_body = result.split("\r\n\r\n",1)
        code = int(re.search("HTTP/.*? ([0-9]{3})", response_headers).group(1))
        return HTTPResponse(code, response_body)

    def GET(self, url, args=None):
        return self.make_request(url, args, "GET {} HTTP/1.1")

    def POST(self, url, args=None):
        return self.make_request(url, args, "POST {} HTTP/1.1")

    def command(self, url, cmd="GET", args=None):
        return self.make_request(url, args, cmd+" {} HTTP/1.1")

if __name__ == "__main__":
    client = HTTPClient()
    if (len(sys.argv) <= 1):
        result = HTTPResponse(None,"httpclient.py [GET/POST] [URL]\n")
    elif (len(sys.argv) == 3):
        result = client.command( sys.argv[2], sys.argv[1] )
    else:
        result = client.command( sys.argv[1] )
    print(result.body)
