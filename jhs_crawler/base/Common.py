#-*- coding:utf-8 -*-
#!/usr/bin/env python

import re
import random
import time
import datetime
import urllib

# defined exception
class DenypageException(Exception):
    pass

class NoPageException(Exception):
    pass

class InvalidPageException(Exception):
    pass

# network fails exception
class NetworkFailureException(Exception):
    pass

# not taobao login exception
class NoTBLoginException(Exception):
    pass

# taobao check code exception
class TBCheckCodeException(Exception):
    pass

# not activity exception
class NoActivityException(Exception):
    pass

# not shop exception
class NoShopException(Exception):
    pass

# not item exception
class NoItemException(Exception):
    pass

# not shop item exception
class NoShopItemException(Exception):
    pass

# 全局变量
template_str = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
template_low = 'abcdefghijklmnopqrstuvwxyz0123456789'
template_tag = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789&='
template_num = '0123456789'

def add_days(n = 0, fmt='%Y-%m-%d'):
    dt = datetime.datetime.now()
    nDays = datetime.timedelta(days=n)
    dt = dt + nDays
    return dt.strftime(fmt)

def today_s(fmt='%Y-%m-%d'):
    return time.strftime(fmt, time.localtime(time.time()))

def today_ss():
    return today_s('%Y%m%d')

def day_s(t, fmt='%Y-%m-%d'):
    return '0.0' if t == '' else time.strftime(fmt, time.localtime(t))

def day_ss(t):
    return day_s(t, '%Y%m%d')

def date2timestamp(d):
    return float(time.mktime(d.timetuple()))

def str2timestamp(s, fmt="%Y-%m-%d %H:%M:%S"):
    try:
        s = s.strip()
        d = datetime.datetime.strptime(s, fmt)
        return date2timestamp(d)
    except:
        return 0.0

def nowhour_s(fmt='%H'):
    return time.strftime(fmt, time.localtime(time.time()))

# To compute time delta
def timeDelta(t, h='00:00:00'):
    t_end = 0.0
    if type(t) is float:
        t_str = day_s(t) + ' ' + h
        t_end = str2timestamp(t_str)
    return t_end

# 随机用户名
def rand_user(pfx = 'tb'):
    s = '%s%06d' %(pfx, random.randint(1, 999999))
    return s

# 随机字符串
def rand_s(template, length):
    s = ''
    for i in range(0, length):
        s += random.choice(template)
    return s

def rand_n(n=4):
    return rand_s(template_num, n)

# 随机IP地址
def randIp():
    ips = []
    ips.append(str(random.randint(111, 251)))
    ips.append(str(random.randint(121, 240)))
    ips.append(str(random.randint( 40, 251)))
    ips.append(str(random.randint(150, 253)))
    return '.'.join(ips)

# 计算差集
def diffSet(A, B):
    return list(set(A).difference(set(B)))

# 计算并集
def unionSet(A, B):
    return list(set(A).union(set(B)))

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

def htmlContent(s, c=''):
    return re.sub('<(.+?)>', c, s, flags=re.S)

def trim_s(s):
    if s and len(s) > 0:
        s = re.sub('\s|　','', s)
    return s

def trim_ch(s):
    if s and len(s) > 0:
        s = re.sub('\n|\r','', s)
    return s

def decode(s):
    return s.decode('utf-8','ignore').encode('gbk','ignore')

def decode_r(s):
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

def now():
    return time.time()

# 当前时间字符串
def now_s(fmt='%Y-%m-%d %H:%M:%S'):
    return time.strftime(fmt, time.localtime(time.time()))

# 当前时间字符串
def now_ss():
    return now_s('%Y%m%d%H%M%S')

def timestamp(_ms = 0):
    return time.time() * 1000 + _ms

# To get url template
def urlTemplate(_type):
    template = None
    if _type == '1':
        template = 'http://detail.tmall.com/item.htm?id=%s'
    elif _type == '2':
        template = 'http://item.taobao.com/item.htm?id=%s'
    return template

def charset(data):
    coder = 'gbk'
    if data and data != '':
        data = re.sub('"|\'| ', '', data.lower())
        if re.search(r'charset=utf-8', data):
            coder = 'utf-8'
    return coder

# 随机json回调名称
def jsonCallback(n=4):
    return 'jsonp%s' %rand_s(template_num, n)

def cookieJar2Dict(cj):
    cj_d = {}
    for c in cj:
        cj_d[c.name] = c.value
    return cj_d

   
# local ip
import socket
def local_ip():
    host = socket.gethostname()
    ip = socket.gethostbyname(host)
    return ip
 
