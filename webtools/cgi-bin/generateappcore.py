# -*- coding: utf-8 -*-
import os,sys
import zipfile
import shutil
import datetime
import commands
import time
import ConfigParser
import re
import commandsutils
import quickReleaseToWeb
import AppConfig
import random
import AutoCropImage
from PIL import Image
import AndroidProjConf
import tempfile

try:
    import xlrd
except ImportError:
    print "no install xlrd"
try:
    import json
except ImportError:
    print "no install json"
TINYPNGKEYS = ["8LUD7Zw-l8HHl8WgFXkRYEsy4W388lXU","0bOIynZNb4pf8h-TxSwBXLQ3Y_wbJxyY"]
TINYPNGKEY  = TINYPNGKEYS[random.randint(0,len(TINYPNGKEYS)-1)]
filename    = time.strftime('%Y_%m_%d_%H_%M_%S')
# cleanup Cache
needCleanupCachedRes = True
#  shortcode
execute   = commandsutils.execCmd
getConfig = AppConfig.getString
#  execute("svn up images")
# execute("svn up appstore")
# execute("svn up android")

def replacefile(file,replaceText):
    f = open(file,'r+')
    # all_the_lines=f.readlines()
    line=f.read()
    f.seek(0)
    f.truncate()
    # for line in all_the_lines:
    #     for kvs in replaceText:
    #         line=re.sub(kvs[0],kvs[1],line)
    #         # line = line.replace(kvs[0],kvs[1])
    #     f.write(line)
    for kvs in replaceText:
        line=re.sub(kvs[0],kvs[1],line)
            # line = line.replace(kvs[0],kvs[1])
    f.write(line)
    f.close()
def tinypng(image,output):
    global TINYPNGKEY

    execute("curl https://api.tinify.com/shrink --user api:"+TINYPNGKEY+" --data-binary @"+image+" --dump-header /dev/stdout --output tinifyshrink.txt")
    if os.path.exists("tinifyshrink.txt"):
        f = open("tinifyshrink.txt",'r')
        data_string=f.read()
        f.close()
        decoded = json.loads(data_string)
        image = decoded["output"]["url"]
        execute("curl "+image+" --user api:"+TINYPNGKEY+" --dump-header /dev/stdout --output "+output)
        os.remove("tinifyshrink.txt")

def replacefilePackageDefine(platform,packageDefine,conf,app,dev):
    AppVersion          = getConfig(app, "AppVersion","")
    USEDSDK             = getConfig(app, "USEDSDK","")
    Fvalue              = getConfig(app, "Fvalue","")
    mtachannel          = getConfig(app, "mtachannel","")
    mtaappkey           = getConfig(app, "mtaappkey","")
    LOGINNOTICEURL      = getConfig(app, "LOGINNOTICEURL","")
    PAYOPEN             = getConfig(app, "PAYOPEN","")
    SVN_TAG             = getConfig(app, "SVN_TAG","")
    serverlist          = getConfig(app, "serverlist","")
    REPORTURL           = getConfig(app, "REPORTURL","")
    updatePath          = getConfig(app, "updatePath","")
    BundleID            = getConfig(app, "BundleID","")
    fontname            = getConfig(app, "fontname","")
    SERVERLIST_BundleID=BundleID
    if dev!="dev":
        dev = "function dump() \nend\nfunction print() \nend"
    else:
        dev=""
    SPLASHIMAGES = getConfig(app,"SPLASHIMAGES","")
    if platform == "ios":
        iosplashdir = getConfig(app,"iosplashdir","")
        if iosplashdir == "":
            if SPLASHIMAGES!="":
                SPLASHIMAGES=SPLASHIMAGES.split(",")
                del SPLASHIMAGES[0]
                SPLASHIMAGES = ",".join(SPLASHIMAGES)
    SPLASHVIEW=getConfig(app,"SPLASHVIEW","false")
    if SPLASHVIEW!="false":
        SPLASHVIEW='require("script.update.SplashView")'
    replacefile(packageDefine,[
        ["_DEV_",dev],
        ["0.0.3",AppVersion],
        ["com.igame.sgqyz",SERVERLIST_BundleID],
        ["_USEDSDK_",USEDSDK],
        ["_Fvalue_",Fvalue],
        ["_MTACHANNEL_",mtachannel],
        ["_MTAAPPKEY_",mtaappkey],
        ["_LOGINNOTICEURL_",LOGINNOTICEURL],
        ["_PAYOPEN_",PAYOPEN],
        ["_SERVERLIST_",serverlist],
        ["_REPORTURL_",REPORTURL],
        ["_UPGRADEURL_",updatePath],
        ["_LOCALETYPE_",getConfig(app,"localeType","zh_CN")],
        ["_LOGLEVEL_",getConfig(app,"LOGLEVEL","1")],
        ["_SPLASHIMAGES_",SPLASHIMAGES],
        ["_SPLASHVIEW_",SPLASHVIEW],
        ["_USELUASDK_",getConfig(app,"USELUASDK","false")],
        ["_DEFAULT_FONTNAME_",fontname]
        ])
def copyressrc(apppath,AppVersion):
    userHome = os.path.expanduser('~')
    execute("cp -rf "+userHome+"/work/qunying/client/trunk/gameClient/res " +apppath)
    execute("cp -rf "+userHome+"/work/qunying/client/trunk/gameClient/src " +apppath)
    replacefile(apppath + '/src/app/Startup.lua',[
            ['downloadPath..cached_res','downloadPath.."'+AppVersion+'"..cached_res']])
def copySplash(path,app,platform):
    SPLASHIMAGES = getConfig(app,"SPLASHIMAGES","")
    print("splashimages :"+SPLASHIMAGES)
    if SPLASHIMAGES!="":
        SPLASHIMAGES=SPLASHIMAGES.replace("\"","")
        SPLASHIMAGES=SPLASHIMAGES.split(",")
        if platform == "ios":
            iosplashdir = getConfig(app,"iosplashdir","")
            if iosplashdir=="":
                del SPLASHIMAGES[0]
        for image in SPLASHIMAGES:
            image1="images/"+image.split("/")[-1]
            if os.path.exists(image1):
                print path+image
                shutil.copy(image1,path+image)
        # 自定义启动画面
        SPLASHVIEW=getConfig(app,"SPLASHVIEW","false")
        if SPLASHVIEW!="false":
            execute("cp -rf images/"+SPLASHVIEW+"/* "+path+"image/ui/login/")
            execute("mv -f "+path+"/image/ui/login/*.lua "+path+"script/update/")
def copyToWeb(sourceFile,targetFile,versionName):
    #  global DAY_TIME
    #  execute("scp "+sourceFile+" vs:~/work/android.apk")
    #  execute('ssh vs "cd /Volumes/VMware\ Shared\ Folders/www/app/ &&[ ! -d '+versionName+' ] && mkdir '+versionName+'"')
    #  execute('ssh vs "cd /Volumes/VMware\ Shared\ Folders/www/app/ &&[ ! -d '+versionName+'/'+DAY_TIME+' ] && mkdir '+versionName+'/'+DAY_TIME+'"')
    #  execute('ssh vs "cd /Volumes/VMware\ Shared\ Folders/www/app/  && cp ~/work/android.apk '+versionName+'/'+DAY_TIME+"/"+targetFile+' && rm ~/work/android.apk && exit"')
    DAY_TIME = time.strftime('%Y_%m_%d')
    userHome = os.path.expanduser('~')
    targetFolder = userHome+"/www/"+versionName+'/'+DAY_TIME
    execute("mkdir -p "+targetFolder)
    targetPath = targetFolder+"/"+targetFile
    execute("cp "+sourceFile+" "+targetPath)
    #写入latest_apk_path文件
    execute("echo "+targetPath+" > latest_pack_path.txt")

# 生成启动图片
def createImage(source,target,W,H,Portrait):
    img         = Image.open(source)
    imgwidth    = img.size[0]
    imageheight = img.size[1]
    scalex      = float(W)/imgwidth
    scaley      = float(H)/imageheight

    if scalex < scaley :
        imgwidth    = int(imgwidth*  scalex )
        imageheight = int(imageheight*  scalex )
    else:
        imgwidth    = int(imgwidth*  scaley )
        imageheight = int(imageheight*  scaley )

    out     = img.resize((imgwidth, imageheight),Image.ANTIALIAS)
    newImg  = Image.new("RGB",(W,H),(255,255,255))
    borderX = (W-imgwidth)/2
    borderY = (H-imageheight)/2
    newImg.paste(out,(borderX,borderY,borderX+imgwidth,borderY+imageheight))
    if Portrait:
        newImg=newImg.transpose(Image.ROTATE_270)
    newImg.save(target,"PNG")
    # tinypng(target,target)
