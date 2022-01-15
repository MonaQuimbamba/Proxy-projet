#!/usr/bin/python3



def filterHtml(ligne):
    res=""   
    
    f = [" titre ", "paragraph"]
    for item in f:
        if item=="titre":
            debutTag=ligne.find("<title>")
            finTag=ligne.find("</title>")
            if debutTag!=-1 and finTag!=-1:
                #print("trouvé le titre",debutTag," et fin ",finTag)
                ligne= ligne[:debutTag+7] + "claudio" + ligne[finTag:]
                res+=ligne
            else:
                res+=ligne
        if item =="paragraph":
            debutTag=ligne.find("<p>")
            finTag=ligne.find("</p>")
            if debutTag!=-1 and finTag!=-1:
                #print("trouvé le titre",debutTag," et fin ",finTag)
                ligne= ligne[:debutTag+3] + "JAS" + ligne[finTag:]
                res+=ligne
            else:
                res+=ligne
            

    

    return res

 
test = " <h1> salut </h1><title> yasmine </title>"

#print(filterHtml(test))
res=""
f = open("test.txt", "r")
for line in f:
    if line not in ["\n\r","","\n"]:
        lin=line.replace(" ","")
        res+=filterHtml(line)

print(res)
    