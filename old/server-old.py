import socket
import threading
import datetime
import os

connected_devices = []
list_msgs = []
lst_tag = []

def service(client, addr):
    try:
        #Un nouveau utilisateur est connecté
        salutation = str(addr[0]) + " est connecté"
        print("\r \n" + salutation)

        client.send("".join([connected_device[1] for connected_device in connected_devices]))

        #Identification d'utilisateur
        nom = client.recv(1024).decode("UTF-8")
        info = nom + " a joint la conversation."
        print(info)

        #Un utilisateur avec le meme nom est déjà connecté
        if nom in [client[1] for client in connected_devices]:
            client.send("utilisateur déjà connecté".encode("UTF-8"))
            client.close()

        connected_devices.append((client, str(nom)))

        #Envoi du message d'attendance à tous les utilisateurs sauf celui-ci
        sendToAll(info, nom)

        # client.send(list_msgs)

        while True:
            msg = client.recv(2048).decode("UTF-8")

            print(msg)

            date_heure = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

            msg = {
                "nom" : str(nom),
                "msg" : str(msg),
                "opt" : "msg"
            }

            broadcastMsg = "\r" + str(nom) + "> " + str(msg)

            #Le tag
            if msg.__contains__("@"):
                #diviser la chaine en sous-chaines en respectant le delimiteur espace
                chaines = msg.split(" ")
                #Pour chaque sous-chaine
                for chaine in chaines:
                    #si la chaine contient debute par un @
                    if chaine[0] == "@":
                        #et si la chaine de character après l'@ est un nomp d'utilisateur connécté
                        if chaine[1:] in [connected_device[1] for connected_device in connected_devices]:
                            broadcastMsg = str(nom) + " vous a taggé> " + str(msg)
                            lst_tag.append((chaine[:1], nom))
                            opt = "tag"
                            sendTo(broadcastMsg, chaine[1:])
                lst_tag.clear()

            # La deconnexion
            if msg == "quit":
                broadcastMsg = str(nom) + " a quitté la conversation "
                for device in connected_devices:
                    if nom in device: #a optimizer
                        connected_devices.remove(device)
                        client.close()
                        opt = "deconnecté"
                        print(nom + " est déconnecté.")
                        print("Les membres de conversations :", end="\n")
                        for clt in connected_devices:
                            print(clt[1], end="\n")

            broadcastMsg += " \n  " + date_heure

            list_msgs.append((nom, msg, date_heure, opt, lst_tag))
            lst_tag.clear()
            save_in_file((nom, msg, date_heure, opt, lst_tag))

            if not broadcastMsg.__contains__("vous a taggé"):
                sendToAll(broadcastMsg, nom)

    except socket.error as err:
        print(err)
        client.close()

#Fonction de broadcast
def sendToAll(broadcastMsg, courant):
    for clt in connected_devices:
        if clt[1] != courant:
            clt[0].send(broadcastMsg.encode("UTF-8"))

#Fonction de broadcast pour des utilisateur spécifiques
def sendTo(broadcastMsg, client):
    for clt in connected_devices:
        if clt[1] == client:
            clt[0].send(broadcastMsg.encode("UTF-8"))

#Fonction d'enregistrement des logs
def save_in_file(msg):
    with open("server_log.data", "w") as f:
        chaine = ""
        for element in msg:
            if type(element) is str:
                chaine += element + ", "
            else:
                chaine.join(element)
        f.write(chaine + "\n")

#save log in xml file
def save_in_xml(msg):
    from lxml import etree
    message = etree.Element("message")
    utilisateur = etree.SubElement(message, "utilisateur")
    utilisateur.text = msg[0]
    date_heure = etree.SubElement(message, "date_heure")
    date_heure.text = msg[2]
    text_msg = etree.SubElement(message, "text")
    text_msg.text = msg[1]
    for tag in msg[4]:
        tag = etree.SubElement(message, "tag")
        tag.text = tag[0]
    with etree.xmlfile("server-log.xml", encoding='utf-8') as xf:
        xf.write(message)

#Fonction principale
def main():
    try:
        print('\n' + '\t' * 4 + "******************* Configuration du serveur *********************", end="\n")

        list_adresses_locaux = get_local_addresses()

        print("\n" + '\t' * 4 + "Veulliez choisir l'interface ou vous voulez demarrer votre serveur : ")
        print("\n" + '\t' * 4 + "Id |             Interface             |    Adresse    ")

        for index, interface in enumerate(list_adresses_locaux):
            print("\n" + '\t' * 4 + str(index + 1) + "  | " + interface["interface"] + "\t| " + interface["adresse"])

        indice_adresse = input("Indice d'interface(par defaut=localhost)> ")
        indice_adresse = len(list_adresses_locaux) - 1 if indice_adresse == "" else int(indice_adresse - 1)

        adresse = list_adresses_locaux[indice_adresse]["adresse"]

        port = input("port(par defaut=genere automatiquement)> ")
        port = get_available_port() if port == "" else int(port)

        print('\n' + '\t' * 4 + "******************* Configuration du serveur est terminee *********************", end="\n")

        serveur = start_serv(adresse, port)

        while(True):
            #acceptation et recuperation des informations du client.
            client, addr = serveur.accept()

            #Demarrage d'un service pour cet client
            thread = threading.Thread(target=service, args=(client, addr))
            thread.start()
    except socket.error as err:
        print(err)
        serveur.close()

#Fonction qui démarre le serveur
def start_serv(adresse, port):
    serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serveur.bind((adresse, port))
    print("serveur en attente ... " + adresse + ":" + str(port))
    serveur.listen(14)
    return serveur

#Récupération des interfaces du pc locale chaque interface avec son adresse
def get_local_addresses():
    import subprocess as sbp
    list_adresses_locaux = []
    cmd = sbp.run('ipconfig', stdout=sbp.PIPE, text=True).stdout.lower()
    liste = str(cmd).split("\n")
    nbre = 0
    for index, ligne in enumerate(liste):
        if ligne.__contains__("wi-fi") or ligne.__contains__("adapter") or ligne.__contains__("lan"):
            list_adresses_locaux.append({"interface" : ligne, "adresse" : None})
            nbre = len(list_adresses_locaux) - 1
            i = index + 2
            while i >= index + 2 and i < len(liste):
                if str(liste[i]).startswith(" ") and liste[i].__contains__("v4"):
                    list_adresses_locaux[nbre]["adresse"] = str(liste[i].split(":")[1]).strip()
                if not str(liste[i]).startswith(" "):
                    break
                i+=1
    list_adresses_locaux = [interface for interface in list_adresses_locaux if interface['adresse'] != None]
    list_adresses_locaux.append({"interface" : "localhost", "adresse" : "127.0.0.1"})
    return list_adresses_locaux

#Retourner le port fonctionnel dans le pc
def get_available_port():
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(('', 0))
    addr, port = tcp.getsockname()
    tcp.close()
    return port

if __name__ == "__main__":
    main()