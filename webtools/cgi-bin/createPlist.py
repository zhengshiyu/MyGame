#!/usr/bin/python
#coding=utf-8
import os,sys 
import os.path
import commands
import commandsutils
import cgi, cgitb 
def createlockFile():
	f = file("lockCreatePlist","w")
	f.close()

def removeLockFile():
	if os.path.isfile("lockCreatePlist"):
		os.remove("lockCreatePlist")



form = cgi.FieldStorage() 
userHome = os.path.expanduser('~')
cversion="trunk"
# 获取数据
if form.getvalue('cversion'):
	cversion = form.getvalue('cversion')

if os.path.isfile("lockCreatePlist"):
	print "Content-Type: text/html" 
	print 
	print "正在生成中，请稍后再试"
else:
	createlockFile()
	BASEDIR_SVN=userHome+"/work/qunying/share/"+cversion+"/美术资源"
	GAMECLIENT_PATH=userHome+"/work/qunying/client/"+cversion+"/gameClient/cached_res"
	commandsutils.execCmd("sh cgi-bin/packimage.sh "+BASEDIR_SVN+" "+GAMECLIENT_PATH)
	print "Content-Type: text/html" 
	print 
	print "生成成功"
	removeLockFile()