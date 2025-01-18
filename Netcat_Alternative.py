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