def changeLogoImageSize(source,target,W,H):
    img         = AutoCropImage.autoCrop(Image.open(source))
    imgwidth    = img.size[0]
    imageheight = img.size[1]
    scalex      = float(W)/imgwidth
    scaley      = float(H)/imageheight
    if scalex < scaley :
        imgwidth    = int(imgwidth*  scalex )
        imageheight = int(imageheight*  scalex )
    else:
        imgwidth    = int(imgwidth*  scaley )
        imageheight = int(imageheight*  scaley )

    out     = img.resize((imgwidth, imageheight),Image.ANTIALIAS)
    newImg  = Image.new("RGBA",(W,H),(0,0,0,0))
    borderX = (W-imgwidth)/2
    borderY = (H-imageheight)/2
    newImg.paste(out,(borderX,borderY,borderX+imgwidth,borderY+imageheight))
    newImg.save(target,"PNG")
def getpackageName(manifest):
    f    = open(manifest,'r')
    line = f.read()
    f.close()
    r1     = re.compile(r'package = "[^"]+"')
    result = r1.search(line)
    if result:
        result = result.group(0)
        result = result.replace('package=',"")
        result = result.replace('"',"")
        return result
    return "com.kx.sgqyz"
def changeLogo(path,app):
    logoimage = getConfig(app, "logoimage","")
    if logoimage!="":
        if os.path.exists("images/"+logoimage):
            changeLogoImageSize("images/"+logoimage,path+"res/image/ui/login/logo.png",338,174)
            if os.path.exists(path+"cached_res/image/ui/login/"):
                shutil.copy(path+"res/image/ui/login/logo.png",path+"cached_res/image/ui/login/logo.png")
    loginbg = getConfig(app, "loginbg","")
    if loginbg!="":
        if os.path.exists("images/"+loginbg):
            shutil.copy("images/"+loginbg,path+"res/image/ui/login/dldt.jpg")
            if os.path.exists(path+"cached_res/image/ui/login/"):
                shutil.copy("images/"+loginbg,path+"cached_res/image/ui/login/dldt.jpg")
    yjad=getConfig(app, "yjad","true")
    if yjad=="false":
        if os.path.exists("images/yjad_blank.png"):
            shutil.copy("images/yjad_blank.png",path+"res/image/ui/login/yjad.png")
            if os.path.exists(path+"cached_res/image/ui/login/"):
                shutil.copy("images/yjad_blank.png",path+"cached_res/image/ui/login/yjad.png")
    elif os.path.exists("images/"+yjad):
        execute("rm -rf "+path+"res/image/ui/login/yjad.png")
        shutil.copy("images/"+yjad,path+"res/image/ui/login/yjad.png")

    openvideo = getConfig(app, "openvideo","")
    if "false"==openvideo:
        execute("rm -rf "+path+"res/open.mp4")
    elif openvideo!="":
        if os.path.exists("images/"+openvideo):
            shutil.copy("images/"+openvideo,path+"res/open.mp4")
def updateCachedResFromSVN(SVN_TAG,tempdir,filename):
    cached_res_path=tempdir+"/"+SVN_TAG+"/"+filename
    if not os.path.exists(cached_res_path):
        quickReleaseToWeb.updateCachedRes(SVN_TAG,cached_res_path)
        if os.path.exists(cached_res_path+"/cached_res/config/config.txt"):
            execute("mv "+cached_res_path+"/cached_res/config/config.txt "+cached_res_path+"/cached_res/config/config.db")
            execute("rm -rf "+cached_res_path+"/cached_res/config/*.txt")
            execute("mv "+cached_res_path+"/cached_res/config/config.db "+cached_res_path+"/cached_res/config/config.txt")
        for x in xrange(0,len(AppConfig.LOCALETYPES)):
            localeType = AppConfig.LOCALETYPES[x].replace("_","-")
            if os.path.exists(cached_res_path+"/cached_res/config/"+localeType+"/config.txt"):
                execute("mv "+cached_res_path+"/cached_res/config/"+localeType+"/config.txt "+cached_res_path+"/cached_res/config/"+localeType+"/config.db")
                execute("rm -rf "+cached_res_path+"/cached_res/config/"+localeType+"/*.txt")
                execute("mv "+cached_res_path+"/cached_res/config/"+localeType+"/config.db "+cached_res_path+"/cached_res/config/"+localeType+"/config.txt")
        quickReleaseToWeb.compileLuasScripts(cached_res_path+"/cached_res/script",cached_res_path+"/cached_res/script64","64")
        quickReleaseToWeb.compileLuasScripts(cached_res_path+"/cached_res/script",cached_res_path+"/cached_res/script","32")
    return cached_res_path

#  revInfo : "branched/1.6.0/395015"
def updateCachedResFromSpecificREV(revInfo):
    revNumber = revInfo.split("/")[-1]
    pathInfo = revInfo[:len(revInfo)-len(revNumber)]
    cached_res_path = "cached_res/"+revInfo
    if not os.path.exists(cached_res_path):
        execute("mkdir -p "+cached_res_path)
        execute("svn checkout -r "+revNumber+" svn://10.8.0.88/dev2/webgame/qunying/client/"+pathInfo+"gameClient/cached_res "+cached_res_path+"/cached_res")
        quickReleaseToWeb.compileLuasScripts(cached_res_path+"/cached_res/script",cached_res_path+"/cached_res/script64","64")
        quickReleaseToWeb.compileLuasScripts(cached_res_path+"/cached_res/script",cached_res_path+"/cached_res/script","32")
        execute("mkdir -p "+cached_res_path+"/cached_res64 && mv "+cached_res_path+"/cached_res/script64 "+cached_res_path+"/cached_res64")
        execute("rm -fr "+cached_res_path+"/cached_res/.svn")
    return cached_res_path
def updateCachedResFromLocalFile(CachedResfile):
    cached_res_path=CachedResfile
    return cached_res_path
def updateCachedResFromArchive(Archive,appendPath):
    execute("unzip -d /tmp/Archive "+Archive)
    cached_res_path="/tmp/Archive/"+appendPath
    return cached_res_path
#本地化多语言
def localizationfile(path,localeType):
    if localeType!="zh_CN":
        userHome = os.path.expanduser('~')
        execute("cd "+userHome+"/work/qunying/share/trunk/程序目录/resource/i18n/ && svn up appLang.xls")
        book = xlrd.open_workbook(userHome+"/work/qunying/share/trunk/程序目录/resource/i18n/appLang.xls")
        sheet=book.sheets()[0]
        localeTypeIndex=0
        localeLang=[]
        for x in xrange(0,sheet.row_len(0)):
            value = sheet.cell(0, x).value
            if localeType == value:
                localeTypeIndex=x
                
        if localeTypeIndex==0:
            print "无翻译"
            return
        for i in xrange(1,sheet.nrows):
            lang = sheet.cell(i,localeTypeIndex).value
            if lang=="":
                lang = sheet.cell(i,0).value
            localeLang.append(['"'+sheet.cell(i,0).value.encode('utf8')+'"','"'+lang.encode('utf8')+'"'])
        print "本地化多语言 "+localeType
        for parent,dirnames,filenames in os.walk(path):
            for i in filenames:
                replacefile(parent+"/"+i,localeLang)
#修改包大小限制 
def checkFileSizeLimit(path,localeType,resVersion,size):
    if size>0:
        size=size*1024*1024
        f = open(path+"/cached_res/md5.txt",'r')
        line=f.read()
        f.close()
        localmd5 = AppConfig.md5ToTable(line)
        outfile = open(path+"/cached_res/md5.txt",'w')
        keys = localmd5.keys()
        #降序排序 保证将大文件打包进去
        filelist=[]
        for key in keys:
            filelist.append([key,int(localmd5[key].split("_")[1])])
        filelist.sort(key=lambda x:x[1],reverse=False)
        for x in xrange(0,len(filelist)):
            key=filelist[x][0]
            if size>0 or key=="script/base/UpDateTipS.lua" or key.find("effect/36.pvr.ccz")>-1 or key.find("effect/36.plist")>-1 or key=="config/config.txt" :
                size=size-filelist[x][1]
                outfile.write(key+"@"+localmd5[key]+"\r") 
            else:
                filename=key.replace(localeType+"/","")
                if os.path.exists(path+"/cached_res/"+filename):
                    os.remove(path+"/cached_res/"+filename)
                    del localmd5[key]
                else:
                    outfile.write(key+"@"+localmd5[key]+"\r")
        outfile.close()
        quickReleaseToWeb.delFolder(path+"/cached_res")
    else:
        replacefile(path+"/res/script/base/packageDefine.lua",[
                ["0.0.0.0",resVersion]
                ])
# 移除重复文件
def removeRepeat(path):
    if os.path.exists(path+"/cached_res/image/ui/effect/36.pvr.ccz"):
        os.remove(path+"/res/image/ui/effect/36.pvr.ccz")
        os.remove(path+"/res/image/ui/effect/36.plist")
        os.rename(path+"/cached_res/image/ui/effect/36.pvr.ccz",path+"/res/image/ui/effect/36.pvr.ccz")
        os.rename(path+"/cached_res/image/ui/effect/36.plist",path+"/res/image/ui/effect/36.plist")

    if os.path.exists(path+"/cached_res/script/base/UpDateTipS.lua"):
        os.remove(path+"/res/script/base/UpDateTipS.lua")
        os.rename(path+"/cached_res/script/base/UpDateTipS.lua",path+"/res/script/base/UpDateTipS.lua")
    
    if os.path.exists(path+"/cached_res64/script/base/UpDateTipS.lua"):
        os.remove(path+"/res64/script/base/UpDateTipS.lua")
        os.rename(path+"/cached_res64/script/base/UpDateTipS.lua",path+"/res64/script/base/UpDateTipS.lua") 
    # 删除字体 
    if os.path.exists(path+"/res/image/font"):
        execute("rm -rf "+path+"/res/image/font")      
