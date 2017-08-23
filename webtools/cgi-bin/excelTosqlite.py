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
import zlib
import AppConfig
import re
curr = os.getcwd()
conn=""
connconfig={}
def copytree(src, dst, symlinks=False):
    names = os.listdir(src)
    if not os.path.isdir(dst):
        os.makedirs(dst)
          
    errors = []
    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks)
            else:
                if os.path.isdir(dstname):
                    os.rmdir(dstname)
                elif os.path.isfile(dstname):
                    os.remove(dstname)
                shutil.copy2(srcname, dstname)
            # XXX What about devices, sockets etc.?
        except (IOError, os.error) as why:
            errors.append((srcname, dstname, str(why)))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except OSError as err:
            errors.extend(err.args[0])
    if errors:
        raise Error(errors)
def getKeyType(filename,key):
	return "TEXT"
# 自动修复翻译出现的不添加转义字符 
def fixLangAuto(filename):
	filecontent=[]
	f = open(filename,'r')
	line=f.readline()
	p = re.compile(r'(?<!\\)"')
	n = re.compile(r'\\[ ]+n')
	r = re.compile(r'\\[ ]+r')
	rr = re.compile(r'\\[ ]+')
	while line:
		line=line.rstrip()
		if line.startswith("langTable["):
			while not line.endswith('"'):
				nextline = f.readline()
				if nextline:
					nextline=nextline.rstrip()
					line=line+"\\n"+nextline
				else:
					break
			line=line.split('= "')
			content = line[-1][0:-1]
			content=re.sub(p,'\\"',content)
			content=re.sub(n ,'\\n',content)
			content=re.sub(r ,'\\r',content)
			content=re.sub(rr,'',content)
			line = line[0]+' = "'+content+'"'
		filecontent.append(line)
		line=f.readline()
	f.close()
	f = open(filename,'wb')	
	f.write("\r\n".join(filecontent))	
	f.close()

def zipFile(file,tofile):
	if os.path.isfile(file):
		fixLangAuto(file)
		f = open(file,'r')
		line=f.read()
		f.close()
		line=line.replace("module(...,package.seeall)","")
		line=line.replace("langTable = {}","return {index=0")+"}"
		line=line.replace("langTable",",")
		# line=line.replace(r"[\s]+","")
		line=re.sub(r'[\r|\n]+','',line)
		line=re.sub(r'\][\s]+=[\s]+"',']="',line)
		# f = open(file,'wb')
		# f.write(line)
		# f.close()
		# print line
		result = zlib.compress(line)
		# result=line
		f = open(tofile+"/ui/locatype.pvr.ccz",'wb')
		f.write(result)
		f.close()
		commandsutils.svnCommit(tofile)
		# commandsutils.execCmd("cd "+tofile+"/ && svn st | grep '^\?' | tr '^\?' ' ' | sed 's/[ ]*//' | sed 's/[ ]/\\ /g' | xargs svn add")
		# commandsutils.execCmd("svn commit "+tofile+"/ -m 'auto commit '")
	# INTEGER
