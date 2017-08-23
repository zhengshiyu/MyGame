#!/usr/bin/python
#coding=utf-8
import cgi, cgitb 
import sqlite3
import os,sys 
import os.path
import commands
import commandsutils
import shutil
import httplib
import urllib2
import urllib
import re
import datetime
curr = os.getcwd()
conn=""
def getAllCdnFiles():
	stat,ret = commands.getstatusoutput('ssh root@27.131.221.98 "cd /data0/cdn/sgqy/&& ls  -l -t -d -g -G   */"')
	return ret
def deletefile(filename):
	if filename!="" and filename!="*":
		pattern = re.compile(r'[\d]+.[\d]+.[\d]+.[\d]+')
		if pattern.match(filename):
			stat,ret = commands.getstatusoutput('ssh root@27.131.221.98 "cd /data0/cdn/sgqy/&& rm -rf %s"' %(filename))
			return ret
if __name__=="__main__":  
	form = cgi.FieldStorage() 
	actiontype=form.getvalue('actiontype')
	print "Content-Type: text/html" 
	print
	if "deletefile" == actiontype:
		filename = form.getvalue('filename')
		print deletefile(filename);
	else:
		print getAllCdnFiles()