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
import time
curr = os.getcwd()
def doResults(upfile):# 显示结果函数
    MAXBYTES = 1024000 #定义上传文件大小函数，单位为b
    filedata = ''  #初始化文件内容
    stop = False  #初始化判断
    filename = upfile.filename or ''  #获取文件名
    fp = upfile.file
    tmpname =  time.strftime('%Y_%m_%d_%H_%M_%S')+filename  #设置需要保存文件名称，按日期保存
    tempdir="/tmp/"
    if os.path.exists("/Volumes/RamDisk/temp/"):
    	tempdir="/Volumes/RamDisk/temp/"
    temp=open(tempdir+tmpname,'w+')
    temp.write(fp.read())
    temp.close()
    fp.close() #关闭文件
    commandsutils.execCmd("scp -i ~/.ssh/id_server_release "+tempdir+tmpname+" 168:/data0/wg_www/ss.ec.feidou.com/serverlist/res/html/"+tmpname)
    return "/serverlist/res/html/"+tmpname

if __name__=="__main__":
	form = cgi.FieldStorage()
	upfile = form["upload_file"]
	filename = upfile.filename or ''
	
	if upfile.file:
		filename = doResults(upfile)
		print "Content-Type: text/html\n"
		print filename
	else:
		print "Content-Type: text/html\n"
		print "false"