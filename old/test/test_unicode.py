#-*- coding:utf-8 -*-
#!/usr/local/bin/python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re
#import base.Config as Config
import parser.Config as Config
#import base.Common as Common
import parser.Common as Common
from parserItem import Item


a='&nbsp;HSTYLE/&#38889;&#37117;&#34915;&#33293;'
print Common.htmlDecode(a)
