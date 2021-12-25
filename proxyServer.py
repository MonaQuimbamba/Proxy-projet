#! /usr/bin/python3
import sys,os,socket,select
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
    host = re_get_host.search(ligne)
    if host:
        return host.groups(1)[0].strip("\\r\\n").split(":")

"""
   Fonction qui permet de faire un client :
   -  pour se connecter au serveur web
"""
def makeClient(hostName,port,request):
    adresse_serveur = socket.gethostbyname(hostName.replace(" ", ""))
    numero_port = int(port)
    print("IP address of the host name {} is: {}".format(hostName, adresse_serveur))
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
            continue
            #ma_socket.sendall(bytes(tapez,"utf8"))
        else: # dans le pere
            ligne = str(ma_socket.recv(1024),"utf8")
            if not ligne:
                break
            print ("From serveur  : "+hostName +" "+ligne)


"""
    Fonction qui envoit une requête au serveur web
"""
def sendRequest():
    print("")

"""
    Fonction va récuperer les infos en réponse du serveur web
"""

def serverResponse():
    print("")


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
    ligne=ligne.replace("Connection: Keep-Alive","")
    #ligne=ligne.replace("Proxy-Connection: Keep-Alive","")
    #ligne=ligne.replace("Accept-Encoding: gzip","")
    print(ligne)

""" === main == """
ma_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM,socket.IPPROTO_TCP)
ma_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
ma_socket.bind(('127.0.0.1', 8080))
ma_socket.listen(socket.SOMAXCONN)
#surveillance = [ma_socket]
print(" Server listening ..... ")
while 1:
    (nouvelle_connexion, TSAP_depuis) = ma_socket.accept()
    print ("Nouvelle connexion depuis ", TSAP_depuis)
    while 1:
        pid=os.fork()
        if not pid:
            ligne = str(nouvelle_connexion.recv(1024),'UTF8')
            if not ligne:
                break
            print("From client : "+ligne)
        else: # dans le pere
            tapez=input(" Entrer n'importe quoi ")
            nouvelle_connexion.sendall(bytes(tapez,"utf8"))
    #(evnt_entree,evnt_sortie,evnt_exception) = select.select(surveillance,[],[])
    #for un_evenement in evnt_entree:
    #    if (un_evenement == ma_socket): # il y a une demande de connexion
    #        nouvelle_connexion, depuis = ma_socket.accept()
    #        print ("Nouvelle connexion depuis ", depuis)
    #        surveillance.append(nouvelle_connexion)
    #        continue

        # sinon cela concerne une socket connectée à un client
    #    ligne = str(un_evenement.recv(1024),'UTF8')

    #    if not ligne :
    #        surveillance.remove(un_evenement) # le client s'est déconnecté
    #    else :
            #print (un_evenement.getpeername(),':',
            # preparer le host

    #        getHost(ligne)
            # faire le client pour envoyer et envoyer une requete au serveur distination
            #makeClient(host,port,"")
    #        makeRequest(ligne)

    #        continue

# fermer all sockets
#for client in surveillance:
#    client.close()
