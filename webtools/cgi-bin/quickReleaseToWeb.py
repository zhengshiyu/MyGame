#!/usr/bin/python
#coding=utf-8
import os,sys 
import os.path
import commands
import shutil
import ConfigParser
import time

import cgi, cgitb
import httplib
import urllib2
import urllib
import re
import datetime
import AppConfig
import commandsutils
import zlib
try: 
    from hashlib import md5
except ImportError:
    print "no install hashlib"
#支持的语言 

def createlockFile():
    f = file("quickReleastToWeb","w")
    f.close()

def removeLockFile():
    if os.path.isfile("quickReleastToWeb"):
        os.remove("quickReleastToWeb")
def calMD5(str):
    m = md5()
    m.update(str)
    return m.hexdigest()

def calMD5ForFile(file):
    statinfo = os.stat(file)
    if int(statinfo.st_size) / (1024*1024) >= 1000:
        return calMD5ForBigFile(file)
    m = md5()
    f = open(file, 'rb')
    m.update(f.read())
    f.close()
    return m.hexdigest()

def calMD5ForFolder(dir, MD5File):
    outfile = open(MD5File+"all.txt",'w')
    fileList=[]
    for root, subdirs, files in os.walk(dir):
        for file in files:
            if file.find(" ")<0 and file.find("UpDateTipS")<0 and file!="md5.txt" and "config.txt"!=file and file!="md5.zip" and file!=".DS_Store" and os.path.splitext(file)[1] != '.eg':
                filefullpath = os.path.join(root, file)
                filerelpath = os.path.relpath(filefullpath, dir)
                if filerelpath[0]!=".":
                    statinfo = os.stat(filefullpath)
                    if statinfo.st_size>0:
                        md5 = calMD5ForFile(filefullpath)
                        md5 = filerelpath+'@'+md5+'_'+str(statinfo.st_size)+'\r'
                        outfile.write(md5)
                        fileList.append([md5,statinfo.st_size])
    outfile.close()
    listLen = len(fileList)
    localetypeFiles={}
    for x in xrange(0,len(AppConfig.LOCALETYPES)):
        localetypeFiles[AppConfig.LOCALETYPES[x].replace("_","-")]=[]
    for x in xrange(listLen-1,0,-1):
        filepath = fileList[x][0]
        for localetype in localetypeFiles.keys():
            if filepath.find(localetype)>-1:
                localetypeFiles[localetype].append(fileList[x])
                del fileList[x]

    for localetype in localetypeFiles.keys():
        localetypes=localetypeFiles[localetype]
        localetypeList=localetypes+fileList
        for lf in localetypes:
            lf = lf[0].split("@")[0].replace("/"+localetype,"")
            for x in xrange(len(localetypeList)-1,0,-1):
                rf=localetypeList[x][0].split("@")[0]
                if lf == rf:
                    del localetypeList[x]
                    break
        savemd5txt(localetypeList,MD5File+localetype.replace("-","_"))
    savemd5txt(fileList,MD5File)
    f = open(MD5File+"all.txt",'r')
    line=f.read()
    f.close()
    f = open(MD5File+"all.zip",'wb')	
    f.write(zlib.compress(line))	
    f.close()

def savemd5txt(filelist,filename):
    line=""
    filelist.sort(key=lambda x:x[1])
    for x in xrange(0,len(filelist)):
        f_s = filelist.pop((x%2)-1)
        if f_s[1]>0:
            line=f_s[0]+line
    outfile = open(filename+".txt",'w')	
    outfile.write(line)	
    outfile.close()
    outfile = open(filename+".zip",'wb')	
    outfile.write(zlib.compress(line))	
    outfile.close()

def delFolder(folder):

    curDir = os.getcwd()
    fl = os.listdir(folder)
    if len(fl) == 0:
        os.rmdir(folder)
        os.chdir(curDir)
        return;
    else:
        os.chdir(folder)
        for f in fl:
            if os.path.isdir(f):
                if ".svn"!=f:
                    delFolder(os.path.join(folder, f))
        os.chdir('..')
        fl = os.listdir(folder)
        if len(fl) == 0:
            os.rmdir(folder)
    os.chdir(curDir)

