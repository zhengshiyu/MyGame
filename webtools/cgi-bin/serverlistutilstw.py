#!/usr/bin/python
#coding=utf-8
import cgi, cgitb 
import sqlite3
import os,sys 
import os.path
import commands
import commandsutils
import shutil
import xlrd
import httplib
import urllib2
import urllib
import re
import datetime
curr = os.getcwd()
conn=""
def gethtmlFile(serverlist):
	try:
		response = urllib2.urlopen(serverlist+"?"+str(datetime.datetime.now().microsecond))
		xmlstring = response.read()
		return xmlstring
	except urllib2.URLError, e:
		print "URLError"
	except urllib2.HTTPError, e:
		print "HTTPError"	
	return ""
def sethtmlFile(serverlist,serverdata):
	tempdir="/tmp/"
	if os.path.exists("/Volumes/RamDisk/temp/"):
		tempdir="/Volumes/RamDisk/temp/"
	if serverlist!="":
		serverlist  = serverlist.split("/")[-1]
		f = file(tempdir+serverlist,"w")
		f.write(serverdata)
		f.close()
		commandsutils.execCmd("scp -i ~/.ssh/id_server_release "+tempdir+serverlist+" 222:/data0/www/serverlist/notic/"+serverlist)
def getAllArealist():
	stat,ret = commands.getstatusoutput('ssh 222 "cd /data0/www/serverlist/ && ls  -F *.xml"')
	return ret
def getAreaListFile(serverlist):
	try:
		response = urllib2.urlopen("http://m.qyz.heyshell.com/serverlist/arealist_"+serverlist+".xml"+"?"+str(datetime.datetime.now().microsecond))
		xmlstring = response.read()
		return xmlstring
	except urllib2.URLError, e:
		print "URLError"
	except urllib2.HTTPError, e:
		print "HTTPError"	
	return ""
def getAreaList(serverlist):
	try:
		response = urllib2.urlopen("http://m.qyz.heyshell.com/serverlist/arealist_"+serverlist+".xml"+"?"+str(datetime.datetime.now().microsecond))
		xmlstring = response.read()
		r1 = re.compile(r'<serverlist>[^<]+</serverlist>')
		result = r1.search(xmlstring)
		if result:
			result = result.group(0)
			result = result.replace('<serverlist>',"")
			result = result.replace('</serverlist>',"")
		return result
	except urllib2.URLError, e:
		print "URLError"
	except urllib2.HTTPError, e:
		print "HTTPError"	
	return ""
def getServerlist(serverlist):
	if serverlist!="":
		try:
			response = urllib2.urlopen(serverlist+"?"+str(datetime.datetime.now().microsecond))
			xmlstring = response.read()
			return xmlstring
		except urllib2.URLError, e:
			print "URLError"
		except urllib2.HTTPError, e:
			print "HTTPError"	
	return ""
def setServerlist(serverlist,serverdata):
	tempdir="/tmp/"
	if os.path.exists("/Volumes/RamDisk/temp/"):
		tempdir="/Volumes/RamDisk/temp/"
	serverlist = getAreaList(serverlist)
	if serverlist!="":
		serverlist  = serverlist.split("/")[-1]
		f = file(tempdir+serverlist,"w")
		f.write(serverdata)
		f.close()
		commandsutils.execCmd("scp -i ~/.ssh/id_server_release "+tempdir+serverlist+" 222:/data0/www/serverlist/"+serverlist)
def setArealist(serverlist,serverdata):
	tempdir="/tmp/"
	if os.path.exists("/Volumes/RamDisk/temp/"):
		tempdir="/Volumes/RamDisk/temp/"
	if serverlist!="":
		serverlist  = "arealist_"+serverlist.split("/")[-1]+".xml"
		f = file(tempdir+serverlist,"w")
		f.write(serverdata)
		f.close()
		commandsutils.execCmd("scp -i ~/.ssh/id_server_release "+tempdir+serverlist+" 222:/data0/www/serverlist/"+serverlist)

if __name__=="__main__":          
	# 创建 FieldStorage 的实例化
	form = cgi.FieldStorage() 
	actiontype=form.getvalue('actiontype')
	# 获取数据
	serverlist = form.getvalue('serverlist')

	print "Content-Type: text/html" 
	print
	if "getserverlist"==actiontype:
		print getServerlist(getAreaList(serverlist))
	elif "allarealist"==actiontype:
		print getAllArealist()
	elif "getarealist" == actiontype:
		print getAreaListFile(serverlist)
	elif "setarealist" == actiontype:
		serverdata = form.getvalue('serverdata')
		setArealist(serverlist,serverdata)
	elif "setserverlist" == actiontype:
		serverdata = form.getvalue('serverdata')
		setServerlist(serverlist,serverdata)
	elif "gethtmldata" == actiontype:
		print gethtmlFile(serverlist)
	elif "sethtmldata" == actiontype:
		serverdata = form.getvalue('serverdata')
		sethtmlFile(serverlist,serverdata)
	else:
		print getAllArealist()