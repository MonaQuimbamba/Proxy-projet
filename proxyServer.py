#! /usr/bin/python3
# coding: utf-8
import sys,os,socket,select,ssl,re
from _thread import *



"""
  Fonction qui permet de lire les données d'une socket
"""
def read_line(ma_socket):
    ligne = b''
    while 1:
        caractere_courant = ma_socket.recv(1)
        if not caractere_courant :
            break
        if caractere_courant == b' \ r':
            caractere_suivant = ma_socket.recv(1)
            if caractere_suivant == b' \ n':
                break
            ligne += caractere_courant + caractere_suivant
            continue
        if caractere_courant == b' \ n':
            break
        ligne += caractere_courant
    return ligne

"""
 Fonction qui permet de récupérer :
  - le nom du serveur Web hébergeant la ressource
  - le numéro de port s'il est indiqué ( par défault le port 80 )
"""
def getHost(ligne):
    port=80
    host=""
    for item in ligne.splitlines():
        if item.split(":")[0]=="Host":
            if(len(item.split(":"))==3): # si y'a le port 443
                # ajouter www dans le host quand y'a pas
                host=item.split(":")[1]
                if host.split(".")[0].replace(" ","") not in ["www","Www","WWW","wWw","wwW"]:
                    host="www."+host.replace(" ","")
                port=item.split(":")[2]
            else:
                host=item.split(":")[1]
                if host.split(".")[0].replace(" ","") not in ["www","Www","WWW","wWw","wwW"]:
                    host="www."+host.replace(" ","")
            return host.replace(" ",""),port

"""
   Fonction qui permet de faire un client :
   -  pour se connecter au serveur web
"""
def client(host,port,request,nouvelle_connexion_navigateur):
    try:
        adresse_serveur = socket.gethostbyname(host)
    except Exception as e:
        print ("Probleme dans le host ", e.args)
        sys.exit(1)

    ma_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_sock=ma_socket

    print(" Client Starting ..... ")
    try:
        s_sock.connect((adresse_serveur, int(port)))
    except Exception as e:
        print ("Probleme de connexion", e.args)
        sys.exit(1)

    s_sock.sendall(request.encode())# envoyer la requête du client au serveur web
    while 1:
        response = read_line(s_sock)
        if (len(response) > 0):
            nouvelle_connexion_navigateur.send(response)
        else:
            break
    s_sock.close()
    nouvelle_connexion_navigateur.close()

"""
        Fonction qui permet de garder une ressource
"""
def saveRessource(host,contenu):
    file = open("ressources/"+host, "w")
    file.write(contenu)
    file.close()

"""
    Focntion qui permet de récuperer une ressource qui est dans le cache
"""
def getRessource(host):
    if os.path.isfile("ressources/"+host):
        try:
            file = open("ressources/"+host)
        except Exception as e:
            print(e.args)
            sys.exit(1)
        contenu = file.readline()
        file.close()
        return contenu

"""
    Fonction qui permet de vérifier s'il existe un cache de la requête
"""
def isCache(host,request):
    if request.split("\r\n")[0]=="GET / HTTP/1.0": # si c la 1ere requête GET
        if os.path.isfile("ressources/"+host): # si il existe un cache
            return True
        return False

"""
   Fonction qui permet de preparer la requete

  - supprimer les lignes commençant par : Connection: Keep-Alive et Proxy-Connection: Keep-Alive
  - supprimer la ligne commençant par Accept-Encoding: gzip
"""
def request(ligne):
    liste=ligne.splitlines()
    ## faire la 1ere ligne
    res=""
    if liste[0].split(" ")[0]=="GET":
        res+="GET / HTTP/1.0\r\n"

    if liste[0].split(" ")[0]=="CONNECT":
        #res+="GET / HTTP/1.0\r\n"
        print(" Le proxy traite que les requêtes HTPP ")
        sys.exit(1)

    if liste[0].split(" ")[0]=="POST":
        print(ligne)
        #res+="POST / HTTP/1.0\r\n"
    # faire l'en-tete
    for i in range(1,len(liste)):
        if liste[i].split(":")[0] not in ["Connection","Proxy-Connection","Accept-Encoding"]:
            if liste[i]=="":
                res=res.rstrip()
                res+="\r\n\r\n"
            else:
                tmp=liste[i].rstrip()
                res+=tmp+"\r\n"
    return res

"""
    Cette Fonction va demarrer le client
"""
def lancerClient(nouvelle_connexion_navigateur,contenu):
    try:
        contenu=contenu.decode()  # voir le contenu
        host,port=getHost(contenu) # récuperer le host et port
        requete=request(contenu) # preparer la requête
        client(host,port,requete,nouvelle_connexion_navigateur) # démarrer le client
    except Exception as e:
        print ("Probleme dans ", e.args)
        sys.exit(1)



""" === main == """
ma_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM,socket.IPPROTO_TCP)
ma_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
ma_socket.bind(('127.0.0.1', 8080))
ma_socket.listen(socket.SOMAXCONN)
print(" Server listening ..... ")
while 1:
    try:
        (nouvelle_connexion_navigateur, TSAP_depuis) = ma_socket.accept()
        print ("Nouvelle connexion depuis ", TSAP_depuis)
        contenu = nouvelle_connexion_navigateur.recv(9092)
        start_new_thread(lancerClient,((nouvelle_connexion_navigateur,contenu)))
    except KeyboardInterrupt:
       ma_socket.close()
       sys.exit(1)

ma_socket.close()