def txttosql(path,filename,locatype,skipLang):
	global connconfig
	sqlite3datafile = path+"export/db/"+filename+".txt"
	txtfile = path+"export/txt/"+filename+".txt"
	if locatype!="zh-CN":
		sqlite3datafile = path+"export/db/"+locatype.replace("_","-")+"/"+filename+".txt"
		txtfile = path+"export/txt/"+locatype+"/"+filename+".txt"
	if os.path.isfile(sqlite3datafile):
		os.remove(sqlite3datafile)
	conn = sqlite3.connect(sqlite3datafile)
	file_object = open(txtfile)
	try:
	    all_the_text = file_object.read( )
	finally:
	    file_object.close()
	xls_path_sheet = filename.split("_")
	book = xlrd.open_workbook(path+"luaxls/"+xls_path_sheet[0]+".xls")
	worksheet = book.sheet_by_name(xls_path_sheet[1])
	cellType={}
	cellType["id"]="INTEGER"
	for x in xrange(1,worksheet.row_len(0)):
		value = worksheet.cell(0, x).value
		if worksheet.cell(1, x).value=="int":
			cellType[value]="INTEGER"
		else:
			cellType[value]="TEXT"
	# print cellType
	all_the_text = all_the_text.split("#")
	Cellkeys = all_the_text[0].split("@")
	sql = "CREATE TABLE IF NOT EXISTS "+filename+"(["
	sql=sql+ Cellkeys[0] +"] INT PRIMARY KEY NOT NULL"
	insertsql="INSERT INTO "+filename+" (["+Cellkeys[0]+"]"
	for index in range(1, len(Cellkeys)):
		sql=sql+ ",["+Cellkeys[index] +"] "+cellType[Cellkeys[index]]
		insertsql=insertsql+",["+Cellkeys[index]+"]"
	sql=sql+");"
	insertsql=insertsql+") VALUES ("
	conn.execute(sql)
	
	for con in connconfig:
		if locatype == con or (locatype=="zh-CN" and not skipLang.has_key(con)):
			connconfig[con].execute(sql)
	for index in range(1, len(all_the_text)):
		keys=all_the_text[index].split("@")
		if len(keys)>1:
			values=keys[0]
			for index in  range(1, len(keys)):
				if cellType[Cellkeys[index]]=="TEXT":
					values=values+",'"+keys[index]+"'"
				else:
					values=values+","+keys[index]
			try:
				conn.execute(insertsql+values+")")
			except Exception as e:
				removeLockFile()
				print e
				raise Exception(insertsql+values+")")
			for con in connconfig:
				if locatype == con or (locatype=="zh-CN" and not skipLang.has_key(con)):
					connconfig[con].execute(insertsql+values+")")
	conn.commit()
	for con in connconfig:
		if locatype == con or (locatype=="zh-CN" and not skipLang.has_key(con)):
			connconfig[con].commit()
	conn.close()

def excel2client(excelpath,clientpath):
	global connconfig
	commandsutils.execCmd("cd "+clientpath+" && svn revert --depth infinity .")
	commandsutils.execCmd("cd "+excelpath+" && svn revert --depth infinity .")
	status ,output = commands.getstatusoutput("cd "+clientpath+" && svn update ")
	print output
	status ,output = commands.getstatusoutput("cd "+excelpath+" && svn update ")
	print output
	excel2tips(excelpath,clientpath)
	excelpath=excelpath+"表生成工具/runnable_jar/"
	
	a = os.popen("cd "+excelpath+" && sh genmiddle.sh&").read()
	commandsutils.execCmd("rm -rf "+excelpath+"export/db")
	commandsutils.execCmd("rm -rf "+excelpath+"export/txt/zip")
	commandsutils.execCmd("mkdir "+excelpath+"export/db")
	sqlite3datafile = excelpath+'export/db/config.txt'
	if os.path.isfile(sqlite3datafile):
		os.remove(sqlite3datafile)
	connconfig["zh-CN"] = sqlite3.connect(sqlite3datafile)
	
	for root, subdirs, files in os.walk(excelpath+"export/txt/"):
		if len(subdirs)>0:
		    for dirs in subdirs:
		    	if dirs.find("_")>1:
		    		if not os.path.exists(excelpath+'export/db/'+dirs.replace("_","-")):
		    			os.mkdir(excelpath+'export/db/'+dirs.replace("_","-"))
		    		sqlite3datafile = excelpath+'export/db/'+dirs.replace("_","-")+'/config.txt'
		    		if os.path.isfile(sqlite3datafile):
		    			os.remove(sqlite3datafile)
		    		connconfig[dirs] = sqlite3.connect(sqlite3datafile)
		
		if root == excelpath+"export/txt/":
		    for file in files:
		    	file = os.path.splitext(file)
		    	if file[1] == '.txt':
		    		saveTother={"zh-CN":True}
		    		for conn in connconfig:
		    			if conn !="zh-CN":
		    				if os.path.exists(root+conn+"/"+file[0]+file[1]):
		    					saveTother[conn]=True
		    		for conn in connconfig:
		    			if conn !="zh-CN":
		    				if os.path.exists(root+conn+"/"+file[0]+file[1]):
		    					txttosql(excelpath ,file[0],conn,saveTother)
			      	txttosql(excelpath,file[0],"zh-CN",saveTother)
	for conn in connconfig:
		connconfig[conn].close()
	a = os.popen("svn update "+clientpath+"config"+"&").read()
	a = os.popen("svn update "+clientpath+"image"+"&").read()
	commandsutils.execCmd("rm -rf "+clientpath+"config/*")
	commandsutils.execCmd("cp -rf "+excelpath+"export/db/*.txt "+clientpath+"config/")
	zipFile(excelpath+"export/lua/LangAuto.lua",clientpath+"image")
	for localtype in AppConfig.LOCALETYPES:
		localtype_ = localtype.replace("_","-")
		if os.path.exists(excelpath+"export/db/"+localtype_):
			if not os.path.exists(clientpath+"config/"+localtype_):
				os.makedirs(clientpath+"config/"+localtype_)
			commandsutils.execCmd("cp -rf "+excelpath+"export/db/"+localtype_+"/*.txt "+clientpath+"config/"+localtype_+"/")
		localtypes = localtype.lower().split("_")
		for langtype in localtypes:
			if os.path.exists(excelpath+"export/lua/LangAuto_"+langtype+".lua"):
				if not os.path.exists(clientpath+"image/"+localtype_):
					os.makedirs(clientpath+"image/"+localtype_+"/ui")
					commandsutils.execCmd("svn add "+clientpath+"image/"+localtype_)
				zipFile(excelpath+"export/lua/LangAuto_"+langtype+".lua",clientpath+"image/"+localtype_)
				break

	copytree(excelpath+"export/lua/",clientpath+"script/mvc/instance/model/cfg2profile/")
	commandsutils.svnCommit(clientpath+"config")
	commandsutils.svnCommit(excelpath+"luaxls")
	commandsutils.svnCommit(clientpath+"script/mvc/instance/model/cfg2profile/")
