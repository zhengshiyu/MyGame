#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CGIHTTPServer import CGIHTTPRequestHandler  
from BaseHTTPServer import HTTPServer
from SocketServer import ThreadingMixIn  
import os
server_address=('',8080)

origin_do_GET = CGIHTTPRequestHandler.do_GET
   
def do_GET(self):
    isPacking = False
    pack_pidfilename = '/tmp/generateApp.pid'
    if os.path.isfile(pack_pidfilename):
        isPacking = True
    if isPacking:
        #  if self.requestline.find("GET /cgi-bin/pack.py?actiontype=generateApp&appname=") == -1:
        if self.requestline.find("GET /cgi-bin/pack") != -1:
            origin_do_GET(self)
            return
        tips = "正在打包，请稍后"
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-length", len(tips))
        self.end_headers()
        self.wfile.write(tips)
    else:
        origin_do_GET(self)

class ThreadingHttpServer( ThreadingMixIn, HTTPServer ):
    pass

CGIHTTPRequestHandler.do_GET = do_GET
myServer = ThreadingHttpServer( server_address, CGIHTTPRequestHandler )
myServer.serve_forever()
