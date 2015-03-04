#-*- coding:utf-8 -*-
#!/usr/bin/env python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re
import MySQLdb


SET_NAMES_QUERY = "set names utf8"
# Open database connection
db = MySQLdb.connect("127.0.0.1","root","zhouxin","jhs",charset='utf8')

# prepare a cursor object using cursor() method
db_cursor = db.cursor()

i = 1
for line in sys.stdin:
    try:
        if line.find('\'field list\'\")') != -1:
            print i
            i += 1
            val = line.split('%s) ')[1]
            p = re.compile(r'\n')
            _val = p.sub('', val)
            val_str = _val.replace('(','').replace(')','')
            val_list = val_str.split('\', ')
            new_list = []
            for item in val_list:
                if item.find('u\'') != -1:
                    new_list.append((item+'\'').decode('unicode_escape').replace('\'','').replace('u\'','\''))
                else:
                    new_list.append(((item+'\'').replace('\'','')).decode('string_escape'))
            t_val = tuple(new_list)
            sql = 'replace into nd_jhs_parser_activity_coming(crawl_time,act_id,category_id,category_name,act_position,act_platform,act_channel,act_name,act_url,act_desc,act_logopic_url,act_enterpic_url,act_status,act_sign,_act_ids,seller_id,seller_name,shop_id,shop_name,discount,act_soldcount,act_remindnum,act_coupon,act_coupons,brand_name,juhome,juhome_position,start_time,end_time,c_begindate,c_beginhour) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            try:
                db_cursor.execute(SET_NAMES_QUERY)
                db_cursor.execute(sql, t_val)
                db.commit()
            except StandardError as err:
                db.rollback()
                print t_val
                print err
                
    except StandardError as err:
        print err

