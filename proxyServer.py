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
    #host = re_get_host.search(ligne)
    #if host:
    #    return host.groups(1)
    port=80
    host=""
    for item in ligne.splitlines():
        if item.split(":")[0]=="Host":
            if(len(item.split(":"))==3): # si y'a un port
                host=item.split(":")[1]
                port=item.split(":")[2]
            else:
                host=item.split(":")[1]
            return host,port

"""
   Fonction qui permet de faire un client :
   -  pour se connecter au serveur web
"""
def makeClient(host,port,request):
    print(repr(request))
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
            if not ligne:
                break
            print ("From serveur  : "+ host +" "+ligne)
            continue
    ma_socket.close()

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
def makeRequest(host,ligne):
    host=host.replace(" ","")
    liste=ligne.splitlines()
    ## faire la 1ere ligne
    res=""
    if liste[0].split(" ")[0]=="GET":
        res+="GET http://"+host+"/index.html HTTP/1.0\n"

    if liste[0].split(" ")[0]=="CONNECT":
        res+="GET https://"+host+"/index.html HTTP/1.0\n"

    if liste[0].split(" ")[0]=="POST":
        res+="POST https://"+host+"/index.html HTTP/1.0\n"



    for i in range(1,len(liste)):
        if liste[i].split(":")[0] not in ["Connection","Proxy-Connection","Accept-Encoding"]:
            if liste[i]=="":
                res=res.rstrip()
                res+="\r\n"
            else:
                res+=liste[i]+"\n"
    return res


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
    ligne = str(nouvelle_connexion.recv(1024),'UTF8')
    if not ligne:
        break
    host,port=getHost(ligne)
    request=makeRequest(host,ligne)
    makeClient(host,port,request)
    #print(repr(request))


ma_socket.close()
#kill -9 $(ps -A | grep python | awk '{print $1}')
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
