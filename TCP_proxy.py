import sys
import socket
import threading
import logging
from cryptography.fernet import Fernet
import json

# Generate a key for encryption
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Configure logging
logging.basicConfig(filename='proxy.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def receive_from(connection):
    buffer = b""
    connection.settimeout(2)
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except:
        pass
    return buffer

def modify_request(data):
    # Add a header to the request
    return b"Modified-Request: True\r\n" + data

def modify_response(data):
    # Add a footer to the response
    return data + b"\r\nModified-Response: True"

def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    if receive_first:
        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            logging.info(f"[<==] Received {len(remote_buffer)} bytes from remote.")
            remote_buffer = modify_response(remote_buffer)
            client_socket.send(cipher_suite.encrypt(remote_buffer))
            logging.info("[<==] Sent to client.")

    while True:
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            logging.info(f"[==>] Received {len(local_buffer)} bytes from client.")
            local_buffer = modify_request(local_buffer)
            remote_socket.send(cipher_suite.encrypt(local_buffer))
            logging.info("[==>] Sent to remote.")

        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            logging.info(f"[<==] Received {len(remote_buffer)} bytes from remote.")
            remote_buffer = modify_response(remote_buffer)
            client_socket.send(cipher_suite.encrypt(remote_buffer))
            logging.info("[<==] Sent to client.")

        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            logging.info("[*] No more data. Closing connections.")
            break

def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((local_host, local_port))
    server.listen(5)
    logging.info(f"[*] Listening on {local_host}:{local_port}")

    while True:
        client_socket, addr = server.accept()
        logging.info(f"[*] Accepted connection from {addr[0]}:{addr[1]}")
        proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket, remote_host, remote_port, receive_first))
        proxy_thread.start()

def main():
    if len(sys.argv[1:]) != 1:
        print('Usage: ./TCP_proxy.py [config_file]')
        print('Example: ./TCP_proxy.py config.json')
        sys.exit(0)

    config_file = sys.argv[1]
    with open(config_file, 'r') as f:
        config = json.load(f)

    local_host = config['local_host']
    local_port = int(config['local_port'])
    remote_host = config['remote_host']
    remote_port = int(config['remote_port'])
    receive_first = config['receive_first']

    server_loop(local_host, local_port, remote_host, remote_port, receive_first)

if __name__ == "__main__":
    main()