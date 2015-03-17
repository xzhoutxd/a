#-*- coding:utf-8 -*-
#!/usr/bin/env python

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re
import time
import random
import Common
from TBCrawler import TBCrawler

class RetryCrawler():
    '''A class of retry crawl data'''
    def __init__(self):
        # 抓取设置
        self.crawler = TBCrawler()

    def getData(self, url, refers='', max_retry=10):
        page = ''
        retry = 1
        while True:
            try:
                page = self.crawler.getData(url, refers)
                break
            except Common.InvalidPageException as e:
                if retry >= max_retry:
                    break
                retry += 1
                print '# Invalid page exception:',e
                time.sleep(1*retry)
            except Common.DenypageException as e:
                if retry >= max_retry:
                    break
                retry += 1
                print '# Deny page exception:',e
                time.sleep(1*retry)
            except Common.SystemBusyException as e:
                if retry >= max_retry:
                    break
                retry += 1
                print '# System busy exception:',e
                time.sleep(1*retry)
            except Exception as e:
                print '# exception err in retry crawler:',e
                if e.find('Read timed out') != -1:
                    if retry >= max_retry:
                        break
                    retry += 1
                    time.sleep(1*retry)
                else:
                    break

        return page
