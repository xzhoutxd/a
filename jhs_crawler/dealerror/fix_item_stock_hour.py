#-*- coding:utf-8 -*-
#!/usr/bin/env python

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import time
import datetime
import re
import os
import json
import MySQLdb
from multiprocessing.dummy import Pool as ThreadPool
class FixStock():
    def __init__(self):
        self.SET_NAMES_QUERY = "set names utf8"
        # Open database connection
        self.db = MySQLdb.connect("127.0.0.1","root","zhouxin","jhs",charset='utf8')

        # prepare a cursor object using cursor() method
        self.db_cursor = self.db.cursor()

    def fix_stock(self,item):
        filepath_m = '/usr/local/jhsdata/page/item/hour/'

        need_fix_file_list = []
        #for item in stock_results:
        #print item
        item_c_time = item[0]
        ju_id = item[1]
        act_id = item[2]
        print item_c_time,ju_id,act_id

        #num = 24
        for i in range(2,26):
            time_dt = datetime.datetime.strptime(item_c_time,'%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=i)
            #time_dt = item_c_time + datetime.timedelta(hours=i)
            time_s = time_dt.strftime('%Y-%m-%d %H:%M:%S')
            filepath = filepath_m + time.strftime('%Y/%m/%d/%H/',time.strptime(time_s, "%Y-%m-%d %H:%M:%S")) + '%s_item/%s/'%(str(act_id),str(ju_id))
            if os.path.exists(filepath):
                file_list = os.listdir(filepath)
                for f in file_list:
                    m = re.search(r'\d+-\d+_item-dynamic_\d+.htm', f, flags=re.S)
                    if m:
                        need_fix_file_list.append((filepath + f, str(i-1), str(ju_id), str(act_id)))
            else:
                print '# file path not find: ',filepath
        print '# num file:', len(need_fix_file_list)

        stock_item_list = []
        i = 0
        for need_file in need_fix_file_list:
            i += 1
            fout = open(need_file[0], 'r')
            s = fout.read()
            fout.close()

            #print need_file[0]
            m = re.search(r'"stock": "(.+?)",', s, flags=re.S)
            if m:
                stock_item_list.append((need_file[1],m.group(1),need_file[2],need_file[3]))

        print '# stock item num:', len(stock_item_list)

        for r in stock_item_list:
            #print r
            update_sql = 'update nd_jhs_parser_item_stock_h_copy set %s = %s where item_juid = %s and act_id = %s'%('item_stock_h%s'%(r[0]),str(r[1]),str(r[2]),str(r[3]))
            print update_sql
            try:
                self.db_cursor.execute(self.SET_NAMES_QUERY)
                self.db_cursor.execute(update_sql)
                self.db.commit()
            except StandardError as err:
                self.db.rollback()
                print err

    def run_fix(self):
        time_start = '2015-02-02'
        time_end = '2015-02-03'
        #stock_sql = 'select DATE_FORMAT(crawl_time,\'%Y-%m-%d %H:%M:%S\'), item_juid, act_id from nd_jhs_parser_item_stock_h_copy where crawl_time > \'%s\' and crawl_time < \'%s\''%(time_start,time_end)
        stock_sql = 'select crawl_time, item_juid, act_id from nd_jhs_parser_item_stock_h_copy where crawl_time > \'%s\' and crawl_time < \'%s\''%(time_start,time_end)

        try:
            self.db_cursor.execute(self.SET_NAMES_QUERY)
            self.db_cursor.execute(stock_sql)
            stock_results = self.db_cursor.fetchall()
        except StandardError as err:
            print err

        print '# date:',time_start
        print '# item num:',len(stock_results)
        print stock_results

        s_results = []
        for item in stock_results:
            #s_results.append((item[0].strftime('%Y-%m-%d %H:%M:%S'),item[1],item[2]))
            s_results.append((str(item[0]),item[1],item[2]))
            
        pool = ThreadPool(2)
        pool.map(self.fix_stock,s_results)
        pool.close()
        pool.join()

        self.db_cursor.close()
        #关闭    
        self.db.close()


    

if __name__ == '__main__':
    f = FixStock()
    f.run_fix()



