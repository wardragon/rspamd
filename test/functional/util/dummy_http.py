#!/usr/bin/env python

import BaseHTTPServer
import SocketServer
import SimpleHTTPServer
import dummy_killer

import time
import os
import sys
import socket

PORT = 18080
HOST_NAME = '127.0.0.1'

PID = "/tmp/dummy_http.pid"


class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def setup(self):
        BaseHTTPServer.BaseHTTPRequestHandler.setup(self)
        self.protocol_version = "HTTP/1.1" # allow connection: keep-alive

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.log_message("to be closed: " + self.close_connection)

    def do_GET(self):
        response = "hello world"
        
        """Respond to a GET request."""
        if self.path == "/empty":
            self.finish()
            return

        if self.path == "/timeout":
            time.sleep(2)

        if self.path == "/error_403":
            self.send_response(403)
        else:
            self.send_response(200)

        if self.path == "/content-length":
            self.send_header("Content-Length", str(len(response)))

        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(response)
        self.log_message("to be closed: %d, headers: %s, conn:'%s'" % (self.close_connection, str(self.headers), self.headers.get('Connection', "").lower()))

        conntype = self.headers.get('Connection', "").lower()
        if conntype != 'keep-alive':
            self.close_connection = True
        
        self.log_message("ka:'%s', pv:%s[%s]" % (str(conntype == 'keep-alive'), str(self.protocol_version >= "HTTP/1.1"), self.protocol_version))


    def do_POST(self):
        response = "hello post"
        """Respond to a GET request."""
        if self.path == "/empty":
            self.finish()
            return

        if self.path == "/timeout":
            time.sleep(2)

        if self.path == "/error_403":
            self.send_response(403)
        else:
            self.send_response(200)
            
        if self.path == "/content-length":
            self.send_header("Content-Length", str(len(response)))

        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(response)


class ThreadingSimpleServer(SocketServer.ThreadingMixIn,
                   BaseHTTPServer.HTTPServer):
    def __init__(self):
        BaseHTTPServer.HTTPServer.__init__(self, (HOST_NAME, PORT), MyHandler)
        self.allow_reuse_address = True
        self.timeout = 1
        
    def run(self):
        dummy_killer.write_pid(PID)
        try:
            while 1:
                sys.stdout.flush()
                server.handle_request()
        except KeyboardInterrupt:
            print "Interrupt"
        except socket.error:
            print "Socket closed"

    def stop(self):
        self.keep_running = False
        self.server_close()


if __name__ == '__main__':
    server = ThreadingSimpleServer()

    dummy_killer.setup_killer(server, server.stop)

    server.run()