def calMD5ForBigFile(file):
    m = md5()
    f = open(file, 'rb')
    buffer = 8192  # why is 8192 | 8192 is fast than 2048
    while 1:
        chunk = f.read(buffer)
        if not chunk : break
        m.update(chunk)
    f.close()
    return m.hexdigest()

def updateCachedRes(svntag,target):
	if not os.path.exists(target):
		print target
		os.makedirs(target)
		svnurl="svn://svn2.intra.kaixin001.com/dev2/webgame/qunying/client/trunk/gameClient/cached_res"
		if svntag!="trunk":
			svnurl="svn://svn2.intra.kaixin001.com/dev2/webgame/qunying/client/"+svntag+"/gameClient/cached_res"
		
		cacheRes=svntag
		if os.path.isdir("cgi-bin/"):
			cacheRes="cgi-bin/"+svntag
		if not os.path.exists(cacheRes+"/cached_res"):
			os.mkdir(cacheRes+"/cached_res")
			commandsutils.execCmd("svn co "+svnurl +" "+cacheRes+"/cached_res")
		else:
			commandsutils.execCmd("cd "+cacheRes+"/cached_res && svn revert --depth infinity . && svn up ")
		
		commandsutils.execCmd('mkdir '+target+"/cached_res")
		commandsutils.execCmd('cp -rf '+cacheRes+'/cached_res/config '+target+"/cached_res/")
		commandsutils.execCmd('cp -rf '+cacheRes+'/cached_res/image '+target+"/cached_res/")
		commandsutils.execCmd('cp -rf '+cacheRes+'/cached_res/script '+target+"/cached_res/")
		commandsutils.execCmd('find '+target+'/cached_res/ -name "*.mine"  -exec rm -f {} \;')
		commandsutils.execCmd('find '+target+'/cached_res/ -name "*.lua.r*"  -exec rm -f {} \;')
		commandsutils.execCmd('find '+target+'/cached_res/ -name "*.eg"  -exec rm -f {} \;')
		commandsutils.execCmd('find '+target+'/cached_res/ -name ".DS_Store"  -exec rm -f {} \;')
		commandsutils.execCmd('find '+target+'/cached_res/ -name "*.bak"  -exec rm -f {} \;')
		commandsutils.execCmd("rm -rf "+target+"/cached_res/image/hero/halfbody/*.png")
		commandsutils.execCmd("rm -rf "+target+"/cached_res/image/zh-CN")
		commandsutils.execCmd("rm -rf "+target+"/cached_res/image/fonts")
		commandsutils.execCmd("rm -rf "+target+"/cached_res/image/*.ttf")
		commandsutils.execCmd("rm -rf "+target+"/cached_res/*.zip")
		commandsutils.execCmd("rm -rf "+target+"/cached_res/*.txt")
		commandsutils.execCmd("rm -rf "+target+"/cached_res/image/db/dfsdfsdfsdf.jpg")
		commandsutils.execCmd("rm -rf "+target+"/cached_res/image/MainScene.csb")
        uiDirs=["/cached_res/image/ui"]
        for x in AppConfig.LOCALETYPES:
            uiDirs.append("/cached_res/image/%s/ui/" %(x.replace("_","-")))

        for subDir in uiDirs:
            for root, subdirs, files in os.walk(target+subDir):
                for dirname in subdirs:
                    filefullpath = os.path.join(root, dirname)
                    if os.path.exists(filefullpath+".plist"):
                        commandsutils.execCmd("rm -rf %s" %(filefullpath))

        if os.path.exists(target+"/cached_res/image/ui/locatype.pvr.ccz"):
            commandsutils.execCmd("rm -rf "+target+"/cached_res/script/mvc/instance/model/cfg2profile/LangAuto*.lua")
        calMD5ForFolder(target+"/cached_res",target+"/cached_res/md5")
        commandsutils.execCmd('cd '+cacheRes+'/cached_res/ && svn info  | grep "Rev" > '+target+'/cached_res/revicion.zip')
	f = open(target+"/cached_res/md5all.txt",'r')
	line=f.read()
	f.close()
	return AppConfig.md5ToTable(line)
def compileLuasScripts(src,output,bitmode):
    result = commandsutils.execCmd("$QUICK_V3_ROOT/quick/bin/compile_scripts.sh -m files -i "+src+" -o "+output+" -b "+bitmode)
    if result.find("ERR:")>-1:
        return False
    return True
