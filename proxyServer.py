#! /usr/bin/python3
# coding: utf-8
import sys,os,socket,select,ssl,re
from thread import *
import threading

#print_lock = threading.Lock()

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
    re_get_host= re.compile(r'Host:([\s\S]*)$') # regex pour trouver l'host dans une requete
    #host = re_get_host.search(ligne)
    #if host:
    #    return host.groups(1)
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
def makeClient(host,port,request,nouvelle_connexion_navigateur):

    adresse_serveur = socket.gethostbyname(host)
    context = ssl.create_default_context()
    ma_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if int(port)==80:
        s_sock=ma_socket
    else:
        s_sock = context.wrap_socket(ma_socket, server_hostname=host)

    print(" Client Starting ..... ")
    try:
        s_sock.connect((adresse_serveur, int(port)))
    except Exception as e:
        print ("Probleme de connexion", e.args)
        sys.exit(1)

    check_cache=isCache(host,request)

    if check_cache==False: #s'il n'existe pas un cache du serveur web
        sendRequest(s_sock,request) # envoyer la requête du client au serveur web
    while 1:
        if check_cache==False:
            contenu =read_line(s_sock)
            if contenu:
                saveRessource(host,contenu) # sauvegarder le contenu du serveur web
                # envoyer la response au navigateur
                #nouvelle_connexion_navigateur.sendall(contenu)
        else:
            contenuCache=getRessource(host)
            filename = "ressources/"+host
            f = open(filename, 'rb')
            l = f.read(1024)
            while l:
               nouvelle_connexion_navigateur.send(l)
            print('Sent ', repr(l))
            l = f.read(1024)
            f.close()
            print_lock.release()
    s_sock.close()
"""
    Fonction qui envoit une requête au serveur web
"""
def sendRequest(socket_client,request):
    socket_client.sendall(request.encode())

"""
    Fonction qui récupere les infos venant du  serveur web
"""

def serverResponse(socket_client):
    return socket_client.recv(1024)


"""
    Fonction va renvoyer les infos en réponse au navigateur web
"""
def sendServerResponse():
    print("")


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
def makeRequest(ligne):
    liste=ligne.splitlines()
    ## faire la 1ere ligne
    res=""
    if liste[0].split(" ")[0]=="GET":
        res+="GET / HTTP/1.0\r\n"

    if liste[0].split(" ")[0]=="CONNECT":
        res+="GET / HTTP/1.0\r\n"

    if liste[0].split(" ")[0]=="POST":
        res+="POST / HTTP/1.0\r\n"
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


""" === main == """
ma_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM,socket.IPPROTO_TCP)
ma_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
ma_socket.bind(('127.0.0.1', 8080))
ma_socket.listen(socket.SOMAXCONN)
print(" Server listening ..... ")
while 1:
    (nouvelle_connexion_navigateur, TSAP_depuis) = ma_socket.accept()
    print ("Nouvelle connexion depuis ", TSAP_depuis)
    ligne = nouvelle_connexion_navigateur.recv(1024)
    if  ligne:
        ligne=ligne.decode()
        host,port=getHost(ligne)
        request=makeRequest(ligne)

        ## Faire le client
        #print(" la request  : ",request)
        adresse_serveur = socket.gethostbyname(host)
        context = ssl.create_default_context()
        ma_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if int(port)==80:
            s_sock=ma_socket
        else:
            s_sock = context.wrap_socket(ma_socket, server_hostname=host)

        print(" Client Starting ..... ")
        try:
            s_sock.connect((adresse_serveur, int(port)))
        except Exception as e:
            print ("Probleme de connexion", e.args)
            sys.exit(1)

        check_cache=isCache(host,request)

        if check_cache==False: #s'il n'existe pas un cache du serveur web
            sendRequest(s_sock,request) # envoyer la requête du client au serveur web
        while 1:
            if check_cache==False:
                contenu =read_line(s_sock)
                if contenu:
                    saveRessource(host,contenu) # sauvegarder le contenu du serveur web
                    # envoyer la response au navigateur
                    #nouvelle_connexion_navigateur.sendall(contenu)
            else:
                contenuCache=getRessource(host)
                # envoyer la responde au naviagteur 
                #nouvelle_connexion_navigateur.sendall(contenu)

        #ma_socket.close()
        #print(repr(request))


ma_socket.close()
#kill -9 $(ps -A | grep python | awk '{print $1}
