# -*- coding: utf-8 -*-
import os
import codecs
import datetime

from qqbot import qqbotsched

@qqbotsched(hour='23', minute='00')
def autoReport(bot):
    gl = bot.List('group', '16软工室长群')
    if gl is not None:
        content = listToText(statUnrepot())
        for group in gl:
            bot.SendTo(group, content)

bot_state = True

if not os.access('report', os.F_OK):
    os.mkdir('report')
file = codecs.open('name_list.txt', 'r', 'utf-8')
name_list = file.read().split('\n')
file.close()

print(name_list)

def retrivePath():
    today = datetime.date.today()
    path = 'report\\%d-%d-%d.txt' % (today.year, today.month, today.day)
    return path

def statReported():
    path = retrivePath()
    if os.access(path, os.F_OK):
        file = codecs.open(path, 'r', 'utf-8')
        reported_list = file.read().split('\n')
        file.close()
    else:
        reported_list = []
    return reported_list

def report(name):
    if name not in statReported():
        path = retrivePath()
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

def listToText(list):
    content = ''
    for r in list:
        content += '@' + r + ' '
    return content

def onQQMessage(bot, contact, member, content): 
    global bot_state
    if contact.ctype == 'group' and contact.name == '16软工室长群':
        name = member.name
        if('松' in name or '竹' in name or '校外' in name and name in name_list):
            report(name)
        
        args = content.split(' ')
        if not bot_state:
            if args[0] == 'start':
                bot_state = True
                bot.SendTo(contact, '服务已开启')
        # stat
        elif args[0] == '统计':
            content = listToText(statUnrepot())
            bot.SendTo(contact, content)
        # autorpt 20:00
        #elif args[0] == 'autorpt':
        #    bot.SendTo(contact, '机器人已关闭')
        # stop
        elif args[0] == 'stop':
            bot_state = False
            bot.SendTo(contact, '服务已关闭')
            # bot.Stop()
        # help
        elif args[0] == 'help':
            bot.SendTo(contact, """支持下面这些命令
help - 获取帮助
统计 - 统计今天还没上报的寝室
stop - 停止服务
start - 开启服务
""")
