import sys
import socket
import getopt
import threading
import subprocess

#Defining some global variables.
listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0

def usage():
    print("zRainerzz Net Tool (main source: Black Hat Python)")
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
    
def main():
    global listen
    global command
    global execute
    global target
    global upload_destination
    global port
    
    if not len(sys.argv[1:]):
        usage()
    #Read the command line options.
        
    try:
        opts,args = getopt.getopt(sys.argv[1:], "hle:t:p:cu",['help','listen', 'execute', 'target', 'port', 'command', 'upload'])
    except getopt.GetoptError as err:
        print(str(err))
        print('/n')
        usage()
        
    for o, a in opts:
        if o in ("-h", '--help'):
            usage()
        elif o in ("-l", '--listen'):
            listen = True
        elif o in ('-e', '--execute'):
            execute = True
        elif o in ('-c', "--commandshell"):
            command = True
        elif o in ('-u', '--upload'):
            upload_destination = a
        elif o in ('-t', '--target'):
            target = a
        elif o in ('-p', '--port'):
            port = int(a)
        else:
            assert False, f"Unfortunately, this is an unhandled option: {o}"
            
            
        #Are we going to listen or just send some data from stdin?
        if not listen and len(target) and port > 0:
            # Read in the buffer from the command line
            # This will block, so send CTRL-D if not sending input to stdin
            buffer = sys.stdin.read()
            
            # Send data off
            client_sender(buffer)
            
        # We are going to listen and potentially upload things, execute commands, and drop a shell back depending on our command line options above
        if listen:
            server_loop()
            
def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try: 
        #Connect to our target host
        client.connect((target, port))
        
        if len(buffer):
            client.send(buffer)
        while True:
            #Now wait for data
            recv_len = 1
            response = ""
            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)



if __name__ == '__main__':
    main()