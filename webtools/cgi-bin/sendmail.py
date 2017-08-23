#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import smtplib
from email.mime.text import MIMEText
from email.header import Header

def isEmailAddr(addr):
    reg = "[a-zA-Z0-9]@.*\.(cn|com)"

def send(text,receivers):
    mail_host="smtp.exmail.qq.com"  
    mail_user="shupan@6sring.cn" 
    mail_pass="12345687aB"

    COMMASPACE = ', '
    sender = 'shupan@6sring.cn'

    message = MIMEText(text, 'plain', 'utf-8')
    message['From'] = sender
    message['To'] =  COMMASPACE.join(receivers)

    subject = "打包完成"
    message['Subject'] = Header(subject, 'utf-8')

    try:
        smtpObj = smtplib.SMTP_SSL(mail_host) 
        smtpObj.login(mail_user,mail_pass)  
        smtpObj.sendmail(sender, receivers, message.as_string())
        print ("邮件发送成功")
    except smtplib.SMTPException as e:
        print ("邮件发送失败")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage : python % text reciver1 reciver2 ...")
    recivers = sys.argv[2:]
    #  for reciver in recivers:
        #  if reciver:
            #  pass
    send(sys.argv[1],recivers)