def addFont(path,app):
    fontname = getConfig(app, "fontname","")
    if fontname!="" and os.path.exists("images/fonts/"+fontname):
        execute("cp -rf images/fonts/"+fontname+" "+path+"/res/")

def generateApp(conf,app,dev,platform=""):
    global filename
    global needCleanupCachedRes
    tempdir="/tmp/generateApp"
    userHome = os.path.expanduser('~')
    curr = os.getcwd()
    if os.path.exists("/Volumes/RamDisk/"):
        tempdir="/Volumes/RamDisk/generateApp"
    # tempdir=curr+"/generatapp"
    if os.path.isdir(tempdir):
        execute("rm -rf "+tempdir+"/*.apk")
        execute("rm -rf "+tempdir+"/*.ipa")
        execute("rm -rf "+tempdir+"/entitlements.plist")
        execute("rm -rf "+tempdir+"/android")
        execute("rm -rf "+tempdir+"/sgqygame.app")
        execute("rm -rf "+tempdir+"/Payload")
    if needCleanupCachedRes:
        execute("rm -rf "+tempdir+"/branches")
        execute("rm -rf "+tempdir+"/tags")
        commandsutils.svnRevertAndUpdate(curr+"/images")
        commandsutils.svnRevertAndUpdate(curr+"/p12")
        commandsutils.svnRevertAndUpdate(curr+"/android")
        commandsutils.svnRevertAndUpdate(curr+"/appstore")
        needCleanupCachedRes = False
    baseApp                = getConfig(app, "baseApp","appstore")
    baseAppNormcase        = baseApp.replace('\\','')
    AppVersion             = getConfig(app, "AppVersion","0.0.5")
    USEDSDK                = getConfig(app, "USEDSDK","false")
    Fvalue                 = getConfig(app, "Fvalue","561410041018")
    mtachannel             = getConfig(app, "mtachannel","appstore")
    mtaappkey              = getConfig(app, "mtaappkey","I5DGQJ322TJQ")
    LOGINNOTICEURL         = getConfig(app, "LOGINNOTICEURL","")
    PAYOPEN                = getConfig(app, "PAYOPEN","0")
    SVN_TAG                = getConfig(app, "SVN_TAG","trunk")
    serverlist             = getConfig(app, "serverlist","")
    REPORTURL              = getConfig(app, "REPORTURL","http://27.131.221.168/serverlist")
    ICON                   = getConfig(app, "icon","")
    localeType             = getConfig(app,"localeType","zh_CN")
    BundleID               = getConfig(app, "BundleID","com.kx.sgqyz")
    cachedRes_from_revision= getConfig(app, "cachedRes_from_revision","")
    local_cachedRes_path   = getConfig(app, "local_cachedRes_path","")
    cachedRes_from_archive = getConfig(app, "cachedRes_from_archive","")
    Facebook_app_id        = getConfig(app, "Facebook_app_id","1592353551057051")
    FacebookDisplayName    = getConfig(app, "FacebookDisplayName","")
    Facebook_app_token     = getConfig(app, "Facebook_app_token","1cef23d74513337cbab27b31f601a742")
    pubkey                 = getConfig(app, "pubkey","")
    APIKEY                 = getConfig(app, "APIKEY","")
    android_icon           = getConfig(app, "android_icon","fl_icon")
    NICEPLAY_APPID         = getConfig(app, "NICEPLAY_APPID","")
    NICEPLAY_APIKEY        = getConfig(app, "NICEPLAY_APIKEY","")
    NICEPLAY_APPLEID       = getConfig(app, "NICEPLAY_APPLEID","")
    NICEPLAY_CPIKEY        = getConfig(app, "NICEPLAY_CPIKEY","")
    AppsFlyerKey           = getConfig(app, "AppsFlyerKey","")
    AppsFlyerID            = getConfig(app, "AppsFlyerID","")
    URLSchemes             = getConfig(app, "URLSchemes","").split(",")
    if platform=="":
        platform = getConfig(app, "PLATFORM","")

    if platform=="":
        print("need config PLATFORM in generateapp.conf")
        return

    SERVERLIST_BundleID=BundleID
    if PAYOPEN=="0":
        PAYOPEN="false"
    else:
        PAYOPEN="true"
    SvnVersion=AppConfig.getSvnVersion(app)
    resVersion=AppConfig.downloadArealist(app,tempdir)
    print "game res version "+resVersion
    if not os.path.exists(tempdir ):
        os.makedirs(tempdir)

    if platform == "ios" and os.path.isdir(baseAppNormcase+"/sgqygame.app"):
        execute("cp -rf "+baseApp+"/sgqygame.app" + ' ' +tempdir )
        execute("rm -rf "+tempdir+'/sgqygame.app/res')
        execute("rm -rf "+tempdir+'/sgqygame.app/src')
        execute("rm -rf "+tempdir+'/sgqygame.app/cached_res')
        copyressrc(tempdir + '/sgqygame.app/',AppVersion)
        execute("rm -rf "+tempdir+'/sgqygame.app/res/script/base/packageDefine.lua')
        execute("cp -rf "+curr+"/packageDefine.lua " +tempdir + "/sgqygame.app/res/script/base/packageDefine.lua")

        if ICON!="":
            IOSICONSIZE={
                "AppIcon29x29"         : 29,
                "AppIcon29x29~ipad"    : 29,
                "AppIcon29x29@2x"      : 58,
                "AppIcon29x29@2x~ipad" : 58,
                "AppIcon29x29@3x"      : 87,
                "AppIcon40x40~ipad"    : 40,
                "AppIcon40x40@2x"      : 80,
                "AppIcon40x40@3x"      : 210,
                "AppIcon50x50~ipad"    : 50,
                "AppIcon50x50@2x~ipad" : 50,
                "AppIcon57x57"         : 57,
                "AppIcon57x57@2x"      : 114,
                "AppIcon60x60@2x"      : 120,
                "AppIcon60x60@3x"      : 180,
                "AppIcon72x72~ipad"    : 72,
                "AppIcon72x72@2x~ipad" : 144,
                "AppIcon76x76~ipad"    : 76,
                "AppIcon76x76@2x~ipad" : 152
            }
            for key in IOSICONSIZE.keys():
                img = Image.open("images/"+ICON)
                out = img.resize((IOSICONSIZE[key], IOSICONSIZE[key]),Image.ANTIALIAS)
                out.save(tempdir+"/sgqygame.app/"+key+".png","PNG")
        iosplashdir = getConfig(app,"iosplashdir","")
        if iosplashdir!="":
            execute("cp -r images/"+iosplashdir+"/*.png " +tempdir + "/sgqygame.app/")
        else:
            SPLASHIMAGES = getConfig(app,"SPLASHIMAGES","")
            if SPLASHIMAGES!="":
                SPLASHIMAGES=SPLASHIMAGES.replace("\"","")
                SPLASHIMAGES=SPLASHIMAGES.split(",")
                image=SPLASHIMAGES[0]
                image1="images/"+image.split("/")[-1]
                if os.path.exists(image1):
                    createImage(image1,tempdir+"/sgqygame.app/LaunchImage-700-568h@2x.png",1136,640,True)
                    createImage(image1,tempdir+"/sgqygame.app/LaunchImage-700-Landscape@2x~ipad.png",2048,1536,False)
                    createImage(image1,tempdir+"/sgqygame.app/LaunchImage-700-Portrait@2x~ipad.png",2048,1536,True)

                    createImage(image1,tempdir+"/sgqygame.app/LaunchImage-700-Landscape~ipad.png",1024,768,False)
                    createImage(image1,tempdir+"/sgqygame.app/LaunchImage-700-Portrait~ipad.png",1024,768,True)

                    createImage(image1,tempdir+"/sgqygame.app/LaunchImage-700@2x.png",960,640,True)
                    createImage(image1,tempdir+"/sgqygame.app/LaunchImage-800-667h@2x.png",1334,750,True)

                    createImage(image1,tempdir+"/sgqygame.app/LaunchImage-800-Landscape-736h@3x.png",2208,1242,False)
                    createImage(image1,tempdir+"/sgqygame.app/LaunchImage-800-Portrait-736h@3x.png",2208,1242,True)
        #  先转化plist为xml格式
        execute("plutil -convert xml1 "+tempdir+"/sgqygame.app/Info.plist")
        replacefile(tempdir+"/sgqygame.app/Info.plist",[
            [r"<key>CFBundleName</key>[\s]+<string>[^<]+</string>","<key>CFBundleName</key>\r\n\t<string>"+getConfig(app, "appName","")+"</string>"],
            [r"<key>CFBundleDisplayName</key>[\s]+<string>[^<]+</string>","<key>CFBundleDisplayName</key>\r\n\t<string>"+getConfig(app, "appName","")+"</string>"],
            [r"<key>CFBundleIdentifier</key>[\s]+<string>[^<]+</string>","<key>CFBundleIdentifier</key>\r\n\t<string>"+BundleID+"</string>"],
            [r"<key>CFBundleVersion</key>[\s]+<string>[^<]+</string>","<key>CFBundleVersion</key>\r\n\t<string>"+AppVersion+"</string>"],
            [r"<key>CFBundleShortVersionString</key>[\s]+<string>[^<]+</string>","<key>CFBundleShortVersionString</key>\r\n\t<string>"+AppVersion+"</string>"],
            [r"<key>CFBundleDevelopmentRegion</key>[\s]+<string>[^<]+</string>","<key>CFBundleDevelopmentRegion</key>\r\n\t<string>"+getConfig(app,"localeType","zh_CN")+"</string>"],
            [r"<key>FacebookAppID</key>[\s]+<string>[^<]+</string>","<key>FacebookAppID</key>\r\n\t<string>"+Facebook_app_id+"</string>"],
            [r"<key>FacebookDisplayName</key>[\s]+<string>[^<]+</string>","<key>FacebookDisplayName</key>\r\n\t<string>"+FacebookDisplayName+"</string>"],
            [r"<string>fb[\d]+</string>","<string>fb"+Facebook_app_id+"</string>"],
            [r"<key>NICEPLAY_APPID</key>[\s]+<string>[^<]+</string>","<key>NICEPLAY_APPID</key>\r\n\t<string>"+NICEPLAY_APPID+"</string>"],
            [r"<key>NICEPLAY_APIKEY</key>[\s]+<string>[^<]+</string>","<key>NICEPLAY_APIKEY</key>\r\n\t<string>"+NICEPLAY_APIKEY+"</string>"],
            [r"<key>NICEPLAY_APPLEID</key>[\s]+<string>[^<]+</string>","<key>NICEPLAY_APPLEID</key>\r\n\t<string>"+NICEPLAY_APPLEID+"</string>"],
            [r"<key>NICEPLAY_CPIKEY</key>[\s]+<string>[^<]+</string>","<key>NICEPLAY_CPIKEY</key>\r\n\t<string>"+NICEPLAY_CPIKEY+"</string>"],
            [r"<key>AppsFlyerKey</key>[\s]+<string>[^<]+</string>","<key>AppsFlyerKey</key>\r\n\t<string>"+AppsFlyerKey+"</string>"],
            [r"<key>AppsFlyerID</key>[\s]+<string>[^<]+</string>","<key>AppsFlyerID</key>\r\n\t<string>"+AppsFlyerID+"</string>"],
            #  [r"<string>UIInterfaceOrientationPortrait</string>",""]
            ])
        # 设置URLSchemes TODO
        # if len(URLSchemes)>0:
        #     commandsutils.setPlist(tempdir+"/sgqygame.app/Info.plist",{"CFBundleURLTypes:0:CFBundleURLSchemes":URLSchemes})
        replacefilePackageDefine(platform,tempdir+"/sgqygame.app/res/script/base/packageDefine.lua",conf,app,dev)
        if os.path.exists(tempdir+"/sgqygame.app/FLGamePlatform_Resources.bundle/FLProperty.plist"):
            replacefile(tempdir+"/sgqygame.app/FLGamePlatform_Resources.bundle/FLProperty.plist",[
                [r"<key>subCoopId</key>[\s]+<string>[^<]+</string>","<key>subCoopId</key>\r\n\t<string>"+getConfig(app,"FLGAMESDK_COOP_ID","300001")+"</string>"]
                ])
