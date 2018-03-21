# -*- coding: utf-8 -*-
import os
import codecs
import datetime

from qqbot import qqbotsched

'''
TODO
消息人性化提示
每天0~12的消息，归到前一天
权限管理
定时设置
自动登录
'''

bot_state = True
bot_auto_report = True

name_list_path = '/data/py/roomreport/name_list.txt'

@qqbotsched(hour='23', minute='00')
def autoReport(bot):
    global bot_auto_report
    if not bot_auto_report:
        return
    gl = bot.List('group', '16软工室长群')
    if gl is not None:
        content = listToText(statUnrepot())
        for group in gl:
            bot.SendTo(group, content)

if not os.access('/data/report', os.F_OK):
    os.mkdir('/data/report')
file = codecs.open(name_list_path, 'r', 'utf-8')
name_list = file.read().split('\n')
file.close()

#print(os.path.abspath("report/xxx.txt"))

#print(name_list)
retrivePath()

def retrivePath():
    today = datetime.date.today()
    offset = today - datetime.timedelta(hours=12)
    path = '/data/report/%d-%d-%d.txt' % (offset.year, offset.month, offset.day)

file = codecs.open('/data/py/roomreport/name_list.txt', 'r', 'utf-8')
name_list = file.read().split('\n')
file.close()
#print(os.path.abspath("report/xxx.txt"))

#print(name_list)


def retrivePath():
    today = datetime.date.today()
    path = '/data/report/%d-%d-%d.txt' % (today.year, today.month, today.day)
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
    if len(list) == 0:
        return '所有人都报啦'
    content = '报寝提醒：'
    for r in list:
        content += '\n@' + r + ' '
    return content

def onQQMessage(bot, contact, member, content): 
    global bot_state
    if contact.ctype == 'group' and contact.name == '16软工室长群': #'机器人交流':# 
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
        # autorpt
        elif args[0] == 'autorpt':
            bot_auto_report = args[1] == 'on'
            if args[1] == 'on':
                bot_auto_report = True
                bot.SendTo(contact, '定时统计已开启')
            elif args[1] == 'off':
                bot_auto_report = False
                bot.SendTo(contact, '定时统计已关闭')
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
autorpt on - 开启定时统计，每天23:00准时统计
autorpt off - 关闭定时统计
stop - 停止服务
start - 开启服务
""")
