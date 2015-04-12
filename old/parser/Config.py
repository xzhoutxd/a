#-*- coding:utf-8 -*-
#!/usr/local/bin/python

import os
import sys
import Common

reload(sys)
sys.setdefaultencoding('utf-8')

######################## 环境变量  ########################
configPath= '../../config/'
pagePath  = '../../page/qzj/'
dataPath  = '../../data/qzj/'
imagePath = '../../image/qzj/'
delim     = '\x01'
#delim    = ','

# 创建目录
def createPath(p):
    if not os.path.exists(p): os.makedirs(p)

######################## 唯品会  ########################
# 唯品会仓库列表
vip_warehouses = ['VIP_NH', 'VIP_SH', 'VIP_BJ', 'VIP_CD', 'VIP_HZ']

# 唯品会平台列表
# 1:PC+移动端, 2:移动端, 3:PC
vip_platforms = ['1', '2', '3']
VIP_ALL    = '1'
VIP_MOBILE = '2'
VIP_PC     = '3'

######################## 抓取设置  ########################

# 抓取对象类型
TMALL_TYPE  = '1'
TAOBAO_TYPE = '2'
VIP_TYPE    = '3'

######################## 其他设置  ########################

# 抓取起始时间
g_crawledTime = Common.str2timestamp('2000-01-01 00:00:00')

# 淘宝信用级别字典
#g_TBCreditDict = Common.buyerCredits(configPath + '/taobao_creditlevel.txt')

# 浮点数判0值
g_zeroValue = 0.00001