def releaseToWeb(SVN_TAG,isquick,localetype):
    curr = os.getcwd()
    cacheRes="/tmp/"
    userHome = os.path.expanduser('~')
    if os.path.exists("/Volumes/RamDisk/"):
        cacheRes="/Volumes/RamDisk/"
    cacheRes=cacheRes+time.strftime('%Y_%m_%d_%H_%M_%S')
    svn_version = AppConfig.getSvn2Version(SVN_TAG)
    localmd5 = updateCachedRes(SVN_TAG,cacheRes)
    resVersion = AppConfig.getResversion(svn_version)
    newResVersion = svn_version+"."+str(int(resVersion)+1)
    oldResVersion = svn_version+"."+resVersion
    remotemd5 = AppConfig.md5ToTable(AppConfig.getRemoteMD5(oldResVersion))
    resLen=(len(localmd5)==len(remotemd5))
    if isquick:
        keys = localmd5.keys()
        for key in keys:
            if remotemd5.has_key(key) and remotemd5[key] == localmd5[key]:
                os.remove(cacheRes+"/cached_res/"+key)
                del localmd5[key]
        delFolder(cacheRes+"/cached_res")
    os.chdir(curr)
    if len(localmd5)==0 and resLen:
        print "无更新"
        return 0,cacheRes
    if os.path.exists(cacheRes+"/cached_res/script"):
        if not compileLuasScripts(cacheRes+"/cached_res/script",cacheRes+"/cached_res/script64","64") or not compileLuasScripts(cacheRes+"/cached_res/script",cacheRes+"/cached_res/script","32"):
            print "编译脚本错误！"
            return 0,cacheRes
    # BundleID = AppConfig.getserverlistBundleID(appName)
    commandsutils.execCmd("rm -rf "+cacheRes+"/cached_res/*.txt")
    commandsutils.execCmd("rm -rf "+cacheRes+"/cached_res/config/config.txt")
    for x in xrange(0,len(AppConfig.LOCALETYPES)):
        commandsutils.execCmd("rm -rf "+cacheRes+"/cached_res/config/"+AppConfig.LOCALETYPES[x].replace("_","-")+"/config.txt")
    delFolder(cacheRes+"/cached_res")
    # 压缩文本文件
    for root, subdirs, files in os.walk(cacheRes+"/cached_res"):
        for file in files:
            if file.find("md5")<0 and file!="md5.txt" and file!="md5all.txt" and file!="md5.zip" and file!=".DS_Store" and os.path.splitext(file)[1] != '.eg':
                filefullpath = os.path.join(root, file)
                filerelpath = os.path.relpath(filefullpath, cacheRes+"/cached_res")
                if filerelpath[0]!=".":
                    ext = os.path.splitext(file)[1]
                    if ext==".txt" or ext==".lua" or ".plist"==ext:
                        # print filefullpath
                        f = open(filefullpath,'r+')
                        line=f.read()
                        result = zlib.compress(line)
                        f.seek(0)
                        f.truncate()
                        f.write(result)
                        f.close()

    commandsutils.execCmd("cd "+cacheRes+"/cached_res && zip -9 -r --exclude=*.svn*  --exclude=*.DS_Store*  "+newResVersion+".zip .")
    commandsutils.execCmd("scp "+cacheRes+"/cached_res/"+newResVersion+".zip root@"+AppConfig.CDN_IP+":/data0/cdn/sgqy/"+newResVersion+".zip")
    commandsutils.execCmd('ssh root@'+AppConfig.CDN_IP+' "[ -d /data0/cdn/sgqy/'+newResVersion+'/ ] && rm -rf /data0/cdn/sgqy/'+newResVersion+'"')
    commandsutils.execCmd('ssh root@'+AppConfig.CDN_IP+' "[ -d /data0/cdn/sgqy/'+oldResVersion+'/ ] && cp -rf /data0/cdn/sgqy/'+oldResVersion+'/ /data0/cdn/sgqy/'+newResVersion+'/"')
    commandsutils.execCmd('ssh root@'+AppConfig.CDN_IP+' "unzip -o /data0/cdn/sgqy/'+newResVersion+'.zip -d /data0/cdn/sgqy/'+newResVersion+'/"')
    commandsutils.execCmd('ssh root@'+AppConfig.CDN_IP+' "rm -rf /data0/cdn/sgqy/'+newResVersion+'.zip"')
    commandsutils.execCmd('ssh root@'+AppConfig.CDN_IP+' "echo \''+str(int(resVersion)+1)+'\'>/data0/cdn/sgqy/'+svn_version+'.txt"')

    # 更新版本
    # commandsutils.execCmd('sed "s/{resversion}/'+newResVersion+'/g" '+cacheRes+'/arealist.xml | sed "s/{BundleID}/'+BundleID+'/g" | sed "s/{serverlist}/'+AppVersion+'/g" | sed "s/{appversion}/'+AppVersion+'/g" > '+cacheRes+'/arealist'+AppVersion+'.xml')
    # commandsutils.execCmd('scp -i ~/.ssh/id_server_release '+cacheRes+'/arealist'+AppVersion+'.xml root@27.131.221.168:/data/wg_www/ss.ec.feidou.com/serverlist/arealist_'+BundleID+'_'+AppVersion+'.xml')
    # commandsutils.execCmd('ssh -i ~/.ssh/id_server_release root@"+AppConfig.CDN_IP+" "[ -d /data0/cdn/sgqy/'+BundleID+'/'+oldResVersion+'/ ] && rm -rf /data0/cdn/sgqy/'+BundleID+'/'+oldResVersion+'/"')
    return newResVersion ,cacheRes

