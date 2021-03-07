import socket 
import threading
import json
import os
import sys
from connections import send
from cryptography.fernet import Fernet


HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
PASSWORD = "gamer"
DISCONNECT_MESSAGE = "exit"
PASSWORD_ENABLED = True

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

global IP_LIST
IP_LIST = []

def encrypt(binary, key):
    f = Fernet(key)
    return f.encrypt(binary)

def decrypt(binary, key):
    f = Fernet(key)
    return f.decrypt(binary)

def key():
    try:
        with open('key.key') as f:
            return f.read()
    except Exception as e:
        with open('key.key', 'wb') as f:
            print('Creating Key...')
            key = Fernet.generate_key()
            f.write(key)
        with open('key.key') as f:
            return f.read()
global KEY
KEY = key()
print(decrypt(encrypt("Encryption works fine on server end!".encode(), KEY), KEY).decode())

def generate(number=10, string=" "):
    product = ""
    for i in range(number):
        product = (product+string)
    return product

def run_cmd(cmd, nick):
    with open('server.log', 'a') as f:
        f.write(f"{nick}: "+cmd+"\n")
        f.close()
    data = open('server.log').read()
    return data

def handle_server():
    while True:
        cmd = input("")
        if cmd=="exit":
            sys.exit("Exited AIR Server")

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    sudo = False
    nickname = "Anonymous"
    connected = True
    IP_LIST.append(conn)
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False
                send("You have been exited from AIR", conn)
            elif msg.startswith("nick:"):
                nickname = msg.split(":")[1]
                print(f"[NICKNAME]({addr}) Nickname is now {nickname}")
            
            print(f"[{addr}, {nickname}] {msg}")
            if connected==True:
                if msg=="" and sudo==False:
                    send('You cannot access any data, to do so please do "sudo {password}"', conn)
                elif sudo==False and not msg.split()[0]=="sudo" and PASSWORD_ENABLED==True:
                    send('You cannot access any data, to do so please do "sudo {password}"', conn)
                elif msg=="":
                    with open('server.log') as f:
                        data = f.read()
                    send(data, conn)
                elif msg.split()[0]=="sudo" and PASSWORD_ENABLED==True:
                    if len(msg.split())==2:
                        if msg.split()[1]==PASSWORD:
                            sudo = True
                            with open("data/message.log") as f:
                                send(f.read(), conn)
                        else:
                            send("[AUTH] Wrong password, deleting thread", conn)
                            connected = False
                    else: send("[SUDO] SYNTAX: sudo {password}", conn)
                else:
                    send(run_cmd(msg, nickname), conn)
            else:
                print(f"[DISCONECT] {addr} disconected")
            

    conn.close()
        

def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}:{int(PORT)}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 2}")

server_term = threading.Thread(target=handle_server)
server_term.start()

print("[STARTING] server is starting...")
start()