#       更新资源
        if local_cachedRes_path!="":
            print('updating CachedRes From local dir:'+local_cachedRes_path)
            cached_res_path=updateCachedResFromLocalFile(local_cachedRes_path)
            shutil.copytree(cached_res_path+"/cached_res",tempdir+"/sgqygame.app/cached_res")
            shutil.copytree(cached_res_path+"/cached_res64",tempdir+"/sgqygame.app/cached_res64")
        elif cachedRes_from_archive != "":
            print('updating CachedRes From ipa:'+cachedRes_from_archive)
            cached_res_path=updateCachedResFromArchive(cachedRes_from_archive,"Payload/sgqygame.app")
            shutil.copytree(cached_res_path+"/cached_res",tempdir+"/sgqygame.app/cached_res")
            shutil.copytree(cached_res_path+"/cached_res64",tempdir+"/sgqygame.app/cached_res64")
        else:
            if os.path.isdir(SVN_TAG+"/cached_res"):
                print('updating CachedRes from SVN tag:'+SVN_TAG)
                cached_res_path=updateCachedResFromSVN(SVN_TAG,tempdir,filename)

                if not os.path.exists(tempdir+"/sgqygame.app/cached_res"):
                    os.makedirs(tempdir+"/sgqygame.app/cached_res")
                if not os.path.exists(tempdir+"/cached_res/cached_res64"):
                    os.makedirs(tempdir+"/sgqygame.app/cached_res64")

                print("cp cached_res to sqgygame.app")
                shutil.copytree(cached_res_path+"/cached_res/config",tempdir+"/sgqygame.app/cached_res/config")
                shutil.copytree(cached_res_path+"/cached_res/image",tempdir+"/sgqygame.app/cached_res/image")
                execute("cp -rf "+tempdir+"/sgqygame.app/cached_res/image/"+localeType.replace("_","-")+"/* "+tempdir+"/sgqygame.app/cached_res/image/")
                execute("cp -rf "+tempdir+"/sgqygame.app/cached_res/config/"+localeType.replace("_","-")+"/* "+tempdir+"/sgqygame.app/cached_res/config/")
                execute("rm -rf "+tempdir+"/sgqygame.app/cached_res/image/*-*")
                execute("rm -rf "+tempdir+"/sgqygame.app/cached_res/config/*-*")
                shutil.copytree(cached_res_path+"/cached_res/script",tempdir+"/sgqygame.app/cached_res/script")
                shutil.copytree(cached_res_path+"/cached_res/script64",tempdir+"/sgqygame.app/cached_res64/script")
                if localeType!="zh_CN":
                    shutil.copy(cached_res_path+"/cached_res/md5"+localeType+".txt",tempdir+"/sgqygame.app/cached_res/md5.txt")
                else:
                    shutil.copy(cached_res_path+"/cached_res/md5.txt",tempdir+"/sgqygame.app/cached_res/md5.txt")
                UpDateTipS =localeType.split("_")[1].lower()
                execute("mv "+tempdir+"/sgqygame.app/cached_res/script/base/UpDateTipS_"+UpDateTipS+".lua "+tempdir+"/sgqygame.app/cached_res/script/base/UpDateTipS.lua")
                execute("mv "+tempdir+"/sgqygame.app/cached_res64/script/base/UpDateTipS_"+UpDateTipS+".lua "+tempdir+"/sgqygame.app/cached_res64/script/base/UpDateTipS.lua")
                execute("rm -rf "+tempdir+"/sgqygame.app/cached_res/script/base/UpDateTipS_*")
                execute("rm -rf "+tempdir+"/sgqygame.app/cached_res64/script/base/UpDateTipS_*")
                checkFileSizeLimit(tempdir+"/sgqygame.app",localeType.replace("_","-"),resVersion,int(getConfig(app,"sizelimit","0")))
                
        changeLogo(tempdir+"/sgqygame.app/",app)
        copySplash(tempdir+"/sgqygame.app/res/",app,platform)
        localizationfile(tempdir+"/sgqygame.app/res/script/update",localeType)
        quickReleaseToWeb.compileLuasScripts(tempdir+"/sgqygame.app/res/script",tempdir+"/sgqygame.app/res64/script","64")
        quickReleaseToWeb.compileLuasScripts(tempdir+"/sgqygame.app/res/script",tempdir+"/sgqygame.app/res/script","32")
        removeRepeat(tempdir+"/sgqygame.app")
        addFont(tempdir+"/sgqygame.app",app)
        mobileprovision=curr+"/p12/"+getConfig(app, dev+"_mobileprovision","")
        codesignName = getConfig(app, dev+"_codesignName","")
        # 新增 自动管理p12证书
        p12path             = getConfig(app, dev+"_p12","")
        pwd                 = getConfig(app, dev+"_p12_pwd","")
        if p12path!="" and pwd!="":
            codesignName=commandsutils.checkP12AndProvision(curr+"/p12/"+p12path,pwd,mobileprovision,dev)
        #证书处理结束

        execute("rm -rf %s/sgqygame.app/embedded.mobileprovision" %(tempdir))
        execute("cp %s %s/sgqygame.app/embedded.mobileprovision" %(mobileprovision,tempdir))
        execute("/usr/libexec/plistbuddy -c 'Delete :CFBundleIconFiles~ipad' "+tempdir+"/sgqygame.app/Info.plist")
        execute('/usr/libexec/PlistBuddy -x -c "print :Entitlements " /dev/stdin <<< $(security cms -D -i '+tempdir+'/sgqygame.app/embedded.mobileprovision)>'+tempdir+'/entitlements.plist')
        if dev=="dev":
            execute("/usr/libexec/PlistBuddy -c 'Set :get-task-allow true' "+tempdir+"/entitlements.plist")
        execute('/usr/bin/security unlock-keychain -p mengjie '+userHome+"/Library/Keychains/login.keychain" +' && /usr/bin/codesign -f -vv -s '+codesignName+' --entitlements '+tempdir+'/entitlements.plist  ' +tempdir+"/sgqygame.app")
        execute("rm -rf %s/Payload" %(tempdir))
        execute("mkdir %s/Payload" %(tempdir))
        execute("mv %s/sgqygame.app %s/Payload/" %(tempdir,tempdir))
        execute("cd %s && zip -r sgqygame.ipa ./Payload" %(tempdir))
        copyToWeb(tempdir+"/sgqygame.ipa",app+"_"+BundleID+"_"+AppVersion+"_"+filename+"_"+dev+'.ipa',app+"_"+BundleID+"_"+AppVersion)

    if platform == "android" :
        baseApkFile = commands.getoutput("find "+baseApp+" -type f -depth 1 -name '*.apk'")
        print('baseApkFile: '+baseApkFile)
        if not (os.path.isdir(baseAppNormcase+"/android") or os.path.exists(baseApkFile)):
            print('not find')
            return
        # 反编译apk 只保留反编译之后的文件 删除apk
        if os.path.exists(baseApkFile):
            apkName = os.path.basename(baseApkFile)
            execute("rm -rf "+baseApp+"/android")
            execute("apktool d -b "+baseApp+"/"+apkName+" -f -o "+baseApp+"/android")
            print("apktool d finish")
            execute("rm -rf "+baseApp+"/android/lib/arm64-v8a")
            execute("rm -rf "+baseApp+"/android/lib/x86")
            execute("rm -rf "+baseApp+"/android/lib/armeabi-v7a/libgamecore.so")
            execute("rm -rf "+baseApp+"/android/lib/armeabi/libgamecore.so")
            execute("rm -rf "+baseApp+"/android/lib/armeabi-v7a/gdbserver")
            execute("rm -rf "+baseApp+"/android/lib/armeabi/gdbserver")
            execute("rm -rf "+baseApp+"/android/assets/src")
            execute("rm -rf "+baseApp+"/android/assets/res")
            execute("rm -rf "+baseApp+"/android/assets/cached_res")
            execute("rm -rf "+baseApp+"/android/assets/debug.log")
            execute("rm -rf "+baseApp+"/android/assets/UserDefault.xml")
            execute("rm -rf "+baseApp+"/"+apkName)
        else:
            commandsutils.svnRevertAndUpdate(baseApp+"/android")
        execute("cp -rf  "+baseApp+"/android " + tempdir)
        if os.path.exists(curr+"/lib/"+dev+"/armeabi/libgamecore.so"):
            if os.path.isdir(tempdir+"/android/lib/armeabi"):
                execute("cp -R -f "+curr+"/lib/"+dev+"/armeabi/libgamecore.so "+tempdir+"/android/lib/armeabi/libgamecore.so")
        if os.path.exists(curr+"/lib/"+dev+"/armeabi-v7a/libgamecore.so"):
            if os.path.isdir(tempdir+"/android/lib/armeabi-v7a"):
                execute("cp -R -f "+curr+"/lib/"+dev+"/armeabi-v7a/libgamecore.so "+tempdir+"/android/lib/armeabi-v7a/libgamecore.so")
        execute("rm -rf "+tempdir+"/android/assets/cached_res")
        execute("rm -rf "+tempdir+"/android/assets/res")
        execute("rm -rf "+tempdir+"/android/assets/src")

        if ICON!="":
            DRAWABLEPATHS={
                    "drawable"         : 48,
                    "drawable-ldpi"    : 36,
                    "drawable-mdpi"    : 48,
                    "drawable-hdpi"    : 72,
                    "drawable-xhdpi"   : 96,
                    "drawable-xxhdpi"  : 144,
                    "drawable-xxxhdpi" : 192
            }
            if "FLappVIVO"==app:
                #  您上传的应用“三国群英传-争霸”内置图标含非高清图标 ：
                #  hdpi文件夹图标需变更为192*192
                #  xhdpi文件夹图标需变更为256*256
                #  xxhdpi文件夹图标需变更为384*384
                #  xxxhdpi文件夹图标需变更为512*512
                DRAWABLEPATHS={
                        "drawable"         : 48,
                        "drawable-ldpi"    : 36,
                        "drawable-mdpi"    : 48,
                        "drawable-hdpi"    : 192,
                        "drawable-xhdpi"   : 256,
                        "drawable-xxhdpi"  : 384,
                        "drawable-xxxhdpi" : 512,
                }
            if os.path.exists(tempdir+"/android/res/values/public.xml"):
                replacefile(tempdir+"/android/res/values/public.xml",[
                    [r'<public type="drawable" name="icon" [^>]+/>',""],
                    [r'<public type="mipmap" name="ic_launcher" [^>]+/>',""],
                    [r'<public type="drawable" name="ic_launcher" [^>]+/>',""]])

            img = Image.open("images/"+ICON)
            for key in DRAWABLEPATHS.keys():
                execute("rm -rf "+tempdir+"/android/res/"+key+"/icon.png")
                execute("rm -rf "+tempdir+"/android/res/"+key+"-v4/icon.png")
                execute("rm -rf "+tempdir+"/android/res/"+key+"/fl_icon.png")
                execute("rm -rf "+tempdir+"/android/res/"+key+"-v4/fl_icon.png")
                execute("rm -rf "+tempdir+"/android/res/"+key+"/ic_launcher.png")
                execute("rm -rf "+tempdir+"/android/res/"+key+"-v4/ic_launcher.png")
                execute("rm -rf "+tempdir+"/android/res/"+key+"/"+android_icon+".png")
                execute("rm -rf "+tempdir+"/android/res/"+key+"-v4/"+android_icon+".png")
                if not os.path.exists(tempdir+"/android/res/"+key):
                    os.makedirs(tempdir+"/android/res/"+key)
                out = img.resize((DRAWABLEPATHS[key], DRAWABLEPATHS[key]),Image.ANTIALIAS)
                out.save(tempdir+"/android/res/"+key+"/"+android_icon+".png","PNG")
                print("save fl_icon.png in "+tempdir+"/android/res/"+key)
            if android_icon!="fl_icon":
                execute("cp "+tempdir+"/android/res/drawable/"+android_icon+".png " +tempdir+"/android/res/drawable/fl_icon.png")
        packageName=getpackageName(tempdir+"/android/AndroidManifest.xml")
        # 包名修改后 替换R.java
        if packageName!=BundleID:
            RPath=packageName.replace('.',"/")
            NRPath=BundleID.replace('.',"/")
            if os.path.exists(tempdir+"/android/smali/"+RPath+"/R.smali") and not os.path.exists(tempdir+"/android/smali/"+NRPath+"/R.smali"):
                execute("mkdir -p "+tempdir+"/android/smali/"+NRPath)
                execute("cp -rf "+tempdir+"/android/smali/"+RPath+"/R.smali "+tempdir+"/android/smali/"+NRPath+"/R.smali")
                replacefile(tempdir+"/android/smali/"+NRPath+"/R.smali",[
                    ["L"+RPath+"/R;","L"+NRPath+"/R;"]
                    ])
        if "FLappNicePlayNew2"==app or "FLappNicePlayNew"==app or "FLappNicePlayNew3"==app or "FLappNicePlayNew4"==app:
            replacefile(tempdir+"/android/res/values/strings.xml",[
                [r'<string name="facebook_app_id">554070681466590</string>','<string name="facebook_app_id">'+Facebook_app_id+'</string>'],
                ])
            replacefile(tempdir+"/android/smali/com/kx/androidsdk/Sdk.smali",[
                [r'"MIIBIjANBgkqhkiG9w0BAQEFAA.*"','"'+pubkey+'"'],
                ])
            if APIKEY!="" and "098BC0FF52096E260BE066740679B40C"!=APIKEY:
               replacefile(tempdir+"/android/smali/com/kx/androidsdk/Sdk.smali",[
                [r'"098BC0FF52096E260BE066740679B40C.*"','"'+APIKEY+'"'],
                ]) 
            replacefile(tempdir+"/android/AndroidManifest.xml",[
                [r'com.kx.sgqyz.niceplay',BundleID],
                ])
        if "FLappNicePlayMycard"==app:
            replacefile(tempdir+"/android/AndroidManifest.xml",[
                [r'com.kx.sgqyz.niceplay',BundleID],
                ])
        #替换Manifest
        replacefile(tempdir+"/android/AndroidManifest.xml",[
            [r'android:debuggable="[^"]+"','android:debuggable="'+str(dev=="dev").lower()+'"'],
            [r'android:icon="@drawable/[^"]+"','android:icon="@drawable/'+android_icon+'"'],
            [r'package="[^"]+"','package="'+BundleID+'"'],
            [r'<meta-data android:name="FLGAME_APPID"[^>]+/>','<meta-data android:name="FLGAME_APPID" android:value="'+getConfig(app,"FLGAME_APPID","100008")+'"/>'],
            [r'<meta-data android:name="FLGAME_APPKEY"[^>]+/>','<meta-data android:name="FLGAME_APPKEY" android:value="'+getConfig(app,"FLGAME_APPKEY","368acb818c538e1ac401539da9bf2800000008")+'"/>'],
            [r'<meta-data android:name="FLGAME_APPSECRET"[^>]+/>','<meta-data android:name="FLGAME_APPSECRET" android:value="'+getConfig(app,"FLGAME_APPSECRET","123456")+'"/>'],
            [r'<meta-data android:name="FLGAMESDK_APP_KEY"[^>]+/>','<meta-data android:name="FLGAMESDK_APP_KEY" android:value="'+getConfig(app,"FLGAMESDK_APP_KEY","7980241A-A057-42BF-B27D-E8513C921272")+'"/>'],
            [r'<meta-data android:name="FLGAMESDK_APP_ID"[^>]+/>','<meta-data android:name="FLGAMESDK_APP_ID" android:value="'+getConfig(app,"FLGAMESDK_APP_ID","100287")+'"/>'],
            [r'<meta-data android:name="FLGAMESDK_COMPANY_ID"[^>]+/>','<meta-data android:name="FLGAMESDK_COMPANY_ID" android:value="'+getConfig(app,"FLGAMESDK_COMPANY_ID","100156")+'"/>'],
            [r'<meta-data[^"]+"FLGAMESDK_COOP_ID"[^>]+/>','<meta-data android:name="FLGAMESDK_COOP_ID" android:value="'+getConfig(app,"FLGAMESDK_COOP_ID","300000")+'"/>'],
            # 替换mta 参数
            [r'<meta-data[^"]+"InstallChannel"[^>]+/>','<meta-data android:name="InstallChannel" android:value="'+BundleID+'"/>'],
            # 乐视替换横屏
            [r'<activity android:configChanges="[^"]+" android:label="@string/le_oauth_login_other_account" android:name="com.le.accountoauth.activity.OauthLoginLetvAccountActivity" android:theme="@style/LeOauthNoTitleBarTheme"/>',
             '<activity android:configChanges="keyboardHidden|orientation|screenSize" android:label="@string/le_oauth_login_other_account" android:name="com.le.accountoauth.activity.OauthLoginLetvAccountActivity" android:screenOrientation="landscape" android:theme="@style/LeOauthNoTitleBarTheme"/>'],
            [r'<activity android:configChanges="[^"]+" android:label="@string/le_oauth_title_activity_account_manager" android:name="com.le.accountoauth.activity.AccountManagerActivity" android:screenOrientation="unspecified" android:theme="@android:style/Theme.NoTitleBar.Fullscreen"/>',
             '<activity android:configChanges="keyboardHidden|orientation|screenSize" android:label="@string/le_oauth_title_activity_account_manager" android:name="com.le.accountoauth.activity.AccountManagerActivity" android:screenOrientation="landscape" android:theme="@android:style/Theme.NoTitleBar.Fullscreen"/>'],
            [r'<activity android:configChanges="[^"]+" android:label="@string/le_oauth_title_activity_loading" android:name="com.le.accountoauth.activity.LeLoadingActivity" android:screenOrientation="unspecified" android:theme="@android:style/Theme.NoTitleBar.Fullscreen"/>',
             '<activity android:configChanges="keyboardHidden|orientation|screenSize" android:label="@string/le_oauth_title_activity_loading" android:name="com.le.accountoauth.activity.LeLoadingActivity" android:screenOrientation="landscape" android:theme="@android:style/Theme.NoTitleBar.Fullscreen"/>'],
            [r'<activity android:configChanges="[^"]+" android:label="@string/le_oauth_title_activity_control" android:name="com.le.accountoauth.activity.AccountControlActivity" android:screenOrientation="unspecified" android:theme="@android:style/Theme.NoTitleBar.Fullscreen"/>',
             '<activity android:configChanges="keyboardHidden|orientation|screenSize" android:label="@string/le_oauth_title_activity_control" android:name="com.le.accountoauth.activity.AccountControlActivity" android:screenOrientation="landscape" android:theme="@android:style/Theme.NoTitleBar.Fullscreen"/>'],
            [r'<meta-data android:name="android.app.lib_name" android:value="gamecore"/>','<meta-data android:name="android.app.lib_name" android:value="gamecore"/>\n\t<provider android:name="com.tencent.mid.api.MidProvider" android:authorities="'+BundleID+'" android:exported="true" > </provider>'],
            #niceplay 权限
             # [r'<permission android:name="[^"]+.permission.C2D_MESSAGE"[^>]+/>',
             #   '<permission android:name="'+BundleID+'.permission.C2D_MESSAGE" android:protectionLevel="signature" />'],
             # [r'<uses-permission android:name="[^"]+.permission.C2D_MESSAGE"[^>]+/>',
             #   '<uses-permission android:name="'+BundleID+'.permission.C2D_MESSAGE" />'],
            ]) 
        # 应用宝不能使用闪屏
        if "FLappYYB"==app:
            replacefile(tempdir+"/android/AndroidManifest.xml",[
                [r'<activity[^>]+android:name="org.cocos2dx.lua.AppActivity"[^>]+/>',""],
                ['"org.cocos2dx.lua.SplashActivity"','"org.cocos2dx.lua.AppActivity" android:hardwareAccelerated="true" ']
                ])
        # 替换闪屏
        splashactivity=getConfig(app,"splashactivity","")
        if splashactivity!="":
            replacefile(tempdir+"/android/smali/org/cocos2dx/lua/SplashActivity.smali",[
                ['com/kx/androidsdk/BaseSplashActivity',splashactivity]
                ])
        # 替换 Application
        androidname = getConfig(app,"androidname","")
        if androidname!="":
            replacefile(tempdir+"/android/AndroidManifest.xml",[
                ['android.app.Application',androidname]
                ])

        replacefile(tempdir+"/android/res/values/strings.xml",[
            [r'<string name="app_name">[^<]+</string>','<string name="app_name">'+getConfig(app, "appName","")+'</string>'],
            [r'<string name="app_reporturl">[^<]+</string>','<string name="app_reporturl">'+REPORTURL+'</string>'],
            [r'<string name="facebookappid">[^<]+</string>','<string name="facebookappid">'+Facebook_app_id+'</string>'],
            [r'<string name="facebookapptoken">[^<]+</string>','<string name="facebookapptoken">'+Facebook_app_token+'</string>']
            ])
        versionCode=0
        flag=1000000
        for x in AppVersion.split("."):
            versionCode=versionCode+int(x)*flag
            flag=flag/1000

        print("replace apktool.yml AppVersion: "+AppVersion)
        replacefile(tempdir+"/android/apktool.yml",[
            [r"versionCode: '[\d]+'","versionCode: '"+str(versionCode)+"'"],
            [r"versionName: [\d|\.]+","versionName: "+AppVersion]])
        print("替换后的  apktool.yml 内容")
        print("替换版本号:" + "versionCode: '"+str(versionCode)+"'")


        print("android apktool.yml  path " + tempdir+"/android/apktool.yml")
        f = open(tempdir+"/android/apktool.yml","r")  
        lines = f.readlines()#读取全部内容  
        for line in lines:  
            print(line) 

        if not os.path.exists(tempdir+"/android/assets"):
            os.makedirs(tempdir+"/android/assets")
        copyressrc(tempdir + '/android/assets/',AppVersion)
        execute("rm -rf "+tempdir+"/android/assets/res/framework64.zip")
        copySplash(tempdir+"/android/assets/res/",app,platform)
        execute("rm -rf "+tempdir+'/android/assets/res/script/base/packageDefine.lua')
        execute("cp -rf "+curr+"/packageDefine.lua " +tempdir + "/android/assets/res/script/base/packageDefine.lua")
        replacefilePackageDefine(platform,tempdir+"/android/assets/res/script/base/packageDefine.lua",conf,app,dev)
        cached_res_path = ""
        if cachedRes_from_revision != "":
            print('updating CachedResFrom revision :'+cachedRes_from_revision)
            cached_res_path=updateCachedResFromSpecificREV(cachedRes_from_revision)
            shutil.copytree(cached_res_path+"/cached_res",tempdir+"/android/assets/cached_res")
            shutil.copytree(cached_res_path+"/cached_res64",tempdir+"/android/assets/cached_res64")
            replacefile(tempdir+"/android/assets/res/script/base/packageDefine.lua",[
                    ["0.0.0.0",resVersion]
                    ])
        elif local_cachedRes_path!="":
            print('updating CachedResFrom local :'+local_cachedRes_path)
            cached_res_path=updateCachedResFromLocalFile(local_cachedRes_path)
            shutil.copytree(cached_res_path+"/cached_res",tempdir+"/android/assets/cached_res")
            shutil.copytree(cached_res_path+"/cached_res64",tempdir+"/android/assets/cached_res64")
            replacefile(tempdir+"/android/assets/res/script/base/packageDefine.lua",[
                    ["0.0.0.0",resVersion]
                    ])
        elif cachedRes_from_archive != "":
            print('updating CachedRes From apk:'+cachedRes_from_archive)
            cached_res_path=updateCachedResFromArchive(cachedRes_from_archive,"assets")
            shutil.copytree(cached_res_path+"/cached_res",tempdir+"/sgqygame.app/cached_res")
            replacefile(tempdir+"/sgqygame.app/res/script/base/packageDefine.lua",[
                    ["0.0.0.0",resVersion]
                    ])
        else:
            if os.path.isdir(SVN_TAG+"/cached_res"):
                if not os.path.exists(tempdir+"/android/assets/cached_res"):
                    os.makedirs(tempdir+"/android/assets/cached_res")
                print('updating CachedRes from SVN tag:'+SVN_TAG)
                cached_res_path=updateCachedResFromSVN(SVN_TAG,tempdir,filename)
                print("cached_res_path path :"+cached_res_path)
                print("tempdir path :"+tempdir)
                shutil.copytree(cached_res_path+"/cached_res/config",tempdir+"/android/assets/cached_res/config")
                shutil.copytree(cached_res_path+"/cached_res/image",tempdir+"/android/assets/cached_res/image")
                execute("cp -rf "+tempdir+"/android/assets/cached_res/image/"+localeType.replace("_","-")+"/* "+tempdir+"/android/assets/cached_res/image/")
                execute("cp -rf "+tempdir+"/android/assets/cached_res/config/"+localeType.replace("_","-")+"/* "+tempdir+"/android/assets/cached_res/config/")
                execute("rm -rf "+tempdir+"/android/assets/cached_res/image/*-*")
                execute("rm -rf "+tempdir+"/android/assets/cached_res/config/*-*")
                shutil.copytree(cached_res_path+"/cached_res/script",tempdir+"/android/assets/cached_res/script")
                if localeType!="zh_CN":
                    shutil.copy(cached_res_path+"/cached_res/md5"+localeType+".txt",tempdir+"/android/assets/cached_res/md5.txt")
                else:
                    shutil.copy(cached_res_path+"/cached_res/md5.txt",tempdir+"/android/assets/cached_res/md5.txt")
                UpDateTipS =localeType.split("_")[1].lower()
                execute("mv "+tempdir+"/android/assets/cached_res/script/base/UpDateTipS_"+UpDateTipS+".lua "+tempdir+"/android/assets/cached_res/script/base/UpDateTipS.lua")
                execute("rm -rf "+tempdir+"/android/assets/cached_res/script/base/UpDateTipS_*")
                checkFileSizeLimit(tempdir+"/android/assets",localeType.replace("_","-"),resVersion,int(getConfig(app,"sizelimit","0")))
            
        changeLogo(tempdir+"/android/assets/",app)
        localizationfile(tempdir+"/android/assets/res/script/update",localeType)
        quickReleaseToWeb.compileLuasScripts(tempdir+"/android/assets/res/script",tempdir+"/android/assets/res/script","32" )
        quickReleaseToWeb.compileLuasScripts(tempdir+"/android/assets/src",tempdir+"/android/assets/src","32" )
        removeRepeat(tempdir+"/android/assets")
        addFont(tempdir+"/android/assets",app)
        tmpdir = None
        # if "FLappYiJie"==app:
        #     tmpdir = tempfile.gettempdir()
        #     execute("mv "+tempdir+"/android/assets/cached_res "+tmpdir)
        #     execute("mv "+tempdir+"/android/assets/res "+tmpdir)
        #     execute("mv "+tempdir+"/android/assets/src "+tmpdir)
        execute("apktool b "+tempdir+"/android -o "+tempdir+"/android.apk")
        keystore     = getConfig(app,"keystore","qunying_123456.keystore")
        storepass    = getConfig(app,"storepass","123456")
        keystorename = getConfig(app,"keystorename","qunying")
        if "FLappDangLe"==app:
            execute("jarsigner -verbose -digestalg SHA1 -sigalg MD5withRSA -keystore "+curr+"/p12/downjoy_253_ohBPHNQVjg5XL1Z.keystore -storepass downjoy_253 -signedjar "+tempdir+"/android_sing.apk "+tempdir+"/android.apk 253")
        else:
            execute("jarsigner -verbose -digestalg SHA1 -sigalg MD5withRSA -keystore "+curr+"/p12/"+keystore+" -storepass "+storepass+" -signedjar "+tempdir+"/android_sing.apk "+tempdir+"/android.apk "+keystorename)
        execute("`for zipalign in $(find $ANDROID_SDK_ROOT/build-tools -type f | grep zipalign);do set i=zipalign; done; echo $zipalign`"+" -f -v 4 "+tempdir+"/android_sing.apk "+tempdir+"/android.apk")
        # execute("cp -rf "+tempdir+"/android.apk "+curr+"/app/"+app+"_"+BundleID+"_"+AppVersion+"_"+filename+"_"+dev+".apk ")
        copyToWeb(tempdir+"/android.apk",app+"_"+BundleID+"_"+AppVersion+"_"+filename+"_"+dev+'.apk',app+"_"+BundleID+"_"+AppVersion)
        # if "FLappYiJie"==app:
        #     execute("tar -cf "+tmpdir+"/yijie_game_assets_res.tar "+tmpdir+"/cached_res "+tmpdir+"/res "+tmpdir+"/src")
        #     copyToWeb(tmpdir+"/yijie_game_assets_res.tar",app+"_"+BundleID+"_"+AppVersion+"_"+filename+"_"+dev+'_yijie_game_assets_res.tar',app+"_"+BundleID+"_"+AppVersion)


    
