#-*- coding:utf-8 -*-
#!/usr/bin/env python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from TBItem import TBItem
from TMItem import TMItem
from parserTBItem import PTBItem
from parserTMItem import PTMItem


if __name__ == '__main__':
    tb_url = 'http://item.taobao.com/item.htm?id=42393202089&ns=1&abbucket=16#detail'
    print '# ', tb_url
    T = TBItem()
    T.antPage(tb_url)
    PT = PTBItem()
    PT.antPage(T)

    #tm_url = 'http://detail.tmall.com/item.htm?id=43128525108&tracelog=jubuybigpic'
    #print '# ', tm_url
    #T = TMItem()
    #T.antPage(tm_url)
    #PT = PTMItem()
    #PT.antPage(T)
