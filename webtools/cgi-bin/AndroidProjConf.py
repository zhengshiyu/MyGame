#!/usr/bin/env python
# -*- coding: utf-8 -*-

maps={
    "feiliusdk"           : "/appstore/android", #这个是飞流母包
    "feiliusdk_withReyun" : "/android/feiliusdk_withReyun/android",
    "kuaiyongSDK"         : "/android/快用/android",
    "youxiduoSdk"         : "/android/游戏多/android",
    "yijieSDK"            : "/android/长尾/android",
    "meizuSDK"            : "/android/魅族/android",
    "oppoSDK"             : "/android/oppo/android",
    "vivoSdk"             : "/android/vivo/android",
    "9s_SDK"              : "/android/niceplay/android",
    "libAnySDK"           : "/android/anysdk/android",
    "heyshellsdk"         : "/android/heyshell/android",
    "samsung"             : "/android/samsung/android",
    "papaSDK"             : "/android/啪啪游戏厅/android",
    "pywSDK"              : "/android/朋友玩/android",
    "anzhiSDK"            : "/android/anzhi/android",
    "dangleSDK"           : "/android/当乐/android",
    "ucSDK"               : "/android/UC/android",
    "guopanSDK"           : "/android/guopan/android",
    "pywSDK"              : "/android/朋友玩/android",
    "huaWei_SDK"          : "/android/华为游戏中心/android",
    "xiaomiSDK"           : "/android/小米应用商店/android",
    "360SDK"              : "/android/360手机助手/android",
    "leshiSDK"            : "/android/乐视手机/android",
    "haimaSDK"            : "/android/海马/android",
    "SMSDK"               : "/android/SM/android",
    "57KSDK"              : "/android/57K/android",
    "YSDK"                : "/android/ysdk/android",
    "baiduSDK"            : "/android/baidu/android",
    "feiliu_SDK"          : "/android/feiliu/android", #这个是后来转给我们接入的飞流sdk
    "lenovoSDK"           : "/android/lenovo/android", 
    "coolpadSDK"          : "/android/coolpad/android", 
    "jinliSDK"            : "/android/jinli/android", 
    "shengzeSDK"          : "/android/shengze/android", 
    "baozouSDK"           : "/android/baozou/android",
    "179appSDK"           : "/android/179app/android",
    "opponewSDK"          : "/android/opponew/android",
    #ios 
    "sgqygame_feiliuSDK.xcodeproj"   : "/appstore",
    "sgqygame_haimaSDK.xcodeproj"    : "/appstore/ios/haima",
    "sgqygame_i4SDK.xcodeproj"       : "/appstore/ios/i4",
    "sgqygame_xySDK.xcodeproj"       : "/appstore/ios/xy",
    "sgqygame_feidouSDK.xcodeproj"   : "/appstore/ios/english",
    "sgqygame_niceplay.xcodeproj"    : "/appstore/ios/niceplay",
    "sgqygame_SMSDK.xcodeproj"       : "/appstore/ios/sm",
    "sgqygame_baozouSDK.xcodeproj"   : "/android/baozou"
}

def getConf():
    global maps
    return maps
