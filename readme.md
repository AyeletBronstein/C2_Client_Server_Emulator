Updated server-client c2 scripts
Before running, install Crypto `python3 -m pip install Crypto`
Run server `python3 server_new.py`
Run client `python3 client_new.py`

The solution exploits the ETag cache control system to hide encrypted data (high entropy) in a header that is legitimatly populated with high entropy data.
Moreover, the client(victim) emultaes a chrome browser in sevral ways, such as: sending favicon.ico, using appropriate headers, etc.