def updateAreaList(appName,localetype):
    curr = os.getcwd()
    version,tempdir=releaseToWeb(AppConfig.getSvnTag(appName),True,localetype)
    os.chdir(curr)
    AppVersion = AppConfig.getAppVersion(appName)
    SvnVersion = AppConfig.getSvnVersion(appName)
    resVersion = AppConfig.getResversion(SvnVersion)
    oldVersion = AppConfig.downloadArealist(appName,tempdir)
    newResVersion=SvnVersion+"."+resVersion
    if newResVersion!= oldVersion:
        BundleID = AppConfig.getserverlistBundleID(appName)
        # 更新版本
        commandsutils.execCmd('sed "s/{resversion}/'+newResVersion+'/g" '+tempdir+'/arealist.xml | sed "s/{BundleID}/'+BundleID+'/g" | sed "s/{serverlist}/'+AppVersion+'/g" | sed "s/{appversion}/'+AppVersion+'/g" > '+tempdir+'/arealist'+AppVersion+'.xml')
        commandsutils.execCmd('scp -i ~/.ssh/id_server_release '+tempdir+'/arealist'+AppVersion+'.xml root@27.131.221.168:/data/wg_www/ss.ec.feidou.com/serverlist/arealist_'+BundleID+'_'+AppVersion+'.xml')
        commandsutils.execCmd("rm -rf "+tempdir)
        print "更新成功"
        return resVersion
    else:
        print "无需更新"
        commandsutils.execCmd("rm -rf "+tempdir)
        return 0

if __name__=="__main__":
    if os.path.isfile("quickReleastToWeb"):
        print "Content-Type: text/html" 
        print 
        print "正在生成中，请稍后再试"
    else:	
        form = cgi.FieldStorage()
        quick=True
        localetype="zh_CN"
        # 获取数据
        if form.getvalue('cversion'):
            appName =form.getvalue('cversion')
            localetype =form.getvalue('localetype')
            quick = form.getvalue('isquick')=="true"
        else:
            # 飞流母包
            # appName ="app9"

            # 三国群英7
            appName ="app2"
            # ios 提审包 1.1.1
            # appName ="app7"
            # 三分天下
            # appName ="sgqyz_sftx"

            # 应用宝
            # appName="app2"
            # ios 提审包 测试
            # appName = "app130"
        try:
            createlockFile()
            if quick:
                newResVersion = updateAreaList(appName,localetype)
            else:
                newResVersion,tempdir=releaseToWeb(appName,True,localetype)
                commandsutils.execCmd("rm -rf "+tempdir)
        except Exception as e:
            print e
            print "操作失败"
        finally:
            removeLockFile()
        print "Content-Type: text/html" 
        print
        if newResVersion == 0:
            print "资源为最新，无需更新"
        elif newResVersion:
            print "更新成功 "+ newResVersion
        else:
            print "更新失败 可能无更新文件"