def excel2tips(excelpath,clientpath):
	commandsutils.execCmd("cd "+excelpath+"resource/i18n/ && svn up ")
	commandsutils.execCmd("cd "+clientpath+"script/base/ && svn up ")
	if os.path.exists(excelpath+"resource/i18n/LangTips.xls"):
		book = xlrd.open_workbook(excelpath+"resource/i18n/LangTips.xls")
		sheet=book.sheets()[0]
		for x in xrange(0,sheet.row_len(0)):
			value = sheet.cell(0, x).value
			localtype=value.lower().split("_")[-1]
			localeLang=[]
			p = re.compile(r'(?<!\\)"')
			for i in xrange(1,sheet.nrows):
				value = sheet.cell(i,x).value.strip()
				if value!="":
					value=re.sub(p,'\\"',value)
					localeLang.append(value.encode('utf8'))
			if len(localeLang)>0:
				localeLang='return {"'+'","'.join(localeLang)+'"}'
				if localtype=="cn":
					f = open(clientpath+"script/base/UpDateTipS.lua",'wb')
				else:
					f = open(clientpath+"script/base/UpDateTipS_"+localtype+".lua",'wb')
				f.write(localeLang)
				f.close()
		commandsutils.execCmd("cd "+clientpath+"script/base/ && svn st | grep '^\?' | tr '^\?' ' ' | sed 's/[ ]*//' | sed 's/[ ]/\\ /g' | xargs svn add")
		commandsutils.execCmd("cd "+clientpath+"script/base/ && svn commit -m'auto commit datatips' ")
def createlockFile():
	f = file("lockexectosql","w")
	f.close()

def removeLockFile():
	if os.path.isfile("lockexectosql"):
		os.remove("lockexectosql")

if __name__=="__main__":
	                              
	# 创建 FieldStorage 的实例化
	form = cgi.FieldStorage() 
	# 获取数据
	cversion = form.getvalue('cversion')
	if not cversion:
		cversion="trunk"
	userHome = os.path.expanduser('~')
	if os.path.isfile("lockexectosql"):
		print "Content-Type: text/html" 
		print 
		print "正在生成中，请稍后再试"
		removeLockFile()
	else:
		if os.path.isdir(userHome+"/work/qunying/share/"+cversion):
			createlockFile()
			try:
				excel2client(userHome+"/work/qunying/share/"+cversion+"/程序目录/",userHome+"/work/qunying/client/"+cversion+"/gameClient/cached_res/")
			except Exception as e:
				print e
			finally:
				removeLockFile()
			print "Content-Type: text/html" 
			print
			print "生成成功"
			removeLockFile()
		else:
			print "Content-Type: text/html" 
			print
			print "版本号不存在"