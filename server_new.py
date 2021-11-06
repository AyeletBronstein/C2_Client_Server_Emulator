#!/usr/bin/env python

from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import re
import time
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


def encrypt_with_key(a_message, _key):
    encryptor = PKCS1_OAEP.new(_key)
    encrypted_msg = encryptor.encrypt(a_message)
    print(encrypted_msg)
    return encrypted_msg
def decrypt_with_key(enc_message, _key):
    encryptor = PKCS1_OAEP.new(_key)
    encrypted_msg = encryptor.decrypt(enc_message)
    print(encrypted_msg)
    return encrypted_msg

key = RSA.importKey(open("rsa.public", "rb").read())
private_key = RSA.importKey(open("rsa.private", "rb").read())



class KodeFunHTTPRequestHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        
        try:
            
            print(self.path)
            f = open("./" + self.path) 
            
            self.send_response(200)
            tag=encrypt_with_key(b"hostname",key)
            self.send_header('Content-type','text/html')
            self.send_header('ETag',tag.hex())
            self.send_header('server','Microsoft-IIS/10.0')
            self.send_header('X-Powered-By','ASP.NET')
            self.end_headers()

            self.wfile.write(bytes(prepare_file(f.read()), "utf-8"))
            f.close()
            return
        
        except IOError:
            self.send_error(404, 'file not found')
    

def prepare_file(unprepared_file_content):
     return re.sub("(</html>)","<footer style=\"center\">{}</footer>\\1".format(time.ctime()),unprepared_file_content)

def run():
    print('http server is starting...')

    server_address = ('127.0.0.1', 8082)
    httpd = HTTPServer(server_address, KodeFunHTTPRequestHandler)
    print('http server is running...')
    httpd.serve_forever()
    
if __name__ == '__main__':
    run()
    