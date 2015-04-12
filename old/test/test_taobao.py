#-*- coding:utf-8 -*-
#!/usr/local/bin/python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re
import random
import json
import time
from TBItem import TBItem
from TMItem import TMItem
from parserTBItem import PTBItem
from parserTMItem import PTMItem

item_url = 'http://item.taobao.com/item.htm?id=42672800182'
T = TBItem()
T.antPage(item_url)
PT = PTBItem()
PT.antPage(T)
result = PT.outItemCrawl()
print result
