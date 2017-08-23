#!/usr/bin/python
# -*- coding: utf-8 -*-
import ConfigParser
import os,sys
import shutil
import time
import generateappcore
import commandsutils
import signal
import sendmail
import functools

def postWX(func):
    def wrapper(*args,**kw):
        func(*args,**kw)
    return wrapper
    
def postEmail():
    def wrapper(*args,**kw):
        func(*args,**kw)
    return wrapper

def generateAppThenPostWX(app,dev,wx_recivers):
    generateApp(app,dev)
    if emailrecivers != "":
        latest_pack_file = '/Users/mengjie/work/webtoos/cgi-bin/latest_pack_path.txt'
        f = open(latest_pack_file,'r')
        path = f.readline()
        path = path.strip()
        f.close()
        if os.path.exists(path):
            path = path.replace("/Users/mengjie/www/app","10.8.3.40:8000")
            sendmail.send("http://"+path,emailrecivers)
        else:
            print(path+' not exists')

def generateAppThenEmail(app,dev,emailrecivers):
    generateApp(app,dev)
    if emailrecivers != "":
        latest_pack_file = '/Users/mengjie/work/webtoos/cgi-bin/latest_pack_path.txt'
        f = open(latest_pack_file,'r')
        path = f.readline()
        path = path.strip()
        f.close()
        if os.path.exists(path):
            path = path.replace("/Users/mengjie/www","10.8.4.38/app")
            sendmail.send("http://"+path,emailrecivers)
        else:
            print(path+' not exists')

def generateApp(app,dev,platform=""):

    conf = ConfigParser.ConfigParser()
    conf.read("generateapp.conf")

    pidfilename = '/tmp/generateApp.pid'
    if os.path.isfile(pidfilename):
        print("generating App!!! please wait")
        return
    pid = os.getpid()
    pidfile = open(pidfilename,'w')
    pidfile.write(str(pid))
    pidfile.close()

    def signal_handler(signal,frame):
        print('capture signal SIGINT')
        os.remove(pidfilename)
        exit(0)
        pass
    signal.signal(signal.SIGINT,signal_handler)
    devs = dev.split("|")
    for dv in devs:
        generateappcore.generateApp(conf,app,dv,platform)
    print("finish generateApp")
    os.remove(pidfilename)
    commandsutils.execCmd("rm -rf /Volumes/RamDisk/generateApp/")
    
def androidArchive(sdkname,precmd="",postcmd=""):
    generateappcore.androidArchive(sdkname,precmd,postcmd)
    
def xcodeArchive(sdkname,precmd="",postcmd=""):
    generateappcore.xcodeArchive(sdkname)
