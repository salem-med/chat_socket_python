import socket
import threading
import tkinter
from tkinter import *

msgs = []

def main():
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    adresse = str(input("adresse du serveur> "))
    port = int(input("port ou le serveur est demarre> "))
    soc.connect((adresse, port))

    thread = threading.Thread(target=receptionMsgs, args=(soc))
    thread.start()

    nom = str(input("Entrer votre Pseudo : "))
    soc.send(nom.encode("UTF-8"))

    while True:

        msg = str(input("> "))
        soc.send(msg.encode("UTF-8"))
        if msg == "quit":
            exit()

# def updateListMsgs(msgs=[]):
#     for msg in msgs:
#         l.insert(msg)


def receptionMsgs(socket):
    while True:
        msg = socket.recv(4092).decode()
        msgs.append(msg)
        print(msg, end="\n")


if __name__ == "__main__":
    main()