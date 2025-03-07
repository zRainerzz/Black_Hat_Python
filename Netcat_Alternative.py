import sys
import socket
import threading
import getopt
import subprocess
import os
from cryptography.fernet import Fernet

# Global variables
listen = False
command = False
execute = ""
target = ""
upload_destination = ""
port = 0
key = Fernet.generate_key()
cipher_suite = Fernet(key)

def usage():
    print()
    print("Usage: Netcat_Alternative.py -t target_host -p port")
    print("-l --listen                - listen on [host]:[port] for incoming connections")
    print("-e --execute=file_to_run   - execute the given file upon receiving a connection")
    print("-c --command               - initialize a command shell")
    print("-u --upload=destination    - upon receiving connection upload a file and write to [destination]")
    print()
    print()
    print("Examples: ")
    print("Netcat_Alternative.py -t 192.168.0.1 -p 5555 -l -c")
    print("Netcat_Alternative.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe")
    print("Netcat_Alternative.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\"")
    print("echo 'ABCDEFGHI' | ./Netcat_Alternative.py -t 192.168.11.12 -p 135")
    sys.exit(0)

def run_command(command):
    command = command.strip()
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        output = e.output
    return output

def client_handler(client_socket):
    global upload_destination
    global execute
    global command

    if len(upload_destination):
        file_buffer = b""
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            else:
                file_buffer += data

        try:
            with open(upload_destination, "wb") as file_descriptor:
                file_descriptor.write(file_buffer)
            client_socket.send(cipher_suite.encrypt(b"Successfully saved file to %s\r\n" % upload_destination.encode()))
        except Exception as e:
            client_socket.send(cipher_suite.encrypt(b"Failed to save file to %s\r\n" % upload_destination.encode()))

    if len(execute):
        output = run_command(execute)
        client_socket.send(cipher_suite.encrypt(output))

    if command:
        while True:
            client_socket.send(cipher_suite.encrypt(b"<BHP:#> "))
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024).decode()
            response = run_command(cmd_buffer)
            client_socket.send(cipher_suite.encrypt(response))

def server_loop():
    global target
    global port

    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()

def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((target, port))
        if len(buffer):
            client.send(cipher_suite.encrypt(buffer.encode()))

        while True:
            response = b""
            while True:
                data = client.recv(4096)
                if not data:
                    break
                response += data
            print(cipher_suite.decrypt(response).decode(), end="")
            buffer = input("")
            buffer += "\n"
            client.send(cipher_suite.encrypt(buffer.encode()))
    except Exception as e:
        print(f"[*] Exception! Exiting. {e}")
        client.close()

def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    if not len(sys.argv[1:]):
        usage()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:", ["help", "listen", "execute=", "target=", "port=", "command", "upload="])
    except getopt.GetoptError as err:
        print(str(err))
        usage()

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--command"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Unhandled Option"

    if not listen and len(target) and port > 0:
        buffer = sys.stdin.read()
        client_sender(buffer)

    if listen:
        server_loop()

if __name__ == "__main__":
    main()