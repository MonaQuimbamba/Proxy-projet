#! /usr/bin/python3
# coding: utf-8

tex='''<link rel="icon" href="/images/favicon.png" type="image/png">
    <title> :: Site pédagogique P-F. Bonnefoi</title>
    <p> Salut </p>
    <link href="/css/nucleus.css?1640202503" rel="stylesheet">
    <link href="/css/fontawesome-all.min.css?1640202503" rel="stylesheet">
    <link href="/css/hybrid.css?1640202503" rel="stylesheet">'''

startTitre=tex.find("<p>")
endTitre=tex.find("</p>")
string = tex[:startTitre+3] + "new_character" + tex[endTitre:]
print(string)
