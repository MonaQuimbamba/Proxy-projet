#! /usr/bin/python3
# coding: utf-8
import sys,os,socket,select,ssl
import re

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
                if host.split(".")[0] not in ["www","Www","WWW","wWw","wwW"]:
                    host="www."+host.replace(" ","")
                port=item.split(":")[2]
            else:
                host=item.split(":")[1]
                if host.split(".")[0] not in ["www","Www","WWW","wWw","wwW"]:
                    host="www."+host.replace(" ","")
            return host,port

"""
   Fonction qui permet de faire un client :
   -  pour se connecter au serveur web
"""
def makeClient(host,port,request):

    adresse_serveur = socket.gethostbyname(host.replace(" ", ""))
    numero_port = int(port)
    print("IP addresse du serveur web  {} est : {} et le port est : {} ".format(host, adresse_serveur,numero_port))
    ma_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(" Client Starting ..... ")
    try:
        ma_socket.connect((adresse_serveur, numero_port))
    except Exception as e:
        print ("Probleme de connexion", e.args)
        sys.exit(1)

    pid = os.fork()
    while 1:
        if not pid:
            ma_socket.sendall(bytes(request,"utf8"))
        else: # dans le pere
            ligne = str(ma_socket.recv(1024),"utf8")
            if ligne:
                print ("From serveur  :"+ligne)
            #continue
    ma_socket.close()

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
#surveillance = [ma_socket]
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
        adresse_serveur = socket.gethostbyname(host.replace(" ", ""))
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

        sendRequest(s_sock,request)
        while 1:
            ligne = s_sock.recv(1024)#serverResponse(s_sock)
            if ligne:
                #print ("on client from  serveur : ",type(ligne))
                nouvelle_connexion_navigateur.sendall(ligne)

        #ma_socket.close()
        #print(repr(request))


ma_socket.close()
#kill -9 $(ps -A | grep python | awk '{print $1}