if __name__ == '__main__':
    begin = time.time()
    #  conf = ConfigParser.ConfigParser()
    #  conf.read("generateapp.conf")
    #  secs = conf.sections()
    #  curr = os.getcwd()
    #  tempdir="/tmp/generateApp"
    #  if os.path.exists("/Volumes/RamDisk/"):
        #  tempdir="/Volumes/RamDisk/generateApp"
    #  shutil.rmtree(tempdir)
    if len(sys.argv) != 1:
        print sys.argv
        #  generateApp(sys.argv[1],'dev')
        generateApp(sys.argv[1],sys.argv[2])
        end = time.time()
        print("总耗时:"+str(end-begin))
        exit(0)
    # 编译ios 工程
    #  generateappcore.xcodeArchive("sgqygame_anysdk-500020")
    # 编译android 魅族 SDK 母包
    #  androidArchive("meizuSDK")
    # 编译android oppo SDK 母包
    #  androidArchive("oppoSDK")
    # 编译android 游戏多 SDK 母包
    #  androidArchive("youxiduoSdk")
    # 编译android 易接 SDK 母包
    #  androidArchive("yijieSDK")
    # 编译android 快用 SDK 母包
    #  androidArchive("kuaiyongSDK")
    # 编译android 飞流SDK 母包
    #  androidArchive("feiliusdk")
    # 编译android AnySdk 母包
    #  androidArchive("libAnySDK")
    # 三国群英传风云再起
    #  userHome = os.path.expanduser('~')
    #  androidArchive("haimaSDK","","")

    #  androidArchive("haimaSDK","mv
            #  "+userHome+"/work/qunying/client/trunk/runtime-src/androidsdks/haima_appcompat-v7-23.4.0/libs/support-v4.jar
            #  "+userHome+"/work/qunying/client/trunk/runtime-src/androidsdks/basesdk/libs","")

    # generateApp("FYZQapp","dev")
    # 飞流母包
    #  generateApp("FLapp","dev")
    #  generateApp("FLapp","dis")
    # 长尾
    #  generateApp("FLappYiJie","dev")
    #  generateApp("FLappYiJie","dis")

    # generateApp("FLappBaidu","dev")
    #  generateApp("FLappBaidu","dis")


    # 评审包
    # generateApp("PJapp","dev")

    # UC
    #  generateApp("FLappUC","dev")
    #  generateApp("FLappUC","dis")
    # 华为
    #  generateApp("FLappHuaWei","dev")
    #  generateApp("FLappHuaWei","dis")
    # 小米
    #  generateApp("FLappXiaoMi","dev")
    #  generateApp("FLappXiaoMi","dis")
    #应用宝
    #  generateApp("appmstk","dev")
    #  generateApp("appmstk","dis")
    # 360
    #  generateApp("FLapp360","dev")
    #  generateApp("FLapp360","dis")
    # oppo
    #  generateApp("FLappOPPO","dev")
    #  generateApp("FLappOPPO","dis")
    # 魅族
    #  generateApp("FLappMeizu","dev")
    #  generateApp("FLappMeizu","dis")
    #当乐
    #  generateApp("FLappDangLe","dev")
    #  generateApp("FLappDangLe","dis")
    #啪啪
    #  androidArchive("papaSDK")
    #  generateApp("FLappPapa","dev")
    #  generateApp("FLappPapa","dis")
    #安智
    #  generateApp("FLappAnZhi","dev")
    #  generateApp("FLappAnZhi","dis")
    #朋友玩
    #  generateApp("FLappPYW","dev")
    #  generateApp("FLappPYW","dis")
    # 果盘
    #  generateApp("FLappGuoPan","dev")
    #  generateApp("FLappGuoPan","dis")
    #  #海马
    #  generateApp("FLappHM","dev")
    #  generateApp("FLappHM","dis")
    #豌豆荚
    #  generateApp("FLappWDJ","dev")
    #  generateApp("FLappWDJ","dis")
    #乐视手机
    #  generateApp("FLappLeShiPhone","dev")
    #  generateApp("FLappLeShiPhone","dis")
    # 快用
    #  generateApp("FLappKuaiYong","dev")
    #  generateApp("FLappKuaiYong","dis")
    # XY 助手 ios
    #  generateApp("FLappXY","dev")
    #  generateApp("FLappXY","dis")

    #  generateApp("FLappSM_iOS","adhoc")

    #  # 爱思ios
    #  generateApp("FLappi4","dev")
    #  generateApp("FLappi4","dis")

    #  # 海马ios
    #  generateApp("ios_haima","dev")
    #  generateApp("ios_haima","dis")

    # 三国群英7
    #  generateApp("app2","dev","android")
    #  generateApp("app2","dev","ios")

    #  generateApp("inhousezq9","dev","android")
    #  generateApp("inhousezq9","dev","ios")

    # 三国群英7 1.3.0
    # generateApp("app130","dev")
    # generateApp("app130","dev")

    # 飞流测试
    # generateApp("FLtestappstore","dev")
    # generateApp("app8","dev")

    #  generateApp("appTW","dis")

    #  generateApp("appTW_IOS","dev")
    #  generateApp("appTW_IOS","dis")

    #  generateApp("appTW_IOS_new3","dev")
    #  generateApp("appTW_IOS_new3","dis")

    #  generateApp("appTW_IOS1.0.3","dev")
    #  generateApp("appTW_IOS1.0.3","dis")
    #  generateApp("appTW_IOS1.0.4","dev")
    #  generateApp("appTW_IOS1.0.4","dis")

    # ios 提审包 测试 1.0.0
    #  generateApp("testappstore","dev")

    # ios 提审包 1.1.1
    # generateApp("app7","dev")
    # generateApp("app7","dis")

    # ios 提审包 1.2.0
    # generateApp("appstore1.2.0","dis")
    # generateApp("appstore1.2.0","dev")

    # ios 提审包 1.2.2
    # generateApp("appstore1.2.2","dis")
    # generateApp("appstore1.2.2","dev")

    # ios 提审包 1.3.0
    #  generateApp("appstore1.3.0","dev")

    # ios 提审包 1.4.0
    #  generateApp("appstore1.4.0","dev")
    #  generateApp("appstore1.4.0","dis")
    # ios 提审包 1.5.0
    #  generateApp("appstore1.5.0","dev")
    #  generateApp("appstore1.5.0","dis")
    # ios 提审包 1.6.2
    #  generateApp("appstore1.6","dev")
    #  generateApp("appstore1.6","dis")

    # 三分天下
    #  generateApp("sgqyz_sftx","dev")
    #  generateApp("sgqyz_sftx","dis")

    #  androidArchive("samsung")
    #  generateApp("FLappSamsung","dev")
    #  generateApp("FLappSamsung","dis")

    #  androidArchive("oppoSDK")
    #  generateApp("FLappOPPO","dis")

    #  androidArchive("meizuSDK")
    #  generateApp("FLappMeizuCS","dis")
    #  generateApp("FLappMeizu","dis")

    #  androidArchive("vivoSdk")
    #  generateApp("FLappVIVO","dis")

    #  androidArchive("9s_SDK")
    #  generateApp("FLappNicePlay","dis")
    #  generateApp("FLappNicePlay","dev")
    #  generateApp("FLappNicePlayTEST","dis")
    #  generateApp("FLappNicePlayTEST","dev")

    #  generateApp("FLappNicePlayNew","dis")
    #  generateApp("FLappNicePlayNew","dev")
    #  generateApp("FLappNicePlayNew2","dis")
    #  generateApp("FLappNicePlayNew2","dev")
    #  generateApp("FLappNicePlayNew3","dis")
    #  generateApp("FLappNicePlayNew3","dev")
    #  generateApp("FLappNicePlayNew4","dis")
    #  generateApp("FLappNicePlayNew4","dev")
    #  generateApp("FLappASQY_baozou_ios","dev")
    #  generateApp("FLappNicePlayMycard","dis")
    #  generateApp("FLappNicePlayMycard","dev")

    # android test
    #  generateApp("ANDROID_TEST","dev")

    #  androidArchive("heyshellsdk")
    # android 英文版本
    #  generateApp("app2en_us_test","dev")
    #  generateApp("app2en_us_test","dis")
    #  generateApp("app2en_us","dev")
    #  generateApp("app2en_us","dis")
    #  generateApp("app2en_us_new","dev")
    #  generateApp("app2en_us_3","dev")
    #  generateApp("app2en_us_3","dis")

    # ios 英文版本
    #  generateApp("app_en_US_iOS","dev")
    #  generateApp("app_en_US_iOS","dis")
    #ios 韩文版本
    #  generateApp("app_ko_kr_iOS","dev")
    #  generateApp("app_ko_kr_iOS","dis")
    #ios 中文简体版本
    #  generateApp("app2jt_us_cn","dev")
    #  generateApp("app2jt_us_cn","dis")
    #ios 中文繁体版本
    #  generateApp("app2ft_us_cn","dev")
    #  generateApp("app2ft_us_cn","dis")

    #android 日文版本
    #  generateApp("app_jp_google","dev")
    #  generateApp("app_jp_google","dis")

    #  generateApp("app_vn_google","dis")
    #android 韩文版本
    #  generateApp("app2ko_kr","dev")
    #  generateApp("app2ko_kr","dis")

    #  generateApp("app2en_us_cn","dev")
    #  generateApp("app2en_us_cn","dis")
    #  generateApp("app2en_us_tw","dev")
    #  generateApp("app2en_us_tw","dis")

    #  generateApp("app2ko_kr_onestore","dev")
    #  generateApp("app2ko_kr_onestore","dis")

    # QA专用
    # 1.5
    #  generateApp("testappstoreming_ios15","dev")
    #  generateApp("testappstoreming_android15","dev")
    # 1.6
    #  generateApp("testappstoreming_ios16","dev")
    #  generateApp("testappstoreming_android16","dev")
    # 1.7
    #  generateApp("testappstoreming_android17","dev")

    end = time.time()
    print("总耗时:"+str(end-begin))
    exit(0)
