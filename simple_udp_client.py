import socket

target_host = "127.0.0.1"
target_ip = 80

#Creating a socket object.
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#Sending some data.
client.sendto("AAABBBCCC",(target_host,target_ip))

#Receiving some data.
data, addr = client.recvfrom(4096)