#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ConfigParser
import time
import generateapp
import AndroidProjConf

conf = ConfigParser.ConfigParser()
conf.read("cgi-bin/generateApp.conf")

def getAll(name):
    global conf
    kvs = conf.items(name)
    confs = {}
    superName = ""
    for kv in kvs:
        if kv[0]=="super":
            superName=kv[1]
            break
    
    if superName!="":
        confs = getAll(superName)
    for kv in kvs:
        key = kv[0]
        val = kv[1]
        confs[key] = val

    return confs

def getAllInJson(name):
    confs = getAll(name)
    string = '{'
    for k in confs:
        val = confs[k].replace('\"','\'')
        string += '"'+k+'"'+":"+'\"'+val+'\"'+','
    string = string[:len(string)-1]
    string += '}'
    return string

def getAllProjectNames():
    maps = AndroidProjConf.getConf()
    string = str(maps.keys())
    string = string[1:len(string)-1]
    string = string.replace('\'','')
    return string

def getAllConfName():
    string = str(conf.sections())
    string = string[1:len(string)-1]
    string = string.replace('\'','')
    return string
def generateApp(name,dev,recivers_email,recivers_wx):
    generateapp.generateAppThenEmail(name,dev,recivers_email.split(','))

def compile(projectname):
    if projectname.endswith(".xcodeproj"):
        generateapp.xcodeArchive(projectname)
    else:
        generateapp.androidArchive(projectname)

if __name__ == "__main__":
    begin = time.time()
    compile("sgqygame_baozouSDK.xcodeproj")
    #  print(getAllProjectNames())
    #  conf.read("generateApp.conf")
    #  getAllInJson("app2en")
    #  string = str(conf.sections())
    #  print(string[1:len(string)-1])
    end = time.time()
    print("总耗时:"+str(end-begin))
