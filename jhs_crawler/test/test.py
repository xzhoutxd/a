#-*- coding:utf-8 -*-
#!/usr/bin/env python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re
import random
import json
import time
import Queue
import traceback
import base.Common as Common
import base.Config as Config
from base.TBCrawler import TBCrawler

print '# start:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

print Common.today_s()

crawler    = TBCrawler()

#brand_url  = 'http://ju.taobao.com/tg/brand.htm'
home_url   = 'http://ju.taobao.com'
#refers     = 'http://www.tmall.com'
url = "http://detail.ju.taobao.com/home.htm?id=10000005814153&amp;item_id=43767519068"
page = crawler.getData(url, home_url)
print crawler.status_code
print type(crawler.history)
if type(crawler.history) is list:
    print type(crawler.history)
print crawler.history
#if re.search(r'<title>【聚划算】无所不能聚</title>', page, flags=re.S):
    # To build header
#    _header = crawler.buildHeader(home_url)
#    page = crawler.session.get(url, headers=_header, cookies=crawler.session_cookie, allow_redirects=False)
#    print page
#else:
#    print page
    

print Common.now()


