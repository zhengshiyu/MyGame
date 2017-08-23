#!/usr/bin/python
#coding=utf-8
import os,sys 
import os.path
import commands
import cgi, cgitb 
def createlockFile():
	f = file("lockcocostolua","w")
	f.close()

def removeLockFile():
	if os.path.isfile("lockcocostolua"):
		os.remove("lockcocostolua")

def cocostudioToLua():
	

if __name__=="__main__":
	print "Content-Type: text/html" 
	print 
	form = cgi.FieldStorage() 
	userHome = os.path.expanduser('~')
	# 获取数据
	cversion = form.getvalue('cversion')
	if not cversion:
		cversion = "trunk"

	if os.path.isfile("lockcocostolua"):
		print "正在生成中，请稍后再试"
	else:
		createlockFile()
		# commands.getstatusoutput("rm -rf "+userHome+"/work/qunying/share/trunk/UI/qunying/res")
		cocostudioPath=userHome+"/work/qunying/share/"+cversion+"/UI/qunying"
		lzgamePath=userHome+"/work/qunying/client/"+cversion+"/gameClient"
		try:
			output = cocostudioToLua()
			print output
			print "生成成功"
		except Exception as e:
			print "操作失败"
		finally:
			removeLockFile()