import socket as sk
import os
import string
import queue as que
import platform as plt
import time as t
import threading as th

#   (non-privileged ports are > 1023)
"""
Socket = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
Socket.connect(("127.0.0.1", 25566))
while True:
    Socket.sendall(input("input : ").encode())
    data = Socket.recv(1024)
    print(data.decode())
"""

def newpath(path = str):
    if plt.system() == "Windows":
        return os.getcwd().encode() + path.encode()
    elif plt.system() == "Darwin":
        return os.getcwd().encode() + str(path.replace("\\", "/")).encode()

class client():
    def __init__(self, username):
        self.Socket = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
        self.username = username

        self.sendallqueue = que.Queue()
        self.joinhqueue = que.Queue()
        self.pingqueue = que.Queue()
        self.quitreqqueue = que.Queue()



    def sender(self):
        while True:
            packet = self.sendallqueue.get()
            if packet != "":
                packet[0].sendall(packet[1])


    def reciever(self):
        while True:
            s, addr = self.Socket.accept()
            packet = s.recv(2048)
            if packet != "":
                packet = list(packet.decode())
                if packet[0] == "ping":
                    self.pingqueue.put(packet)
                elif packet[0] == "join":
                    packet.append(s)
                    self.joinhqueue.put(packet)
                elif packet[0] == "quit":
                    self.quitreqqueue.put(s)
                elif packet[0] == "game":
                    packet.append(s)


    def tryrecieve(self, queue = que.Queue(), tries = 5, timout = 500): #ms 
        tr = tries
        while tr > 0:
            try:
                packet = queue.get()
                break
            except not packet:
                pass
            t.sleep(timout/1000)
            tr -= 1
        if not packet:
            return "timeout"
        else:
            return packet


    def joinreq(self, addr, joinkey):
        self.Socket.connect(addr)
        self.Socket.sendall(f"join {self.username} {joinkey}".encode())
        packet = self.tryrecieve(self.joinhqueue, 10, 100)
        if packet == "timeout":
            return "timeout"
        if packet[0] == "err":
            if packet[1] == "worngentkey":
                return "worngentkey"
            elif packet[1] == "servfull":
                return "servfull"
            elif packet[1] == "usronline":
                return "useronline"
        if packet[1] == "succesfull":
            return "succesfull"
