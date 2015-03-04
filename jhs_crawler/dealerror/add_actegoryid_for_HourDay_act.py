#-*- coding:utf-8 -*-
#!/usr/bin/env python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re
import MySQLdb


SET_NAMES_QUERY = "set names utf8"
# Open database connection
#db = MySQLdb.connect("127.0.0.1","root","zhouxin","jhs",charset='utf8')
db = MySQLdb.connect("192.168.1.113","jhs","123456","jhs",charset='utf8')

# prepare a cursor object using cursor() method
db_cursor = db.cursor()

# hour
#sql = 'select act_id,category_id,category_name from nd_jhs_parser_activity where act_id in (select act_id from nd_jhs_parser_activity_alive_hour)'
# day
sql = 'select act_id,category_id,category_name from nd_jhs_parser_activity where act_id in (select act_id from nd_jhs_parser_activity_alive_day)'
try:
    db_cursor.execute(SET_NAMES_QUERY)
    db_cursor.execute(sql)
    results = db_cursor.fetchall()
except StandardError as err:
    print err

for r in results:
    print r
    # hour
    #update_sql = 'update nd_jhs_parser_activity_alive_hour set category_id = \'%s\',category_name = \'%s\' where act_id = %s'%(str(r[1]),str(r[2]),str(r[0]))
    # day
    update_sql = 'update nd_jhs_parser_activity_alive_day set category_id = \'%s\',category_name = \'%s\' where act_id = %s'%(str(r[1]),str(r[2]),str(r[0]))
    print update_sql
    try:
        db_cursor.execute(SET_NAMES_QUERY)
        db_cursor.execute(update_sql)
        db.commit()
    except StandardError as err:
        db.rollback()
        print err

db_cursor.close()    
   
#关闭    
db.close()
