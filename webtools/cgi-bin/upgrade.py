#!/usr/bin/python
#coding=utf-8
import os,sys 
import os.path
import commands
print "Content-Type: text/html" 
print 
status ,output = commands.getstatusoutput("git pull")
print output