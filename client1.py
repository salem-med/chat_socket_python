import socket
import threading
import tkinter
from tkinter import *
import json
import time
import atexit
import datetime
import os

msgs = []
begin = False
nom = ""

def main():
    try:
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        adresse = str(input("adresse du serveur> "))
        port = int(input("port ou le serveur est demarre> "))
        soc.connect((adresse, port))

        atexit.register(exit_handler, soc)

        thread = threading.Thread(target=receptionMsgs, args=(soc, ))
        thread.start()

        #Attendre jusqu'a ce que le serveur envois la liste des utilisateurs connectés
        while not begin:
            pass

        global nom
        nom = str(input("Entrer votre Pseudo : "))
        soc.send(nom.encode("UTF-8"))

        while True:
            print("> ", end="")
            msg = str(input())
            print("\033[F", end="")
            soc.send(msg.encode("UTF-8"))

            if msg == "&quit":
                soc.close()
                exit()

            if msg == "&enregistrer":
                save_in_xml()

    except socket.error as err:
        print(err)
        soc.send("&quit".encode("UTF-8"))
        soc.close()
        exit()
    except KeyboardInterrupt as ki:
        soc.send("&quit".encode("UTF-8"))
        exit()

# def updateListMsgs(msgs=[]):
#     for msg in msgs:
#         l.insert(msg)

def receptionMsgs(socket):
    global nom
    while True:
        msg = socket.recv(2048).decode()

        if msg:
            msg = json.loads(msg)

            #Tester le type du message reçus depuis l'utilisateur
            if msg["opt"] == "notification":
                msg_a_affiche = "Information> " + msg["msg"]
            if msg["opt"] == "utilisateurs":
                msg_a_affiche = "\n Les utilisateurs connectés : \n" + msg["msg"]
                global begin
                begin = True
            elif msg["opt"] == "msg":
                # Si quelqu'un a taggé cet utilisateur
                if nom not in [tag[0] for tag in msg["lst_tag"]]:
                    msg_a_affiche = "{0}> {1} \n {2}".format(msg["nom"], msg["msg"], msg["date_heure"])
                else:
                    msg_a_affiche = msg["nom"] + " vous a taggé> " + msg["msg"] + "\n " + msg["date_heure"]

            msgs.append(msg)
            print(msg_a_affiche, end="\n")

            if msg_a_affiche.__contains__("déjà"):
                break

# Fonction exécutée avant la fermeture du programme
def exit_handler(soc):
    soc.send("&quit".encode("UTF-8"))

#save log in xml file
def save_in_xml():
    from lxml import etree
    messages = etree.Element("messages")
    for msg in msgs:
        #L'element parent
        message = etree.SubElement(messages, "message")
        #Sous element nom d'expéditeur
        if "nom" in msg.keys():
            utilisateur = etree.SubElement(message, "utilisateur")
            utilisateur.text = msg["nom"]
        #Sous element date et heure du message
        if "date_heure" in msg.keys():
            date_heure = etree.SubElement(message, "date_heure")
            date_heure.text = msg["date_heure"]
        #Sous element contenu du message
        text_msg = etree.SubElement(message, "text")
        text_msg.text = msg["msg"]
        #Sous element operation
        operation = etree.SubElement(message, "operation")
        operation.text = msg["opt"]
        #Sous element liste des tags dans ce message
        if "lst_tag" in msg.keys():
            for tag in msg["lst_tag"]:
                tagE = etree.SubElement(message, "tag")
                tagE.text = tag[0]

    # Formattage xml
    from xml.dom import minidom

    a_enregistrer = minidom.parseString(etree.tostring(messages)).toprettyxml(indent="   ")

    nom_fichier = "logs-" + datetime.datetime.now().strftime("%m-%d-%Y-%H-%M-%S") + ".xml"
    #Enregistrement
    with open(nom_fichier, "w") as f:
        f.write(a_enregistrer)
    print("Fichier enregistré : " + os.path.dirname(__file__) + "/" + nom_fichier)

if __name__ == "__main__":
    main()

