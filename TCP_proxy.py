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

def hexdump(src, length=16):
    result = []
    digits = 4 if isinstance(src, str) else 2
    for i in range(0, len(src), length):
        s = src[i:i+length]
        hexa = ' '.join([f'{ord(x):0{digits}X}' for x in s])
        text = ''.join([x if 0x20 <= ord(x) < 0x7F else '.' for x in s])
        result.append(f'{i:04X}   {hexa:<{length*(digits+1)}}   {text}')
    print('\n'.join(result))

def receive_from(connection):
    buffer = b""
    connection.settimeout(2)
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except Exception:
        pass
    return buffer

def request_handler(buffer):
    # Modify the request packet before sending to the remote server
    return b"Modified-Request: True\r\n" + buffer

def response_handler(buffer):
    # Modify the response packet before sending to the client
    return buffer + b"\r\nModified-Response: True"

def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    if receive_first:
        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            logging.info(f"[<==] Received {len(remote_buffer)} bytes from remote.")
            hexdump(remote_buffer)
            remote_buffer = response_handler(remote_buffer)
            client_socket.send(cipher_suite.encrypt(remote_buffer))
            logging.info("[<==] Sent to client.")

    while True:
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            logging.info(f"[==>] Received {len(local_buffer)} bytes from client.")
            hexdump(local_buffer)
            local_buffer = request_handler(local_buffer)
            remote_socket.send(cipher_suite.encrypt(local_buffer))
            logging.info("[==>] Sent to remote.")

        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            logging.info(f"[<==] Received {len(remote_buffer)} bytes from remote.")
            hexdump(remote_buffer)
            remote_buffer = response_handler(remote_buffer)
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