#!/usr/bin/python
#coding=utf-8

#lua代码多语言脚本
import cgi, cgitb 
import commandsutils
import os
import re
import sys
import xlrd
reload(sys)
sys.setdefaultencoding('utf-8')

userHome = os.path.expanduser('~')


if __name__=="__main__":


	form = cgi.FieldStorage()
	cversion = form.getvalue('cversion')
	if not cversion:
		cversion = "trunk"

	rootdir = userHome + "/work/qunying/client/" + cversion + "/gameClient/cached_res"
	saveDir = userHome + "/work/qunying/share/" + cversion + "/程序目录/resource/i18n"
	ClientLangDir = saveDir + "/ClientLang.xls"
	svnLuaDir = "$HOME/work/qunying/client/" + cversion + "/gameClient/cached_res/script"
	svnExcelDir = "$HOME/work/qunying/share/" + cversion + "/程序目录/resource/i18n"
	cversionDir = userHome + "/work/qunying/share/" + cversion

	if os.path.isdir(cversionDir):

		commandsutils.execCmd("svn update " + svnLuaDir)
		commandsutils.execCmd("svn update " + svnExcelDir)

		NeedReplaceStr = []
		NeedReplaceStrReverse = {}
		NeedReplaceStrMap = {}
		NeedReplaceStrMapOld = {}

		SaveIndex = 0 		# 保存excel多余的index起始索引
		if os.path.exists(ClientLangDir):
			data = xlrd.open_workbook(ClientLangDir)
			table = data.sheets()[0] 
			num = table.nrows
			SaveIndex = num 
			for x in range(0,num):

				tempKey = str(table.cell(x,0).value)
				tempValue = str(table.cell(x,1).value)
				tempData = [tempKey, tempValue]
				NeedReplaceStr.append(tempData)
				NeedReplaceStrReverse[tempValue] = len(NeedReplaceStr) - 1
				NeedReplaceStrMap[tempKey] = tempValue
				NeedReplaceStrMapOld[tempKey] = tempValue


		# 筛选需要替换的数组
		for parent,dirnames,filenames in os.walk(rootdir):
			for i in filenames:

				m=re.search(".*lua$",i)
		  		if m != None and i != "LangAuto.lua" and i.find("UpDateTipS")<0 and i != "UpDateTipS.lua" and parent != rootdir + "/script/mvc/instance/model/cfg2profile":
		  			path = parent + "/" + i

		  			pathDesc = i.replace(".lua", "")

		  	 		zz = open(path, "r+")

		  	 		lines = zz.readlines()
		  	 		if len(lines) > 0 :
		  	 			# print pathDesc

		  	 			zz.seek(0)
		  	 			zz.truncate()
		  	 			
		  	 			#双中括号相关
			  	 		isInOtherDesc = False
			  	 		strOtherDesc = ""
			  	 		isHaveChinese = False

			  	 		for lineIndex, strA in enumerate(lines):

				  	 		strNew = strA

				  	 		if strNew.find("print") > -1:
				  	 			# 打印的代码pass
			  	 				pass
			  	 			elif strNew.find("dump") > -1:
				  	 			# dump打印的代码pass
			  	 				pass
			  	 			else:

					  	 		# b = re.findall(r'\"([^u4e00-u9fff]+)\"',strNew)
					  	 		# for ccc in b:
					  	 		# 	# strNew = strNew.replace('"' + ccc + '"', "替换数据")
					  	 		# 	# print strNew
					  	 		# 	print ccc

					  	 		# # zz.write(strNew)

					  	 		replaceList = []
					  	 		index = 0 			#下次开始的索引
					  	 		isStrCenter = False	#是否处于查找中
					  	 		strStartIndex = 0 	#开始截取的index
					  	 		indexType = 0 		#0：正常	1：单引号锁定	2：双引号锁定
					  	 		indexZhuShi = strNew.find("--")

					  	 		while 1:
						  	 		
					  	 			if isInOtherDesc == True:
					  	 				# 在[[ ]]中
					  	 				indexDescOtherRight = strNew.find("]]", index)
					  	 				if indexDescOtherRight > -1:
						  	 				isInOtherDesc = False
						  	 				index = indexDescOtherRight + 2
						  	 				
						  	 				if isHaveChinese == True:
						  	 					

						  	 					pathDescIndex = 0
						  	 					while True:
					  	 							key = str(pathDesc) + str(pathDescIndex)
					  	 							if key in NeedReplaceStrMap:
					  	 								pathDescIndex = pathDescIndex + 1
					  	 							else:
					  	 								break
					  	 						tempdesc = str(strNew[strStartIndex: indexDescOtherRight])
					  	 						strOtherDesc = strOtherDesc + tempdesc
					  	 						strOtherDesc = strOtherDesc.replace("\n", "\\n")
					  	 						strOtherDesc = strOtherDesc.replace("\r", "\\r")
						  	 					Data = [key, strOtherDesc]
						  	 					desc = str(strNew[strStartIndex: indexDescOtherRight + 2])
						  	 					
						  	 					if strOtherDesc in NeedReplaceStrReverse:
					  	 							# 重复
					  	 							tempIndex = NeedReplaceStrReverse[strOtherDesc]
					  	 							key = NeedReplaceStr[tempIndex][0]
					  	 							DescData = [desc, key]
										  			replaceList.append(DescData)
					  	 						else:
					  	 							# 不重复
					  	 							DescData = [desc, key]
										  			replaceList.append(DescData)
													NeedReplaceStr.append(Data)
						  	 						NeedReplaceStrReverse[strOtherDesc] = len(NeedReplaceStr) - 1
						  	 						NeedReplaceStrMap[key] = strOtherDesc
						  	 				isHaveChinese = False
						  	 				strOtherDesc = ""
						  	 			else:
						  	 				if isHaveChinese == True:
						  	 					key = "clearDesc"
						  	 				
						  	 					DescData = [strNew, key]
										  		replaceList.append(DescData)
						  	 					strOtherDesc = strOtherDesc + strNew

					  	 					break

						  	 		indexTwo = strNew.find("\"", index)
						  	 		indexOne = strNew.find("\'", index)
						  	 		indexDescOther = strNew.find("[[", index)
						  	 		if indexZhuShi > -1 and ((indexTwo > -1 and indexTwo > indexZhuShi) or indexTwo == -1) and ((indexOne > -1 and indexOne > indexZhuShi) or indexOne == -1) and ((indexDescOther > -1 and indexDescOther > indexZhuShi) or indexDescOther == -1):
						  	 			# 注释 跳过
						  	 			break
						  	 		elif indexDescOther > -1 and ((indexTwo > -1 and indexTwo > indexDescOther) or indexTwo == -1) and ((indexOne > -1 and indexOne > indexDescOther) or indexOne == -1):
						  	 			# 双中括号开始
						  	 			isInOtherDesc = True
						  	 			index = indexDescOther + 1
						  	 			strStartIndex = indexDescOther
						  	 			indexDescOtherRight = strNew.find("]]", index)
						  	 			if indexDescOtherRight > -1:
						  	 				isInOtherDesc = False
						  	 				index = indexDescOtherRight + 1
						  	 				desc = str(strNew[strStartIndex: indexDescOtherRight + 2])
						  	 				b = re.findall('[\x80-\xff].', desc) 
						  	 				if len(b) > 0:
						  	 					pathDescIndex = 0
						  	 					while True:
					  	 							key = str(pathDesc) + str(pathDescIndex)
					  	 							if key in NeedReplaceStrMap:
					  	 								pathDescIndex = pathDescIndex + 1
					  	 							else:
					  	 								break
					  	 						Value = str(strNew[strStartIndex + 2: indexDescOtherRight])
					  	 						Data = [key, Value]
					  	 						if Value in NeedReplaceStrReverse:
					  	 							# 重复
					  	 							tempIndex = NeedReplaceStrReverse[Value]
					  	 							key = NeedReplaceStr[tempIndex][0]
					  	 							DescData = [desc, key]
										  			replaceList.append(DescData)
					  	 						else:
					  	 							# 不重复
					  	 							DescData = [desc, key]
										  			replaceList.append(DescData)
													NeedReplaceStr.append(Data)
						  	 						NeedReplaceStrReverse[Value] = len(NeedReplaceStr) - 1
						  	 						NeedReplaceStrMap[key] = Value
						  	 			else:
						  	 				isHaveChinese = False

						  	 				desc = str(strNew[strStartIndex: -1])
						  	 				b = re.findall('[\x80-\xff].', desc)
						  	 				if len(b) > 0:
						  	 					isHaveChinese = True

						  	 					key = "clearDesc"
						  	 				
						  	 					DescData = [desc, key]
										  		replaceList.append(DescData)

										  		strOtherDesc = str(strNew[strStartIndex + 2: -1])
										  	else:
							  	 				for x in range(lineIndex,len(lines) - 1):
							  	 					strTempLine = lines[x]
							  	 					tempRightIndex = strTempLine.find("]]")
							  	 					strTempDesc = strTempLine[0: tempRightIndex]
							  	 					cc = re.findall('[\x80-\xff].', strTempDesc) 
							  	 					if len(cc) > 0:
							  	 						isHaveChinese = True
							  	 						key = "clearDesc"
						  	 				
						  	 							DescData = [desc, key]
										  				replaceList.append(DescData)

										  				strOtherDesc = str(strNew[strStartIndex + 2: -1])
							  	 						break
							  	 					if tempRightIndex > -1:
							  	 						isHaveChinese = False
							  	 						break

						  	 				break


						  	 		elif indexType == 1:
						  	 			indexTwo = -1
						  	 		elif indexType == 2:
						  	 			indexOne = -1

						  	 		if indexOne == -1 and indexTwo == -1:
						  	 			break
						  	 		elif indexOne == -1 and indexTwo > -1:

						  	 			if isStrCenter == True:

						  	 				# 在字符串中
						  	 				if strNew[indexTwo - 1] == "\\":
						  	 					# 转意"
						  	 					pass
						  	 				else:
						  	 					isStrCenter = False
						  	 					indexType = 0

						  	 					desc = str(strNew[strStartIndex: indexTwo + 1])
						  	 					b = re.findall('[\x80-\xff].', desc) 
						  	 					if len(b) > 0:

						  	 						pathDescIndex = 0
						  	 						while True:
						  	 							key = str(pathDesc) + str(pathDescIndex)
						  	 							if key in NeedReplaceStrMap:
						  	 								pathDescIndex = pathDescIndex + 1
						  	 							else:
						  	 								break
						  	 						Value = str(strNew[strStartIndex + 1: indexTwo])
						  	 						Data = [key, Value]
						  	 						if Value in NeedReplaceStrReverse:
						  	 							# 重复
						  	 							tempIndex = NeedReplaceStrReverse[Value]
						  	 							key = NeedReplaceStr[tempIndex][0]
						  	 							DescData = [desc, key]
											  			replaceList.append(DescData)
						  	 						else:
						  	 							# 不重复
						  	 							DescData = [desc, key]
											  			replaceList.append(DescData)
														NeedReplaceStr.append(Data)
							  	 						NeedReplaceStrReverse[Value] = len(NeedReplaceStr) - 1
							  	 						NeedReplaceStrMap[key] = Value
							  	 						# print "Value:" + Value
							  	 						# print "NeedReplaceStr:" + NeedReplaceStr[len(NeedReplaceStr) - 1][1]
						  	 			else:
						  	 				# 重新开始字符串
						  	 				strStartIndex = indexTwo
						  	 				isStrCenter = True

						  	 			index = indexTwo + 1
						  	 		elif indexOne > -1 and indexTwo == -1:
						  	 			if isStrCenter == True:

						  	 				# 在字符串中
						  	 				if strNew[indexOne - 1] == "\\":
						  	 					# 转意"
						  	 					pass
						  	 				else:
						  	 					isStrCenter = False
						  	 					indexType = 0

						  	 					desc = str(strNew[strStartIndex: indexOne + 1])
						  	 					b = re.findall('[\x80-\xff].', desc) 
						  	 					if len(b) > 0:
						  	 						
						  	 						pathDescIndex = 0
						  	 						while True:
						  	 							key = str(pathDesc) + str(pathDescIndex)
						  	 							if key in NeedReplaceStrMap:
						  	 								pathDescIndex = pathDescIndex + 1
						  	 							else:
						  	 								break
						  	 						Value = str(strNew[strStartIndex + 1: indexOne])
						  	 						Data = [key, Value]
						  	 						if Value in NeedReplaceStrReverse:
						  	 							# 重复
						  	 							tempIndex = NeedReplaceStrReverse[Value]
						  	 							key = NeedReplaceStr[tempIndex][0]
						  	 							DescData = [desc, key]
											  			replaceList.append(DescData)
						  	 						else:

						  	 							# 不重复
						  	 							DescData = [desc, key]
											  			replaceList.append(DescData)
							  	 						NeedReplaceStr.append(Data)
							  	 						NeedReplaceStrReverse[Value] = len(NeedReplaceStr) - 1
							  	 						NeedReplaceStrMap[key] = Value
						  	 					
						  	 			else:
						  	 				# 重新开始字符串
						  	 				strStartIndex = indexOne
						  	 				isStrCenter = True

						  	 			index = indexOne + 1
						  	 		else:
						  	 			if indexTwo > indexOne:
						  	 				# 单引号开始
						  	 				strStartIndex = indexOne
						  	 				index = indexOne + 1
						  	 				indexType = 1
						  	 			else:
						  	 				# 双引号开始
						  	 				strStartIndex = indexTwo
						  	 				index = indexTwo + 1
						  	 				indexType = 2

						  	 			isStrCenter = True
						  	 	for replaceDesc in replaceList:
						  	 		print replaceDesc[0] + u"," + replaceDesc[1]
						  	 		if replaceDesc[1] == "clearDesc" :
						  	 			strNew = strNew.replace(replaceDesc[0], '')
						  	 		else:
						  	 			strNew = strNew.replace(replaceDesc[0], 'l_lang.getText(\"' + replaceDesc[1] + '\")')

					  	 	zz.write(strNew)

				  	 	zz.close()


		# 保存在Excell
		from xlwt import *
		from xlutils.copy import copy

		if not os.path.exists(ClientLangDir):
			print "开始创建"
			w = Workbook()     #创建一个工作簿
			ws = w.add_sheet(u'一个表')     #创建一个工作表
			
			for Name in NeedReplaceStr:
				ws.write(SaveIndex, 0,Name[0].decode("utf-8"))
				ws.write(SaveIndex, 1,Name[1].decode("utf-8"))
				SaveIndex = SaveIndex + 1

			w.save(ClientLangDir)     #保存
			print "创建完成"
		else:
			print "开始修改"
			w = xlrd.open_workbook(ClientLangDir)
			dataWrite = copy(w)
			ws = dataWrite.get_sheet(0)
			
			for Name in NeedReplaceStr:
				if Name[0].decode("utf-8") in NeedReplaceStrMapOld:
					pass
				else:
					ws.write(SaveIndex, 0,Name[0].decode("utf-8"))
					ws.write(SaveIndex, 1,Name[1].decode("utf-8"))
					SaveIndex = SaveIndex + 1

			dataWrite.save(ClientLangDir)     #保存
			print "修改完成"

		commandsutils.execCmd('svn commit ' + svnExcelDir + ' -m "auto commit ClientLang.xls"')
		commandsutils.execCmd('svn commit ' + svnLuaDir + ' -m "auto commit 多语言代码替换"')

	else:

		print "版本号不存在"

