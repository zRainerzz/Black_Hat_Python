import socket
import threading

# Define the IP address and port number the server will bind to.
bind_ip = '0.0.0.0'  # '0.0.0.0' means the server will accept connections on all available interfaces.
bind_port = 9999     # Port number to listen on.

# Create a socket object using IPv4 (AF_INET) and TCP (SOCK_STREAM).
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the server to the specified IP address and port.
server.bind((bind_ip, bind_port))

# Start listening for incoming connections. The number 5 specifies the backlog (max queued connections).
server.listen(5)

# Inform the user that the server is ready and listening.
print('[*] Listening on %s:%d' % (bind_ip, bind_port))

# Define a function to handle communication with a connected client.
def handle_client(client_socket):
    # Receive data from the client (up to 1024 bytes).
    request = client_socket.recv(1024)
    
    # Print the data received from the client.
    print('[*] Received: %s' % request.decode('utf-8'))  # Decode bytes to string for readability.
    
    # Send a response back to the client.
    client_socket.send(b"ACK!")  # The 'b' prefix indicates a bytes object.
    
    # Close the client connection.
    client_socket.close()

# Main server loop to accept incoming client connections.
while True:
    # Accept an incoming connection. 'client' is the client socket, 'addr' is the client's address.
    client, addr = server.accept()
    
    # Print the address of the connected client.
    print('[*] Accepted connection from %s:%d' % (addr[0], addr[1]))
    
    # Create a new thread to handle the client's communication.
    client_handler = threading.Thread(target=handle_client, args=(client,))
    client_handler.start()