# 编译工程
def xcodeArchive(sdk):
    execute("rm -rf /Volumes/RamDisk/temp/*")
    execute("rm -rf /Volumes/RamDisk/temp/sgqyz.xcarchive")
    userHome = os.path.expanduser('~')
    curr = os.getcwd()
    iosprojPath=userHome+"/work/qunying/client/trunk/runtime-src/proj.ios_mac/"
    commandsutils.svnRevertAndUpdate(iosprojPath)
    execute("cd "+curr+"/appstore && svn up ")
    targetPath=curr+"/appstore"
    maps = AndroidProjConf.getConf()
    if maps.has_key(sdk):
        targetPath=curr+maps[sdk]
    else:
        pirnt("no set %s in AndroidProjConf.py" %(sdk))
        return
    replacefile(iosprojPath+sdk+"/project.pbxproj",[
        [
            r'PRODUCT_BUNDLE_IDENTIFIER = [^;]+',
            "PRODUCT_BUNDLE_IDENTIFIER = com.kx.sgqyz"
        ],
        [
            r'PROVISIONING_PROFILE = [^;]+',
            'PROVISIONING_PROFILE = "f9bfc7c0-c78f-469b-83e1-c150925a0533"'
        ],
        [
            r'PROVISIONING_PROFILE_SPECIFIER = [^;]+',
            'PROVISIONING_PROFILE_SPECIFIER = sg_dis'
        ],
        [
            r'DevelopmentTeam = [^;]+',
            'DevelopmentTeam = K98J7D6A5Z'
        ],
        [
            r'DEVELOPMENT_TEAM = [^;]+',
            'DEVELOPMENT_TEAM = K98J7D6A5Z'
        ]

    ])
    info = execute("/usr/bin/security unlock-keychain -p mengjie ~/Library/Keychains/login.keychain && xcodebuild -project ~/work/qunying/client/trunk/runtime-src/proj.ios_mac/"+sdk+" -scheme sgqygame archive -archivePath /Volumes/RamDisk/temp/sgqyz.xcarchive PRODUCT_BUNDLE_IDENTIFIER=com.kx.sgqyz CODE_SIGN_IDENTITY='iPhone Distribution: Feiliu Game (Chengdu) Tech. Co., Ltd. (K98J7D6A5Z)' PROVISIONING_PROFILE='f9bfc7c0-c78f-469b-83e1-c150925a0533'")
    if not os.path.exists("/Volumes/RamDisk/temp/sgqyz.xcarchive/Products/Applications/sgqygame.app"):
        print info
        return
    if os.path.exists(targetPath+"/sgqygame.app"):
        execute("rm -rf "+targetPath+"/sgqygame.app/sgqygame")
        execute("rm -rf "+targetPath+"/sgqygame.app/FLGamePlatform_Resources.bundle")
        execute("mv /Volumes/RamDisk/temp/sgqyz.xcarchive/Products/Applications/sgqygame.app/sgqygame "+targetPath+"/sgqygame.app/sgqygame")
        execute("mv /Volumes/RamDisk/temp/sgqyz.xcarchive/Products/Applications/sgqygame.app/FLGamePlatform_Resources.bundle "+targetPath+"/sgqygame.app/FLGamePlatform_Resources.bundle")
        execute("cp -rf /Volumes/RamDisk/temp/sgqyz.xcarchive/Products/Applications/sgqygame.app/*.bundle "+targetPath+"/sgqygame.app/")
    else:
        execute("mv /Volumes/RamDisk/temp/sgqyz.xcarchive/Products/Applications/sgqygame.app "+targetPath+"/")
    # 备份 dSYM
    execute("cd /Volumes/RamDisk/temp/sgqyz.xcarchive/dSYMs/ && zip -r sgqygame.app.dSYM.zip ./sgqygame.app.dSYM")
    execute('curl -k "https://api.bugly.qq.com/openapi/file/upload/symbol?app_key=f7371105-60da-4b6f-9468-ad538ae3277d&app_id=238b13540b" --form "api_version=1" --form "app_id=238b13540b" --form "app_key=f7371105-60da-4b6f-9468-ad538ae3277d" --form "symbolType=2"  --form "bundleId=com.kx.sgqyz" --form "productVersion='+filename+'" --form "channel=ios" --form "fileName=sgqygame.'+filename+'.app.dSYM.zip" --form "file=@/Volumes/RamDisk/temp/sgqyz.xcarchive/dSYMs/sgqygame.app.dSYM.zip"')
    execute("mv /Volumes/RamDisk/temp/sgqyz.xcarchive/dSYMs/sgqygame.app.dSYM.zip "+targetPath+"/sgqygame."+filename+".app.dSYM.zip")
    commandsutils.setPlist(targetPath+"/sgqygame.app/Info.plist",{"buildtimestamp":filename})
    execute("rm -rf /Volumes/RamDisk/temp/*")
    commandsutils.svnCommit(targetPath)

