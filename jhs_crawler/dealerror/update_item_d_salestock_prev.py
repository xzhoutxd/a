#-*- coding:utf-8 -*-
#!/usr/bin/env python

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re
import os
import json
import time
import MySQLdb
from multiprocessing.dummy import Pool as ThreadPool
import MysqlPool

jhs_db = MysqlPool.g_jhsDbPool


"""
SET_NAMES_QUERY = "set names utf8"
# Open database connection
#db = MySQLdb.connect("127.0.0.1","root","zhouxin","jhs",charset='utf8')
db = MySQLdb.connect("192.168.1.113","jhs","123456","jhs",charset='utf8')

# prepare a cursor object using cursor() method
db_cursor = db.cursor()
"""

def run(val):
    update_sql = 'call update_jhs_parser_item_d(%s,%s,%s,%s)'
    jhs_db.execute(update_sql,val)
    """
    try:
        db_cursor.execute(SET_NAMES_QUERY)
        db_cursor.execute(update_sql,val)
        db.commit()
    except StandardError as err:
        db.rollback()
        print err
    """

#s_date,e_date = '2015-01-01','2015-02-05'
#s_date,e_date = '2015-02-05','2015-02-07'
#s_date,e_date = '2015-02-07','2015-02-10'
#s_date,e_date = '2015-02-10','2015-02-15'
#s_date,e_date = '2015-02-15','2015-02-20'
s_date,e_date = '2015-02-20','2015-03-08' #81758
sql = 'select crawl_time,item_juid,act_id,c_begindate from nd_jhs_parser_item_d where item_soldcount_prev is null and item_stock_prev is null and crawl_time < \'%s\' and crawl_time > \'%s\''%(e_date,s_date)
results = jhs_db.select(sql)
"""
try:
    db_cursor.execute(SET_NAMES_QUERY)
    db_cursor.execute(sql)
    results = db_cursor.fetchall()
except StandardError as err:
    print err
"""

print '#Start time:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
print '# items num:',len(results)

item_val = []
for r in results:
    item_val.append((r[0],r[1],r[2],r[3]))
    """
    #update_sql = 'call update_jhs_parser_item_d(%s,%s,%s,%s)'%(r[0],r[1],r[2],r[3])
    update_sql = 'call update_jhs_parser_item_d(%s,%s,%s,%s)'
    try:
        db_cursor.execute(SET_NAMES_QUERY)
        db_cursor.execute(update_sql,(r[0],r[1],r[2],r[3]))
        db.commit()
    except StandardError as err:
        db.rollback()
        print err
    """

# 多线程
# multiprocessing.dummy Pool
pool = ThreadPool(3)
item_list = pool.map(run,item_val)
pool.close()
pool.join()

"""
#关闭    
db_cursor.close()
db.close()
"""
print '#End time:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

