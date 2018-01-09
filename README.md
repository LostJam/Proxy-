# Proxy-
my proxy with multithreading and compression.
takes client requests and removes hop by hop headers, sends to and receives from server, then back to client. If compression switch is on and is allowed it will return compressed file back
through client socket. If multithreading switch is on, will do so. When both are on serving time is halved. 
