import socket as sk
import os
import random
import string
import queue as que
import platform as plt
import time as t
import gamedata as gmd



def newpath(path = str):
    if plt.system() == "Windows":
        return os.getcwd().encode() + path.encode()
    elif plt.system() == "Darwin":
        return os.getcwd().encode() + str(path.replace("\\", "/")).encode()

#   (non-privileged ports are > 1023)

"""
Socket = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
Socket.bind(("127.0.0.1", 25566))
Socket.listen()
while True:
    c, addr = Socket.accept()
    data = c.recv(1024)
    if data.decode() == "End" or not data:
        print(data.decode())
        break
    else:
        print(data.decode())
    c.sendall(input("input : ").encode())
"""
    

class server():
    def __init__(self, address = ("127.0.0.1", 32768), tabletxt = "exampletablename", joinkey = "123"):
        #variables, initiations
        self.onlinesockets = []
        self.onlineusers = []
        self.userchipcount = []
        self.game = gmd.Game()
        self.Socket = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
        self.Socket.bind(address)
        self.Socket.listen()
        self.joinkey = joinkey

        #queues
        self.joinhqueue = que.Queue()
        self.pingqueue = que.Queue()
        self.sendallqueue = que.Queue()
        self.quitreqqueue = que.Queue()
        self.gamedataqueue = que.Queue()

        #configurations
        self.table = tabletxt
        self.configs = []
        with open(newpath("\\server datas\\" + str(self.table) + "\\tableconfigs.txt"), "r") as c:
            for conf in c:
                if conf.endswith("\n"): conf = conf.replace("\n", "")
                datatype = ""
                data = ""
                C = 0
                for L in conf:
                    if L == ":":
                        C = 1
                    elif C == 0:
                        datatype += L
                    else:
                        data += L
                self.configs.append(data)

    #   startup, gametype, assigned chips, timer
    def gentable(self, tablename, configs):
        with open(newpath("\\server datas\\", str(tablename) + "\\tableconfigs.txt"), "a") as c:
            for conf in configs:
                c.write(conf + "\n")

     

    #   thread
    #   example input to queue: type data socket
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
                    self.gamedataqueue.put(packet)


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

    #   thread
    def sender(self):
        while True:
            packet = self.sendallqueue.get()
            if packet != "":
                packet[0].sendall(packet[1])


    def tokengen(self):
        usedtokens = []
        with open(newpath("\\server datas\\" + self.table + "\\usedtokens.txt"), "r") as t:
            for utoken in t:
                if utoken.endswith("\n"): utoken = utoken.replace("\n", "")
                usedtokens.append(utoken)
                t.close()

        with open(newpath("\\server datas\\" + self.table + "\\usedtokens.txt"), "a") as t:
            letters = string.ascii_letters + string.digits
            while True:
                leng = 32
                token = ""
                while leng != 0:
                    token += letters[random.randint(0, 61)]
                    leng -= 1

                try:
                    usedtokens.index(token)
                except Exception:
                    t.write(token + "\n")
                    break
        return token

    #   thread
    def onlinepinger(self):
        while True:
            for socket in self.onlinesockets:
                self.sendallqueue.put([socket, "ping".encode()])
                packet = self.tryrecieve(queue=self.pingqueue, tries=10, timout=100)
                if packet == "online":
                    self.sendallqueue.put()
                if packet == "timeout":self.quithandler(socket)



    def quithandler(self, Socket):
        NO = self.onlinesockets.index(Socket)
        self.onlinesockets.pop(NO)
        self.onlineusers.pop(NO)
        self.userchipcount.pop(NO)

    #   thread
    #   example package (for login) -> join username enterancekey socket
    def joinhandler(self):
        while True:
            package = self.tryrecieve(queue=self.joinhqueue, tries=10, timout=100)
            if package[0] == "join":
                if self.joinkey != package[2]:
                    self.sendallqueue.put(package[3], "err wrongentkey".encode())
                elif len(self.onlineusers) >= 5:
                    self.sendallqueue.put(package[3], "err servfull".encode())
                else:
                    for username in self.onlineusers:
                        if package[1] == username:
                            self.sendallqueue.put([package[3], "err usronline".encode()])
                            break
                        else:
                            self.sendallqueue.put([package[3], "join successfull"])
                            self.onlinesockets.append(package[3])
                            self.onlineusers.append(package[1])
                            self.userchipcount.append(int(self.configs[0]))
            else:
                pass


    def setchips(self, username, amount):
        self.userchipcount[self.onlineusers.index(username)] = amount

    def getchips(self, username):
        return self.userchipcount[self.onlineusers.index(username)]

    def getsocket(self, username):
        return self.onlinesockets[self.onlineusers.index(username)]

    def clssock(self):
        for socket in self.onlinesockets:
            self.sendallqueue.put([socket, "serv closing"])
        self.Socket.close()


    #game username bet {amount} 
    #if {amount} = 0, register as folded
    def startgame(self):
        usercards = []
        self.game.shuffle()
        comcards = self.game.draw(5)
        bettings = []
        #round 1 bettings
        for user1 in self.onlineusers:
            cards = self.game.draw(2)
            usercards.append([cards, user1])
            self.sendallqueue.put([self.getsocket(user1), f"game cards {cards}".encode()])
            self.sendallqueue.put([self.getsocket(user1), f"game reqbet".encode()])
            for user2 in self.onlinesockets:
                self.sendallqueue.put([user2, f"game wfor {user1}".encode()])
            clock = self.configs[3]
            conf = 0
            while clock > 0:
                try:
                    packet = self.tryrecieve(queue=self.gamedataqueue, tries=10, timout=100)
                except:
                    if not packet:pass
                else:
                    if int(packet[3]) == 0:
                        for user in self.onlinesockets:self.sendallqueue.put([user, f"game fold {packet[1]}"])
                        for card in usercards:
                            if card[1] == packet[1]:usercards.pop(usercards.index(card))
                    else:
                        bettings.append([packet[1], packet[3]])
                        conf = 1
                        break
                t.sleep(1)
                clock =- 1
                self.sendallqueue.put([user1, f"game tleft {clock}"])
            if conf == 1:
                self.sendallqueue.put([self.getsocket(user1), f"game userbet {packet[3]}".encode()])
            else:
                    for user in self.onlinesockets:self.sendallqueue.put([user, f"game fold {packet[1]}"])
                    for card in usercards:
                        if card[1] == packet[1]:usercards.pop(usercards.index(card))
            

        #   Finish Obj for later:
        #       make a skech on how all the menus will look (hard)


        
        


                    


