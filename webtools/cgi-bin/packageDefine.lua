if not packageDefine then
IS_DOWNLOAD_PACKAGE=true
USEDSDK = _USEDSDK_
PAYOPEN=_PAYOPEN_
HOSTS={
	"_SERVERLIST_"
}
HOST = HOSTS[1]
gamecode = "sgqyz"
AppVersion = "0.0.3"
APPResVersion = "0.0.0.0"
BundleID = "com.igame.sgqyz"
AreaId = "1"
FVALUE="_Fvalue_"
MTACHANNEL="_MTACHANNEL_"
MTAAPPKEY="_MTAAPPKEY_"
SPLASHIMAGES={_SPLASHIMAGES_}
SPLASHVIEW=_SPLASHVIEW_
DEFAULT_FONTNAME = "_DEFAULT_FONTNAME_"
SDKCONFIG={}
FORCELOGIN="1"
LOCALETYPE="_LOCALETYPE_"
-- 士兵比例
BATTLESOLIDERZOOM="1"
-- 中心服
PASSPORT = "http://ss.qyz.feidou.com:8090/game_center_server"  
-- 登录地址
--LOGINURL = "callback/login.verify?password={password}&username={username}&pid={logintype}&gamecode="..gamecode.."&currenttime={currenttime}&channelid={channelid}"
LOGINURL = "/callback/login.verify?pid={platformID}&sid="
LOGINNOTICEURL="_LOGINNOTICEURL_"
REPORTURL="_REPORTURL_"
-- 充值比例
COINRATE = "1"
-- 充值货币
CHARGECURRENCY=""
-- 更新地址
UPGRADEURL="_UPGRADEURL_"
--是否强制更新
FORCEUPGRADE="1"
-- 金币花费二次弹框
GOLD_COST_CONFIRM = "0"
-- 创建角色随机名字
RANDON_PLAYER_NAME = "0" 
--20连抽确认
SHENJIANG_MAKESURE="0"
WEBCHARGE="0"
AREA_LIST_URL  =  string.format("/arealist_%s_%s.xml?_t=%s",BundleID,AppVersion,os.time()) 
AREA_LIST = nil
RESOURCE = nil
LOGLEVEL=_LOGLEVEL_
USELUASDK=_USELUASDK_
--本地推送开关
LOCAL_PUSH_SWITCH = "0"
-- 评价开关
GO_MARKET_SWITCH = "0"
-- 官网
OFFICIAL="http://sgqyz.feiliu.com/"
-- 论坛
FORUM="http://bbs.8783.com/forum-221-1.html"
FORCELOGIN="1"

_DEV_

if not DOWNLOAD_PATH then DOWNLOAD_PATH = nil end

packageDefine = true
end
