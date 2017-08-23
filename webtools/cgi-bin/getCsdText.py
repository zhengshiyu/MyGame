#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cgi, cgitb 
import os
import xml.dom
from xml.dom import minidom
import re
import sys
import commandsutils
import xlrd
reload(sys)
sys.setdefaultencoding('utf-8')


userHome = os.path.expanduser('~')

def get_attr_value(node, attrname):
     return node.getAttribute(attrname) if node else ''

def get_csd_name(root_node):
    property_groups = root_node.getElementsByTagName("PropertyGroup") if root_node else ''
 
    csd_names = []
 
    for item in property_groups:
        csd_names.append(get_attr_value(item, "Name"))
 
    if csd_names.__len__() == 1:
        return csd_names[0]
    else:
        return ""


if __name__=="__main__":

	form = cgi.FieldStorage()
	cversion = form.getvalue('cversion')
	if not cversion:
		cversion = "trunk"

	rootdir = userHome + "/work/qunying/share/" + cversion + "/UI/qunying/cocosstudio"
	saveDir = userHome + "/work/qunying/share/" + cversion + "/程序目录/resource/i18n"
	LangCsdDir = saveDir + u"/LangCsd.xls"
	svnDir = "$HOME/work/qunying/share/" + cversion + "/程序目录/resource/i18n"
	svnCsdDir = "$HOME/work/qunying/share/" + cversion + "/UI/qunying"
	cversionDir = userHome + "/work/qunying/share/" + cversion

	if os.path.isdir(cversionDir):

		commandsutils.execCmd("svn update " + svnCsdDir)
		commandsutils.execCmd("svn update " + svnDir)

		NeedReplaceStr = []
		NeedReplaceStrReverse = {}		#检查重复key使用
		repectKey = []
		NeedReplaceStrMapOld = {}


		SaveIndex = 0
		if os.path.exists(LangCsdDir):
			print "读取表数据"
			data = xlrd.open_workbook(LangCsdDir)
			table = data.sheets()[0] 
			num = table.nrows
			SaveIndex = num 
			for x in range(0,num):
				tempKey = str(table.cell(x,0).value)
				tempValue = str(table.cell(x,1).value)
				tempData = [tempKey, tempValue, x]
				NeedReplaceStrMapOld[tempKey] = tempData


		for parent,dirnames,filenames in os.walk(rootdir):
			for i in filenames:

				m=re.search(".*csd$",i)
		  		if m != None:
		  			path = parent + "/" + i
		  			print path
		  			# 得到dom对象
		  			# doc = xml.dom.minidom.parse(path)
		  			doc = minidom.parse(path)
		  			# 得到文档元素对象
		  			rootElement = doc.documentElement

		  			csd_name = i
		  			# print csd_name

					NodeObjectDataList = rootElement.getElementsByTagName("NodeObjectData")
					for NodeObjectData in NodeObjectDataList:
						strText = get_attr_value(NodeObjectData, "ButtonText")
						if len(strText) <= 0:
							strText = get_attr_value(NodeObjectData, "PlaceHolderText")
						if len(strText) <= 0:
							strText = get_attr_value(NodeObjectData, "LabelText")

						if len(strText) > 0 :

							strText = str(strText)
							b = strText
							# b = re.findall('[\x80-\xff].', strText)

							if len(b) > 0:
								# 重组KEY
								strName = get_attr_value(NodeObjectData, "Name")
								key = csd_name[0:len(csd_name) - 4].replace("view", "") + "_" + strName
								# 首字母大写
								key=key[0].upper()+key[1:len(key)]
								strText = strText.replace("\n", "\\n")

								if key in NeedReplaceStrReverse:
									repectKey.append(key)
								else:
									#去重
									# if strText in NeedReplaceStr:
									# 	print "重复：" + strText
									# else:
									# 	Data = [key, strText]
									# 	NeedReplaceStr.append(Data)
									# 	print strText

									#不去重 直接保存
									Data = [key, strText]
									NeedReplaceStr.append(Data)
									print "-" + strText + "-"

									NeedReplaceStrReverse[key] = key


		# from pyExcelerator import *
		from xlwt import *
		from xlutils.copy import copy

		exchangeList = [] 		# 中文修改，key不修改的list

		if not os.path.exists(LangCsdDir):
			print "开始创建"
			w = Workbook()     #创建一个工作簿
			ws = w.add_sheet(u'一个表')     #创建一个工作表
			for Name in NeedReplaceStr:
				ws.write(SaveIndex, 0,str(Name[0]).decode("utf-8"))
				ws.write(SaveIndex, 1,str(Name[1]).decode("utf-8"))
				SaveIndex = SaveIndex + 1

			w.save(saveDir + "/LangCsd.xls")     #保存
			print "创建完成"
		else:
			print "开始修改"
			w = xlrd.open_workbook(LangCsdDir)
			dataWrite = copy(w)
			ws = dataWrite.get_sheet(0)
			
			for Name in NeedReplaceStr:
				if Name[0].decode("utf-8") in NeedReplaceStrMapOld:
					if Name[1].decode("utf-8") != NeedReplaceStrMapOld[Name[0].decode("utf-8")][1]:
						Data = [Name[0].decode("utf-8"), Name[1].decode("utf-8"), NeedReplaceStrMapOld[Name[0].decode("utf-8")][1]]
						exchangeList.append(Data)
						ws.write(int(NeedReplaceStrMapOld[Name[0].decode("utf-8")][2]), 1,Name[1].decode("utf-8"))
				else:
					ws.write(SaveIndex, 0,Name[0].decode("utf-8"))
					ws.write(SaveIndex, 1,Name[1].decode("utf-8"))
					SaveIndex = SaveIndex + 1

			dataWrite.save(LangCsdDir)     #保存
			print "修改完成"


		if len(repectKey) > 0:
			print "警告：有重复key------------------------------------------"
			for key in repectKey:
				print key
		
		# 有key修改描述
		w1 = Workbook()     #创建一个工作簿
		ws1 = w1.add_sheet(u'一个表')     #创建一个工作表
		
		ws1.write(0, 0,u"key")
		ws1.write(0, 1,u"旧字符串")
		ws1.write(0, 2,u"新字符串")

		
		if len(exchangeList) > 0:
			exchangeListIndex = 1
			print "警告：有key修改描述，请根据表：多语言LangCsd需要修改字段.xls 修改多语言对应版本----------------------"
			for key in exchangeList:
				ws1.write(exchangeListIndex, 0,key[0].decode("utf-8"))
				ws1.write(exchangeListIndex, 1,key[2].decode("utf-8"))
				ws1.write(exchangeListIndex, 2,key[1].decode("utf-8"))
				exchangeListIndex = exchangeListIndex + 1
				# print key[0] + " :" + key[2] + "->" + key[1]

		w1.save(saveDir + "/多语言LangCsd需要修改字段.xls")     #保存

		commandsutils.execCmd('svn commit ' + svnDir + ' -m "auto commit csdExcel "')
	else:

		print "版本号不存在"
