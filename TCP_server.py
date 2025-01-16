import socket
import threading

bind_ip = '0.0.0.0'
bind_port = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((bind_ip, bind_port))

server.listen(5)

print ('[*] Listening on %s:%d' %(bind_ip, bind_port))

#This is our client-handling thread.
def handle_client(client_socket):
    
    #Print out what the client sends
    request = client_socket.recv(1024)
    
    print('[*] Received %s' % request)
    
    #Send back packet
    client_socket.send("ACK!")
    
    client_socket.close()
    
    
while True:
    