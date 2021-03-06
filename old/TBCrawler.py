#-*- coding:utf-8 -*-
#!/usr/bin/env python

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re
import time
import random
import Common
from Crawler import Crawler

class TBCrawler(Crawler):
    def __init__(self):
        # parent construct
        Crawler.__init__(self)

        self.crawl_cookie = {}

    def getData(self, url, refers='', decode=True, terminal='1'):
        # when null url, exit function
        if not url or not re.search(r'http://', url):
            return None

        # To build header
        _header = self.buildHeader(refers, terminal)

        # 天猫/淘宝店铺搜索页延时3-10秒
        if re.search(r'htm?search=y', url):
            time.sleep(random.uniform(3, 10))
        # 天猫成交页面延时5-10秒
        elif re.search(r'http://ext.mdskip.taobao.com/\w+/dealRecords.htm?', url):
            time.sleep(random.uniform(5, 10))
        # 淘宝成交页面延时5-10秒
        elif re.search(r'http://detailskip.taobao.com/\w+/show_buyer_list.htm?', url) :
            time.sleep(random.uniform(5, 10))
        # 其他页面延时0.1-1秒
        else:
            time.sleep(random.uniform(0.1, 1))

        _cookie = self.session_cookie if self.use_cookie else self.crawl_cookie

        # http Get请求
        if self.use_stream:
            r = self.session.get(url, headers=_header, cookies=_cookie, timeout=self.timeout, stream=True)
        else:
            r = self.session.get(url, headers=_header, cookies=_cookie, timeout=self.timeout)

        # check http code
        if not r.ok: r.close(); raise Common.InvalidPageException("Invalid crawl page occurs, url=%s" %url)

        # 网页内容
        data = ''
        if self.use_stream:
            for line in r.iter_lines(): data += (line if line else '')
        else: data = r.content

        # 跟踪cookie
        if not self.use_cookie and len(r.cookies) > 0: self.crawl_cookie = Common.cookieJar2Dict(r.cookies)

        # 网页编码
        self.f_coder = Common.charset(r.headers.get('content-type'))

        # 关闭结果
        r.close()

        # 网页编码归一化
        if decode and self.f_coder != self.t_coder: data = data.decode(self.f_coder,'ignore').encode(self.t_coder,'ignore')

        # pc/wap网页异常
        if terminal in ['1', '2']:
            # 异常处理1: 网站deny页
            m = re.search(r'<title>亲，访问受限了</title>', data)
            if m: raise Common.DenypageException("Deny page occurs!")

            m = re.search(r'<title>很抱歉，现在暂时无法处理您的请求-.+?</title>', data)
            if m: raise Common.DenypageException("Deny page occurs!")

            # 异常处理2: 出现淘宝登录页面
            m = re.search(r'<title>淘宝网 - 淘！我喜欢</title>.+?<li class="current"><h2>登录</h2></li>', data, flags=re.S)
            if m: raise Common.NoTBLoginException("Not Taobao login exception occurs!")

            # 异常处理3: 出现验证码页面
            m = re.search(r'<label for="checkcodeInput">验证码：</label>', data)
            if m: raise Common.TBCheckCodeException("Taobao Check code occurs!")

            # 异常处理4: 网页不存在
            m = re.search(r'<title>对不起，您访问的页面不存在！</title>', data)
            if m: raise Common.NoPageException("No page occurs!")

        # 返回抓取结果
        return data
