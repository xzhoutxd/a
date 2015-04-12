#-*- coding:utf-8 -*-
#!/usr/local/bin/python

import re
import time
import datetime
import urllib

def now():
    return time.time()

# 当前时间字符串
def now_s():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

# 当前时间字符串
def now_ss():
    return time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))

def timestamp():
    return time.time() * 1000

def today_s():
    return time.strftime('%Y-%m-%d', time.localtime(time.time()))

def today_ss():
    return time.strftime('%Y%m%d', time.localtime(time.time()))

def day_s(t, fmt='%Y-%m-%d'):
    return '0.0' if t == '' else time.strftime(fmt, time.localtime(t))

def day_ss(t, fmt='%Y%m%d'):
    return '0.0' if t == '' else time.strftime(fmt, time.localtime(t))

def date2timestamp(d):
    return float(time.mktime(d.timetuple()))

def str2timestamp(s, fmt='%Y-%m-%d %H:%M:%S'):
    try:
        s = s.strip()
        d = datetime.datetime.strptime(s, fmt)
        return date2timestamp(d)
    except:
        return 0.0

# To compute time delta
def timeDelta(t, h='00:00:00'):
    t     = float(t)
    t_str = day_s(t) + ' ' + h
    t_end = str2timestamp(t_str)
    return t_end

# 计算中位数
def median(numbers):
    n = len(numbers)
    if n == 0: return None

    copy = numbers[:]
    copy.sort()
    if n & 1:
        m_val = copy[n/2]
    else:
        # 改进中位数算法：数值列表长度为偶数时，取中间小的数值
        m_val = copy[n/2-1]
        # 正常中位数算法：数值列表长度为偶数时，取中间2个数值的平均
        #m_val = (copy[n/2-1] + copy[n/2])/2
    return m_val

import HTMLParser
gHtmlParser = HTMLParser.HTMLParser()

def htmlDecode(data):
    return gHtmlParser.unescape(data)

def jsonDecode(data):
    return data.decode("unicode-escape")

def urlDecode(data):
    return urllib.unquote_plus(data)

def urlCode(data):
    return urllib.quote_plus(data)

def urlEncode(data,from_cs='utf-8',to_cs='gbk'):
    if from_cs != to_cs:
        data = data.decode(from_cs).encode(to_cs)
    return urllib.quote(data)

def htmlContent(s):
    return re.sub('<(.+?)>','', s, flags=re.S)

def trim_s(s):
    if s and len(s) > 0:
        s = re.sub('\s|　','', s)
    return s

def fileDecode(s):
    return s.decode('utf-8','ignore').encode('gbk','ignore')

def fileDecode_r(s):
    return s.decode('gbk','ignore').encode('utf-8','ignore')

def quotes_s(s):
    return re.sub(r'\'', '\\\'', s)

def time_s(t, fmt='%Y-%m-%d %H:%M:%S'):
    s = ''
    if type(t) is float:
        s = time.strftime(fmt, time.localtime(t))
    return s

def time_ss(t):
    return time_s(t, '%Y%m%d%H%M%S')

def htmlDecode_s(s):
    return s if s.find(r'&#') == -1 else htmlDecode(s)

def repeat_s(n, ss='%s'):
    s = ''
    for i in range(n):
        s += ss
    return s

def charset(data):
    data = re.sub('"|\'| ', '', data.lower())
    if re.search(r'charset=utf-8', data):
        coder = 'utf-8'
    else:
        coder = 'gbk'
    return coder

def fileRead(f_name):
    try:
        f = open(f_name, 'r')
        s = f.read()
        return s
    except Exception as e:
        print '# fileRead() exception :', f_name, e
    finally:
        f.close()
        
def buyerCredits(f_name):
    credit_d = {}
    infile = file(f_name, "r")
    for row in infile.readlines():
        row = row.strip()
        if len(row) > 0 and row[0] != '#':
            key, name = row.split(',')
            credit_d[key] = name
    infile.close()
    return credit_d
