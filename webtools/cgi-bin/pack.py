#!/usr/bin/python
#coding=utf-8
import cgi, cgitb 
import os,sys 
import os.path
import packapi

if __name__=="__main__":          
    form = cgi.FieldStorage() 
    actiontype=form.getvalue('actiontype')
    curdir = os.getcwd()

    print "Content-Type: text/html" 
    print
    if "getconf" == actiontype:
        appname=form.getvalue('appname')
        print packapi.getAllInJson(appname)
    elif "getAllProjectNames" == actiontype:
        print packapi.getAllProjectNames()
    elif "getAllConfName" == actiontype:
        print packapi.getAllConfName()
    elif "generateApp" == actiontype:
        appname  = form.getvalue('appname')
        dev      = form.getvalue('dev')
        recivers_email = form.getvalue('recivers_email')
        recivers_wx = form.getvalue('recivers_wx')
        if recivers_email == None:
            recivers_email = ""
        if recivers_wx == None:
            recivers_wx = ""
        os.chdir(curdir+"/cgi-bin")
        packapi.generateApp(appname,dev,recivers_email,recivers_wx)
    elif "compile" == actiontype:
        projectname=form.getvalue('projectname')
        os.chdir(curdir+"/cgi-bin")
        packapi.compile(projectname)