def preCompile(cmd):
    execute(cmd)

def postCompile(cmd):
    execute(cmd)

def androidArchive(sdk,preCompileCMD="",postCompileCMD=""):
    userHome = os.path.expanduser('~')
    curr = os.getcwd()
    androidprojPath=userHome+"/work/qunying/client/trunk/runtime-src/proj.android_sdk/"
    execute("svn up "+userHome+"/work/qunying/client/trunk/runtime-src/")
    execute("svn up "+userHome+"/work/qunying/client/trunk/cocos2d-x/cocos/platform/android/java/")
    execute("svn revert "+androidprojPath+"AndroidManifest.xml")
    execute("svn revert "+androidprojPath+"project.properties")
    execute("cd "+curr+"/android &&  svn up ")
    execute("cd "+androidprojPath+"../androidsdks/"+sdk+" && svn revert --depth infinity . && svn up ")
    preCompile(preCompileCMD)
    #切换引用sdk工程
    replacefile(androidprojPath+"project.properties",[
        [
            r'android.library.reference.2=[^"]+',
            "android.library.reference.2=../androidsdks/"+sdk
            ]
        ])
    #替换assets目录
    execute("mkdir -p "+androidprojPath+"assets")
    execute("rm -fr "+androidprojPath+"assets/*")
    if os.path.isdir(androidprojPath+"../androidsdks/"+sdk+"/assets"):
        execute("cp -fr "+androidprojPath+"../androidsdks/"+sdk+"/assets/* "+androidprojPath+"assets/")
    # 检查build.xml 是否存在 
    if not os.path.exists(androidprojPath+"../androidsdks/"+sdk+"/build.xml"):
        execute("${ANDROID_SDK_ROOT}/tools/android  update project --subprojects --path "+androidprojPath+"../androidsdks/"+sdk)
    #替换AndroidManifest.xml文件
    srcXMLPath = androidprojPath+"../androidsdks/"+sdk+"/AndroidManifest.xml"
    targetXMLPath = androidprojPath+"AndroidManifest.xml"
    execute("cp "+srcXMLPath+" "+targetXMLPath)
    # compile
    #  os.chdir(androidprojPath)
    print("(cd "+androidprojPath+";ant clean release -Dsdk.dir=$ANDROID_SDK_ROOT -Dkey.store.password=123456 -Dkey.alias.password=123456 -Dkey.store="+curr+"/p12/qunying_123456.keystore -Dkey.alias=qunying)")
    if "9s_SDK" == sdk:
        replacefile(androidprojPath+"/AndroidManifest.xml",[
                [r'<permission android:name="com.kx.sgqyz.niceplay.permission.C2D_MESSAGE" android:protectionLevel="signature" />',''],
                ])
    output = commands.getoutput("(cd "+androidprojPath+";ant clean release  -Dsdk.dir=$ANDROID_SDK_ROOT -Dkey.store.password=123456 -Dkey.alias.password=123456 -Dkey.store="+curr+"/p12/qunying_123456.keystore -Dkey.alias=qunying)")
    while output.find("BUILD FAILED")>-1:
        r1     = re.compile(r'Invalid file:[^.]+.xml')
        result = r1.search(output)
        if result:
            result = result.group(0).replace("Invalid file:","")
            if result.find("build.xml")>-1:
                result=result.replace("build.xml","").strip()
                execute("${ANDROID_SDK_ROOT}/tools/android  update project --subprojects --path "+result)
            output = commands.getoutput("(cd "+androidprojPath+";ant clean release  -Dsdk.dir=$ANDROID_SDK_ROOT -Dkey.store.password=123456 -Dkey.alias.password=123456 -Dkey.store="+curr+"/p12/qunying_123456.keystore -Dkey.alias=qunying)")
        else:
            print output
            return
    postCompile(postCompileCMD)
    if "BUILD FAILED" in output:
        print("BUILD FAILED")
        return
    #  execute("(cd "+androidprojPath+";ant clean release -Dsdk.dir=$ANDROID_SDK_ROOT -Dkey.store.password=123456 -Dkey.alias.password=123456 -Dkey.store="+curr+"/p12/qunying_123456.keystore -Dkey.alias=qunying)")
    maps = AndroidProjConf.getConf()

    if maps.get(sdk):
        apktoolOutput = curr+maps[sdk]
    else:
        apktoolOutput =  curr+"/android/"+sdk+"/android" 
    if not os.path.exists(apktoolOutput):
        execute("mkdir -p "+apktoolOutput)
    # 自动提交svn 
    execute("cd "+apktoolOutput+" && svn up ")
    execute("apktool d -b -f "+androidprojPath+"bin/quickgame-release.apk -o "+apktoolOutput)
    if "9s_SDK" == sdk:
        replacefile(apktoolOutput+"/AndroidManifest.xml",[
                [r'<uses-permission android:name="com.kx.sgqyz.niceplay.permission.C2D_MESSAGE"/>','<permission android:name="com.kx.sgqyz.niceplay.permission.C2D_MESSAGE" android:protectionLevel="signature" />\r\n\t<uses-permission android:name="com.kx.sgqyz.niceplay.permission.C2D_MESSAGE"/>'],
                ])
    # 删除 libgamecore
    execute("rm -rf %s/lib/armeabi/libgamecore.so" %(apktoolOutput))
    execute("rm -rf %s/lib/armeabi-v7a/libgamecore.so" %(apktoolOutput))
    # 删除 mips arm64 x86 arm64-v8a mips64 x86_64
    for arm in ["mips" ,"x86","arm64", "arm64-v8a", "mips64","x86_64"]:
        execute("rm -rf %s/lib/%s" %(apktoolOutput,arm))
    # so文件数量不一致 保留最多的文件
    listarmeabi=os.listdir("%s/lib/armeabi" %(apktoolOutput))
    listarmeabiv7a=os.listdir("%s/lib/armeabi-v7a" %(apktoolOutput))
    if len(listarmeabi)!= len(listarmeabiv7a):
        if len(listarmeabi)<len(listarmeabiv7a):
            execute("svn del %s/lib/armeabi --force" %(apktoolOutput))
        else:
            execute("svn del %s/lib/armeabi-v7a --force" %(apktoolOutput))
    execute("cd "+apktoolOutput+" && svn st | grep '^\!' | tr '^\!' ' ' | sed 's/[ ]*//' | sed 's/[ ]/\\ /g' | xargs svn del")
    execute("cd "+apktoolOutput+" && svn st | grep '^\?' | tr '^\?' ' ' | sed 's/[ ]*//' | sed 's/[ ]/\\ /g' | xargs svn add")
    # 删除 libgamecore 打包的时候复制过来
    execute("cd "+apktoolOutput+" && svn del lib/armeabi/libgamecore.so --force")
    execute("cd "+apktoolOutput+" && svn del lib/armeabi-v7a/libgamecore.so --force")
    
    # svn 默认不添加so文件 
    execute("cd "+apktoolOutput+" && svn add lib/armeabi/*.so")
    execute("cd "+apktoolOutput+" && svn add lib/armeabi-v7a/*.so")

    execute("cd "+apktoolOutput+" && svn commit -m 'auto commit by apktool' ")