"""
if package[1] == "log":
    with open(newpath("\\server datas\\" + self.table + "\\userdatas.txt"), "r") as t:
        for user in t: 
            if user.endswith("\n"): user = list(user.replace("\n", ""))
            if user[0] == package[2]:
                if user[1] == package[3]:
                    self.sendallqueue.put([package[4], f"join {package[3]} certified".encode()])
                    self.sendallqueue.put([package[4], f"st {package[3]} SessionToken {self.tokengen()}".encode()])
                    self.onlinesockets.append(package[4])  
                else:
                    self.sendallqueue.put([package[4], f"join {package[3]} incpasskey".encode()])
            else:
                self.sendallqueue.put([package[4], f"join {package[3]} inctoken".encode()])
elif package[1] == "reg":
    with open(newpath("\\server datas\\" + self.table + "\\userdatas.txt"), "a") as t:
        t.write((self.tokengen(), package[2], self.configs[0]))
"""
                    

"""
with open(newpath("\\server datas\\" + self.table + "\\userdatas.txt"), "r") as t:
    for user in t: 
        if user.endswith("\n"): user = list(user.replace("\n", ""))
        if user[0] == package[1]:
            if user[1] == package[2]:
                self.sendallqueue.put([package[3], f"join {package[2]} certified".encode()])
                self.sendallqueue.put([package[3], f"st {package[2]} SessionToken {self.tokengen()}".encode()])
                self.onlinesockets.append(package[3])  
            else:
                self.sendallqueue.put([package[3], f"join {package[2]} incpasskey".encode()])
"""

if __name__ == "__main__":
    serv = server(tabletxt="exampletablename", joinkey="123")

"""
        ROADMAP

            Joinhandler
                client : join req + enterance key + asigns the token to the domain/join ip
                server : gives token + asigns the key to the token + gives seat no + asigns the set amount of chips + adds the player socket to the online sockets
                client : requests the amount of chips
                server : sends them the amount of chips the token(user) has
                -- waiting until game starts --
            
            playeronlinestatus
                for socket in online sockets:
                socket -> sends ping msg
                if not data -> remove socket
                else -> pass

            user registration and initiation
                Registration
                    send server a join packet ( ex : join reg ... , join log ...)


                
"""