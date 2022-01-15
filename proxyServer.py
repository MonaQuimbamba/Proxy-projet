#! /usr/bin/python3
# coding: utf-8
import sys,os,socket,select,ssl,re
import threading
import subprocess

global goFilter
goFilter = True

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
                    host="http://"+host.replace(" ","")
                port=item.split(":")[2]
            else:
                host=item.split(":")[1]
                if host.split(".")[0].replace(" ","") not in ["www","Www","WWW","wWw","wwW"]:
                    host="http://"+host.replace(" ","")
            return host.replace(" ",""),port


"""
 Fonction qui permet de récuperer les paramètres pour le filtre
"""

def getFiltres():
    try:
        f = open("Config/configFile.txt", "r")
        filter={}
        for line in f:
        	if line:
        		line=line.replace(" ","")
        		if len(line.split(":"))==2:
        			fil=line.split(":")[0]
        			valeur=line.split(":")[1].strip()
        			filter[fil]=valeur.replace(" ","")
        f.close()
    except Exception as e:
        print ("Probleme dans la fonction getFilter", e.args)
        sys.exit(1)
    return filter

"""
    Focntion qui permet de faire le filtre
"""

def filterHtml(ligne):
    res=""
    try:
        filtrers=getFiltres()
        for filter in filtrers:
            if filter=="titre":
                debutTag=ligne.find("<title>")
                finTag=ligne.find("</title>")
                if debutTag!=-1 and finTag!=-1:
                    ligne= ligne[:debutTag+7] + filtrers[filter] + ligne[finTag:]
                    res+=ligne
                else:
                    res+=ligne
            """if filter =="paragraphe":
                debutTag=ligne.find("<p>")
                finTag=ligne.find("</p>")
                if debutTag!=-1 and finTag!=-1:
                    ligne= ligne[:debutTag+3] + filtrers[filter] + ligne[finTag:]
                    res+=ligne
                else:
                    res+=ligne"""
    except Exception as e:
        print ("Probleme dans la fonction filterHtml", e.args)
        sys.exit(1)
    return res

"""
    Fonction qui permet d'enregistrer la reponse dans un fichier avant le filtre
"""
def saveResponse(response):
    try:
        f = open("tmpHtml.txt", "w")
        f.write(response)
        f.close()
    except Exception as e:
        print ("Probleme dans la fonction saveResponse", e.args)
        sys.exit(1)

"""""
    Fonction qui permet d'appliquer le filtre
"""""
def filterApplied():
    res=""
    try:
        f = open("tmpHtml.txt", "r")
        for line in f:
            if line not in ["\n\r","","\n"]:
                lin=line.replace(" ","")
                res+=filterHtml(line)
        f.close()
    except Exception as e:
        print ("Probleme dans la fonction filterApplied", e.args)
        sys.exit(1)
    return res


"""
   Fonction qui permet de faire un client :
   -  pour se connecter au serveur web
"""
def client(host,port,request,nouvelle_connexion_navigateur):
    global goFilter

    cmd_ext = subprocess.Popen('host -t a '+host, stdin=subprocess.PIPE, stdout=subprocess.PIPE,shell=True)
    (sortie_standard,sortie_erreur) = cmd_ext.communicate()
    if (cmd_ext.returncode != 0): # on teste la valeur de succes de la commande
        try:
             host = "www."+host.split("//")[1]
             adresse_serveur = socket.gethostbyname(host)
        except Exception as e:
            print ("Probleme dans le host ", e.args)
            sys.exit(1)
    else :
        adresse_serveur=sortie_standard.split(" ")[-1].split("\n")[0]


    ma_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_sock=ma_socket
    try:
        s_sock.connect((adresse_serveur, int(port)))
    except Exception as e:
        print ("Probleme de connexion", e.args)
        sys.exit(1)

    s_sock.sendall(request.encode())# envoyer la requête du client au serveur web
    while 1:
        response = read_line(s_sock)
        if (len(response) > 0):
            if response:
                #if goFilter:
                saveResponse(response)
                response=filterApplied()
                #goFilter=False
                nouvelle_connexion_navigateur.sendall(response)
        else:
            break
    s_sock.close()
    nouvelle_connexion_navigateur.close()

"""
   Fonction qui permet de preparer la requete

  - supprimer les lignes commençant par : Connection: Keep-Alive et Proxy-Connection: Keep-Alive
  - supprimer la ligne commençant par Accept-Encoding: gzip
"""
def request(ligne,host):
    liste=ligne.splitlines()
    ## faire la 1ere ligne
    res=""
    if liste[0].split(" ")[0]=="GET":
        res+=liste[0].split(" ")[0]+" "+liste[0].split(" ")[1]+" HTTP/1.0\r\n"
    if liste[0].split(" ")[0]=="CONNECT":
        print(" Le proxy traite que les requêtes HTPP ")
    if liste[0].split(" ")[0]=="POST":
        res+=liste[0].split(" ")[0]+" "+liste[0].split(" ")[1]+" HTTP/1.0\r\n"
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
    if contenu:
        contenu=contenu.decode()  # voir le contenu
        host,port=getHost(contenu) # récuperer le host et port
        requete=request(contenu,host) # preparer la requête
        client(host,port,requete,nouvelle_connexion_navigateur) # démarrer le client


""" === main == """
ma_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM,socket.IPPROTO_TCP)
ma_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
ma_socket.bind(('127.0.0.1', 8080))
ma_socket.listen(socket.SOMAXCONN)
print(" Server listening ..... ")
while 1:
    try:
        (nouvelle_connexion_navigateur, TSAP_depuis) = ma_socket.accept()
        contenu = nouvelle_connexion_navigateur.recv(9092)
        clientStart = threading.Thread(target=lancerClient, args=(nouvelle_connexion_navigateur,contenu))
        clientStart.start()

    except KeyboardInterrupt:
       ma_socket.close()
       sys.exit(1)

ma_socket.close()
