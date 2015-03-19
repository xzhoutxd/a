#-*- coding:utf-8 -*-
#!/usr/bin/env python

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re
import os
import json
import time
#import MySQLdb
from multiprocessing.dummy import Pool as ThreadPool
import MysqlPool

jhs_db = MysqlPool.g_jhsDbPool


def run(val):
    update_sql = 'call nd_jhs_parser_activity_coming(%s,%s,%s)'
    jhs_db.execute(update_sql,val)

s_date,e_date = '2015-01-01','2015-02-05'
#s_date,e_date = '2015-02-05','2015-02-07'
#s_date,e_date = '2015-02-07','2015-02-10'
#s_date,e_date = '2015-02-10','2015-02-15'
#s_date,e_date = '2015-02-15','2015-02-20'
#s_date,e_date = '2015-02-20','2015-03-20'
sql = 'select act_id,c_begindate,c_beginhour from nd_jhs_parser_activity_coming where crawl_time < \'%s\' and crawl_time > \'%s\''%(e_date,s_date)
results = jhs_db.select(sql)

print '#Start time:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
print '# items num:',len(results)

item_val = []
for r in results:
    item_val.append((r[0],r[1],r[2]))

# 多线程
# multiprocessing.dummy Pool
pool = ThreadPool(3)
item_list = pool.map(run,item_val)
pool.close()
pool.join()

print '#End time:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

