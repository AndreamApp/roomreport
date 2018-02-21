# -*- coding: utf-8 -*-
import os
import codecs
import datetime

if not os.access('report', os.F_OK):
    os.mkdir('report')
file = codecs.open('name_list.txt', 'r', 'utf-8')
name_list = file.read().split('\n')
file.close()

print(name_list)

def statReported():
    today = datetime.date.today()
    path = 'report\\%d-%d-%d.txt' % (today.year, today.month, today.day)
    if os.access(path, os.F_OK):
        file = codecs.open(path, 'r', 'utf-8')
        reported_list = file.read().split('\n')
        file.close()
    else:
        reported_list = []
    return reported_list

def report(name):
    today = datetime.date.today()
    path = 'report\\%d-%d-%d.txt' % (today.year, today.month, today.day)
    reported_list = statReported()
    if name not in reported_list:
        file = codecs.open(path, 'a', 'utf-8')
        file.write(name + '\n')
        file.close()

def statUnrepot():
    reported_list = statReported()
    unreport = []
    for n in name_list:
        if n not in reported_list:
            unreport.append(n)
    return unreport

def onQQMessage(bot, contact, member, content): 
    if contact.ctype == 'group' and contact.name == '16软工室长群':
        name = member.name
        if('松' in name or '竹' in name and name in name_list):
            report(name)
        if content == '统计':
            unreport = statUnrepot()
            content = ''
            for r in unreport:
                content += '@' + r + ' '
            bot.SendTo(contact, content)
        elif content == '-stop':
            bot.SendTo(contact, '机器人已关闭')
            bot.Stop()
