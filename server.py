#!/usr/bin/env python

from http.server import BaseHTTPRequestHandler, HTTPServer
import os

class KodeFunHTTPRequestHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        
        try:
            
            f = open("./" + self.path) 
            
            self.send_response(200)

            self.send_header('Content-type','application/json')
            self.end_headers()

            self.wfile.write(bytes(f.read(), "utf-8"))
            f.close()
            return
        
        except IOError:
            self.send_error(404, 'file not found')
    
def run():
    print('http server is starting...')

    server_address = ('127.0.0.1', 8082)
    httpd = HTTPServer(server_address, KodeFunHTTPRequestHandler)
    print('http server is running...')
    httpd.serve_forever()
    
if __name__ == '__main__':
    run()
    