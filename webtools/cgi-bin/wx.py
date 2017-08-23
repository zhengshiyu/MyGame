#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from wxpy import *
import os
import subprocess
import base64
import time
import configparser

def qr_callback(uuid,status,qrcode):
    return
def login_callback():
    print("login_callback")
    return
def logout_callback():
    print("logout_callback")
    return

def parsePackCmdFromWXMsg(conf,msg):
    cmd = msg.text
    splited = cmd.split(" ")
    if cmd == splited:
        return cmd
    if len(splited) != 3:
        return cmd
    if splited[0] == "pack":
        appName = splited[1]
        dev = splited[2]
        if conf[appName]:
            return "python generateApp.py "+appName+" "+dev
    return cmd

    
def initBot():

    conf = configparser.ConfigParser()
    conf.read("generateApp.conf")

    qr_path = os.getcwd()
    bot_cache_path = os.getcwd()
    bot = Bot(bot_cache_path+"/../bot.pkl",False,qr_path+"/../wx.png",None,login_callback,logout_callback)
    friends = bot.friends()
    imbahom = friends.search("imbahom")

    @bot.register(imbahom)
    def print_msg(msg):
        cmd = parsePackCmdFromWXMsg(conf,msg)
        exec_re = subprocess.getoutput(cmd)
        if cmd == msg.text:
            imbahom[0].send(exec_re)
        else:
            with open("latest_pack_path.txt","r") as f:
                path = f.readline()
                path = path.strip()
                if os.path.exists(path):
                    path = path.replace("/Users/mengjie/www/app","10.8.3.40:8000")
                    imbahom[0].send(path)
                else:
                    imbahom[0].send('file not exist')
            
        #  try:
            #  bot.file_helper.send(exec_re)
        #  except Exception as e:
            #  bot.file_helper.send(base64.b64encode(exec_re.encode()))
        
    embed()

if __name__ == "__main__":
    initBot()
