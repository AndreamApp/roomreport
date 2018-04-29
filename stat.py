# -*- coding: utf-8 -*-
import os
import codecs
import datetime
import operator

'''
读取聊天记录内容
'''
def read():
	file = codecs.open(chat_record_path, 'r', 'utf-8')
	lines = file.read().replace('\r', '').split('\n')
	file.close()
	return lines

'''
读取姓名列表
'''
def name_list():
    file = codecs.open(name_list_path, 'r', 'utf-8')
    list = file.read().replace('\r', '').split('\n')
    file.close()
    return list

stat_start_date = datetime.datetime(2018, 3, 5)
chat_record_path = 'chat.txt'
name_list_path = 'name_list.txt'

names = name_list()

class Record:
    def __init__(self):
        self.time: datetime.datetime = datetime.datetime.now()
        self.name: str = ''
        self.content: str = ''

class RoomStat:
    def __init__(self):
        self.total_report: int = 0
        self.ontime_report: int = 0
        self.outtime_report: int = 0
        self.report_list = []
        self.last_report_time: datetime.datetime = datetime.datetime(1970, 1, 1)

    def add(self, time: datetime.datetime, content: str):
        if time.strftime('%Y-%m-%d') != self.last_report_time.strftime('%Y-%m-%d'):
            if (time.hour >=  23 and time.minute > 30) or (time.hour <= 16):
                self.outtime_report += 1
            else:
                self.ontime_report += 1
            self.total_report += 1
        self.last_report_time = time
        self.report_list.append(content)

class WeekStat:
    def __init__(self, week_num: int):
        self.week_num = week_num
        self.period_start: datetime.datetime = stat_start_date + datetime.timedelta(weeks = (week_num - 1))
        self.period_end: datetime.datetime = self.period_start + datetime.timedelta(weeks = 1)
        self.stat: dict = {}

        # init all names
        for n in names:
            if n != '':
                self.stat[n] = RoomStat()

    def inThisWeek(self, time: datetime.datetime)-> bool:
        offset_time = offset(time)
        return offset_time >= self.period_start and offset_time < self.period_end


'''
对没有群名片的姓名，根据回复内容，尝试规范化名字
eg.
2018-03-12 22:19:23 高雨彤(3226491609)
松四642，应在2人，实在2人，请假0人
返回
松四-642-高雨彤
'''
def fix_name(name, content):
    if name not in names:
        # try to fix unnormal name
        # analyse sender name from content
        if len(content.strip('\r\t ')) > 5:
            s = content.strip('\r\t ')
            prefix = s[0:2] + '-' + s[2:5]
            for n in names:
                if n.startswith(prefix):
                    return n
    return name

'''
因为每天凌晨的记录要归到前一天。所以判断所属天数时把时间向前偏移12小时
'''
def offset(time):
    return time - datetime.timedelta(hours=12)

'''
字典按key排序，返回list<[key, value]>
'''
def sortDict(d: dict):
    return sorted(d.items(), key = operator.itemgetter(0))

'''
解析聊天记录，返回list<Record>
'''
def parse():
    lines = read()
    lines.append('\n2018-01-01 00:00:00 Boundary(666666)\n')

    res = []
    temp = Record()
    content = '' # type: str
    started = False
    for line in lines: # type: str
        line = line.replace('\r', '') # ignore \r
        if line.startswith('2018'):
            # append last record
            if started:
                # filter unrelative message
                if temp.name != '系统消息' \
                        and temp.name != ''\
                        and '周艺璇' not in temp.name\
                        and '班主任' not in temp.name\
                        and '辅导员' not in temp.name:
                    temp.name = fix_name(temp.name, content)
                    temp.content = content
                    res.append(temp)
                    content = ''
                    temp = Record()
            else:
                started = True

            line_seg = line.split(' ')
            # parse next record
            timestr = line_seg[0] + ' ' + line_seg[1]
            # eg. 2018-03-12 22:18:32
            temp.time = datetime.datetime.strptime(timestr, '%Y-%m-%d %H:%M:%S') # type: datetime

            name_end_index = -1
            if line.endswith(')'):
                name_end_index = line.rfind('(')
            else:
                name_end_index = line.rfind('<')
            temp.name = line[len(timestr) + 1 : name_end_index]
        else:
            # parse content of record
            if line != '':
                content += line
    return res

'''
根据聊天记录，统计每周的报寝情况，返回list<WeekStat>
'''
def stat():
    list = parse()

    res = []
    week = 1
    week_stat = WeekStat(week)

    i = 0
    while i < len(list):
        record = list[i]

        if week_stat.inThisWeek(record.time):
            if record.name in week_stat.stat:
                week_stat.stat[record.name].add(record.time, record.content)
            i += 1
        else:
            week_stat.stat = sortDict(week_stat.stat)
            res.append(week_stat)
            week += 1
            week_stat = WeekStat(week)
    if len(week_stat.stat) > 0:
        week_stat.stat = sortDict(week_stat.stat)
        res.append(week_stat)
    return res

'''
输出每周的报寝情况，包括各个寝室报寝此时、按时、未按时次数
'''
def output():
    week_stats = stat()

    for s in week_stats: # type: WeekStat
        print('第' + str(s.week_num) + '周')
        print(s.period_start.strftime('%Y-%m-%d'), '~', s.period_end.strftime('%Y-%m-%d'))
        print('寝室', '报寝次数', '按时', '未按时')
        for r in s.stat:
            print(r[0], r[1].total_report, r[1].ontime_report, r[1].outtime_report)
            if(r[0] == ''):
                print(r[1].report_list)
        print('')

output()
