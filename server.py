import socket
import threading
import datetime
import os
import json

connected_devices = []

def service(client, addr):
    #Un nouveau utilisateur est connecté
    salutation = str(addr[0]) + " est connecté"
    # save_in_file(salutation) #this
    print("\n" + salutation)

    msg = {
        "msg" : str(", ".join([connected_device[1] for connected_device in connected_devices])),
        "opt" : "utilisateurs",
    }

    client.send(json.dumps(msg).encode("UTF-8"))

    #Identification d'utilisateur
    nom = client.recv(2048).decode("UTF-8")

    #Un utilisateur avec le meme nom est déjà connecté
    if nom in [client[1] for client in connected_devices]:
        msg["msg"] = "Un utilisateur avec ce nom est déjà connecté"
        client.send(json.dumps(msg).encode("UTF-8"))
        client.close()
        return

    info = nom + " a joint la conversation."
    # save_in_file(info) #this
    print(info)
    msg["msg"] = info
    msg["opt"] = "notification"

    connected_devices.append((client, str(nom)))

    #Envoi du message d'attendance à tous les utilisateurs sauf celui-ci
    sendToAll(msg, nom)

    # client.send(list_msgs)

    while True:
        try:
            msg_depuis_client = client.recv(2048).decode("UTF-8")

            date_heure = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

            print(str(nom) + "> " + msg_depuis_client + " à " + date_heure)

            msg_obj = {
                "nom" : str(nom),
                "msg" : str(msg_depuis_client),
                "opt" : "msg",
                "date_heure" : date_heure,
                "lst_tag" : []
            }

            # broadcastMsg = "\r" + str(nom) + "> " + str(msg)

            # Le tag
            if msg_depuis_client.__contains__("@"):
                #diviser la chaine en sous-chaines en respectant le delimiteur espace
                chaines = msg_depuis_client.split(" ")
                #Pour chaque sous-chaine
                for chaine in chaines:
                    #si la chaine contient debute par un @
                    if chaine[0] == "@":
                        #et si la chaine de character après l'@ est un nomp d'utilisateur connécté
                        if chaine[1:] in [connected_device[1] for connected_device in connected_devices]:
                            #broadcastMsg = str(nom) + " vous a taggé> " + str(msg)
                            print(nom + " a taggé " + chaine[1:])
                            msg_obj["lst_tag"].append((chaine[1:], nom))

            # La déconnexion
            if msg_depuis_client == "&quit":
                # broadcastMsg = str(nom) + " a quitté la conversation "
                for device in connected_devices:
                    if nom in device: #a optimizer
                        connected_devices.remove(device)
                        client.close()
                        info = nom + " est déconnecté."
                        msg_obj["opt"] = "notification"
                        msg_obj["msg"] = info
                        print(info)
                        print("Les membres de conversation : ", end="\n")
                        for clt in connected_devices:
                            print(clt[1], end="\n")

            # save_in_file(msg_obj)

            sendToAll(msg=msg_obj)

        except socket.error:
            break

#Fonction de broadcast
def sendToAll(msg, nom=""):
    if msg["opt"] != "utilisateurs" and msg["opt"] != "notification":
        for clt in connected_devices:
            clt[0].send(json.dumps(msg).encode("UTF-8"))
    else:
        for clt in connected_devices:
            if clt[1] != nom:
                clt[0].send(json.dumps(msg).encode("UTF-8"))


# #Fonction de broadcast pour un utilisateur spécifique
# def sendTo(msg, client):
#     print(client)
#     for clt in connected_devices:
#         if clt[1] == client:
#             clt[0].send(json.dumps(msg).encode("UTF-8"))

#Fonction d'enregistrement des logs
# def save_in_file(msg):
#     with open("server_log.data", "w") as f:
#         chaine = ""
#         for element in msg:
#             if type(element) is str:
#                 chaine += element + ", "
#             else:
#                 chaine.join(element)
#         f.write(chaine + "\n")

#Fonction principale
def main():
    try:
        print('\n' + '\t' * 4 + "******************* Configuration du serveur *********************", end="\n")

        #Récuperer toutes les interfaces du pc locale chacune avec une adresse ip
        list_adresses_locaux = get_local_addresses()

        print("\n" + '\t' * 4 + "Veulliez choisir l'interface ou vous voulez demarrer votre serveur : ")
        print("\n" + '\t' * 4 + "Id |             Interface             |    Adresse    ")

        for index, interface in enumerate(list_adresses_locaux):
            print("\n" + '\t' * 4 + str(index + 1) + "  | " + interface["interface"] + "\t| " + interface["adresse"])

        indice_adresse = len(list_adresses_locaux) + 2
        while int(indice_adresse) not in range(1, len(list_adresses_locaux) + 1):
            indice_adresse = input("Indice d'interface(par defaut=localhost)> ")
            if indice_adresse == "":
                break

        indice_adresse = len(list_adresses_locaux) - 1 if indice_adresse == "" else int(int(indice_adresse) - 1)
        adresse = list_adresses_locaux[indice_adresse]["adresse"]

        port = 0
        while int(port) in range(0, 1024):
            port = input("port(par defaut=genere automatiquement)> ")
            if port == "":
                break

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
        exit()

# Fonction qui démarre le serveur
def start_serv(adresse, port):
    serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serveur.bind((adresse, port))
    print("serveur en attente ... " + adresse + ":" + str(port))
    serveur.listen(14)
    return serveur

# Récupération des interfaces du pc locale chaque interface avec son adresse
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