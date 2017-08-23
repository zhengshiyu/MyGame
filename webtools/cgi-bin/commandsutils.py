import commands
import subprocess
import os,sys,re
import time
def execCmd(cmd):
	print cmd
	# commands.getstatusoutput(cmd)
	return os.popen(cmd).read()
	# retcode= subprocess.call(cmd,shell=True)
def svnRevertAndUpdate(path):
	execCmd("cd %s/ && svn revert --depth infinity . && svn up " %(path))
# svn del add commit
def svnCommit(path):
	execCmd("cd %s && svn st | grep '^\!' | tr '^\!' ' ' | sed 's/[ ]*//' | sed 's/[ ]/\\\\ /g' | xargs svn del " %(path))
	execCmd("cd %s && svn st | grep '^\?' | tr '^\?' ' ' | sed 's/[ ]*//' | sed 's/[ ]/\\\\ /g' | xargs svn add " %(path))
	execCmd("cd %s && svn commit -m 'auto commit and del file -%s'" %(path,time.strftime('%Y_%m_%d_%H_%M_%S')))
# string array dict bool real integer date data
def getPlistNodeType(value):
	nodeTyep = "string"
	if isinstance(value,bool):
		nodeTyep="bool"
	elif isinstance(value,list):
		nodeTyep="array"
	elif isinstance(value,dict):
		nodeTyep="dict"
	elif isinstance(value,int):
		nodeTyep="integer"
	return nodeTyep
def addArrayItem(key,index,value,path):
	nodeTyep = getPlistNodeType(value)
	execCmd("/usr/libexec/PlistBuddy -c 'Add :%s %s' %s" %(key,nodeTyep,path))
	execCmd("/usr/libexec/PlistBuddy -c 'Set :%s:%s %s' %s" %(key,index,value,path))

def addPlist(key,value,path):
	nodeTyep = getPlistNodeType(value)
	execCmd("/usr/libexec/PlistBuddy -c 'Add :%s %s' %s" %(key,nodeTyep,path))
	if nodeTyep=="array":
		execCmd("/usr/libexec/PlistBuddy -c 'Delete :%s' %s" %(key,path))
		execCmd("/usr/libexec/PlistBuddy -c 'Add :%s %s' %s" %(key,nodeTyep,path))
		index = 0
		for v in value:
			addArrayItem(key+":",index,v,path)
	elif nodeTyep == "dict":
		for v in value:
			addPlist(key+":"+v,value[v],path)
	else:
		execCmd("/usr/libexec/PlistBuddy -c 'Set :%s:0 %s' %s" %(key,value,path))

def setPlist(path,value):
	for k in value:
		nodeTyep =getPlistNodeType(value[k])
		addPlist(k,value[k],path)
def importP12(path,pwd):
	execCmd("security unlock-keychain -p mengjie ~/Library/Keychains/login.keychain")
	execCmd("security import %s -k ~/Library/Keychains/login.keychain -P %s -T /usr/bin/codesign" %(path,pwd))
def checkTeamName(path,dev):
	execCmd("security unlock-keychain -p mengjie ~/Library/Keychains/login.keychain")
	codesigning = execCmd("/usr/libexec/PlistBuddy -c 'Print TeamName' /dev/stdin <<< $(security cms -D -i %s)"  %(path)).strip()
	if dev=="dev":
		codesigning="iPhone Developer: "+codesigning
	else:
		codesigning="iPhone Distribution: "+codesigning
	identities = execCmd("security find-identity -v codesigning ~/Library/Keychains/login.keychain").strip()
	group = re.findall(r'"iPhone[^"]+"',identities)
	for gp in group:
		if gp.find(codesigning)>-1:
			return gp
	return '"iPhone Developer: shuai wang (FQ7YPW7E88)"'
def checkP12AndProvision(p12path,p12pwd,provisionpath,dev):
	if not checkTeamName(provisionpath,dev):
		importP12(p12path,p12pwd)
	return checkTeamName(provisionpath,dev)
if __name__ == "__main__":
	setPlist("/Volumes/RamDisk/generateApp/sgqygame.app/Info.plist",{"CFBundleURLTypes:0:CFBundleURLSchemes":["com.asqdddyz02.sddgqyz026.zhenjiang"]})
	# print checkP12AndProvision("~/work/webtoos/cgi-bin/p12/dh_dis.p12","123","~/work/webtoos/cgi-bin/p12/dh_dis.mobileprovision","dis")
	