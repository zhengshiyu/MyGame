#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,sys 
import shutil
import ConfigParser
import httplib
import urllib2
import urllib
import re
import zlib
import datetime
LOCALETYPES=["zh_CN","zh_BH","zh_BS","zh_TW","en_US","ja_JP","ko_KR","vi_VN"]
CDN_IP="139.199.15.89"
conf = ConfigParser.ConfigParser()
if os.path.isfile("cgi-bin/generateapp.conf"):
	conf.read("cgi-bin/generateapp.conf")
else:
	conf.read("generateapp.conf")
#获取脚本文件的当前路径
def getcwd():
	path = sys.path[0]
	if os.path.isdir(path):
		return path
	elif os.path.isfile(path):
		return os.path.dirname(path)
def getSvnTag(name):
	return getString(name, "SVN_TAG","trunk")
def getserverlist(name):
	return getString(name, "serverlist","").split('"')[0]
def getserverlistBundleID(name):
	return getString(name, "BundleID","")
def getAppVersion(name):
	return getString(name, "AppVersion","")

def getAreaListURL(name):
	serverlist=getserverlist(name)
	BundleID=getserverlistBundleID(name)
	cversion=getAppVersion(name)
	return serverlist+"/arealist_"+BundleID+"_"+cversion+".xml"
def getAreaList(name):
	serverlist=getAreaListURL(name)
	try:
		response = urllib2.urlopen(serverlist+"?"+str(datetime.datetime.now().microsecond))
		xmlstring = response.read()
		return xmlstring
	except urllib2.URLError, e:
		print "URLError"
	except urllib2.HTTPError, e:
		print "HTTPError"	
	return ""
def getString(name,key,defaultvalue):
	global conf
	kvs = conf.items(name)
	key=key.lower()
	superConfig=""
	for k in kvs:
		if k[0]==key:
			return k[1]
		elif "super" ==k[0]:
			superConfig=k[1]
	if superConfig!="":
		return getString(superConfig,key,defaultvalue)
	return defaultvalue
def getSvnVersion(name):
	return getSvn2Version(getSvnTag(name))
	
def getSvn2Version(SVN_TAG):
	svn_version = SVN_TAG.split("/")
	if len(svn_version)>1:
		svn_version=svn_version[1]
		svn_version=svn_version.split(".")
		while len(svn_version)>3:
			svn_version.pop()
		return ".".join(svn_version)
	else:
		svn_version="0.0.5"
	return svn_version
def getResversion(cversion):
	try:
		serverlist="http://"+CDN_IP+"/sgqy/"+cversion
		response = urllib2.urlopen(serverlist+".txt?"+str(datetime.datetime.now().microsecond))
		xmlstring = response.read()
		return xmlstring.replace("\n","")
	except urllib2.URLError, e:
		print "get Res version URLError"
	except urllib2.HTTPError, e:
		print e.code
	return "0"

def downloadArealist(name,cacheRes):
	serverlist=getserverlist(name)
	BundleID=getserverlistBundleID(name)
	cversion=getAppVersion(name)
	try:
		print serverlist+"/arealist_"+BundleID+"_"+cversion+".xml?"
		response = urllib2.urlopen(serverlist+"/arealist_"+BundleID+"_"+cversion+".xml?"+str(datetime.datetime.now().microsecond))
		xmlstring = response.read()
		# print xmlstring
		r1 = re.compile(r'resversion="[\d|\.]+"')
		result = r1.search(xmlstring)
		if result:
			result = result.group(0)
			result = result.replace('resversion=',"")
			result = result.replace('"',"")
			if os.path.isdir(cacheRes):
				f=file(cacheRes+"/arealist.xml","w")
				f.write(xmlstring.replace(result,"{resversion}"))
				f.close()
			return result
		else:
			print 'search fails'
	except urllib2.URLError, e:
		print "URLError"
	except urllib2.HTTPError, e:
		print e.code
	return getSvnVersion(name)+"."+getResversion(name)

def getRemoteMD5(resversion):
	md5url="http://"+CDN_IP+"/sgqy/"+ resversion+"/md5all.zip"
	print md5url
	try:
		response = urllib2.urlopen(md5url+"?"+str(datetime.datetime.now().microsecond))
		print 
		md5url = zlib.decompress(response.read())
	except urllib2.URLError, e:
		print "URLError"
		md5url=getRemoteMD5Zip(resversion)
	except urllib2.HTTPError, e:
		print "HTTPError"
		md5url=getRemoteMD5Zip(resversion)
	except Exception as e:
		md5url=""
	return md5url
def getRemoteMD5Zip(resversion):
	md5url="http://"+CDN_IP+"/sgqy/"+ resversion+"/md5.zip"
	print md5url
	try:
		response = urllib2.urlopen(md5url+"?"+str(datetime.datetime.now().microsecond))
		print 
		md5url = zlib.decompress(response.read())
	except urllib2.URLError, e:
		md5url=""
		print "URLError"
	except urllib2.HTTPError, e:
		md5url=""
		print "HTTPError"
	return md5url 
def md5ToTable(md5txt):
	md5txt=md5txt.split('\r')
	table={}
	for line in md5txt :
		line=line.split('@')
		if len(line)>1:
			table[line[0]]=line[1]
	return table
if __name__=="__main__":
	print getSvn2Version("tags/1.5.0.41")
