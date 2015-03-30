#-*- coding:utf-8 -*-
#!/usr/bin/env python

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import traceback
import time
import datetime
import re
import os
import json
from db.MysqlAccess import MysqlAccess
from JHSItem import JHSItem
from multiprocessing.dummy import Pool as ThreadPool
class FixLockTotalstock():
    def __init__(self):
        self.SET_NAMES_QUERY = "set names utf8"
        # Open database connection
        #self.db = MySQLdb.connect("127.0.0.1","root","zhouxin","jhs",charset='utf8')
        #self.db = MySQLdb.connect("192.168.1.113","jhs","123456","jhs",charset='utf8')

        # prepare a cursor object using cursor() method
        #self.db_cursor = self.db.cursor()
        # mysql
        self.mysqlAccess = MysqlAccess()

    def fix_stock(self,item):
        filepath_m = '/home/har/jhs/crawler_v2/jhsdata/page/item/hour/'

        need_fix_file_list = []
        #for item in stock_results:
        #print item
        start_time = item[0]
        ju_id = int(item[1])
        act_id = int(item[2])
        print start_time,ju_id,act_id

        #num = 24
        sql_list_updatetotalstock = []
        item = JHSItem()
        item.item_juId, item.item_actId = ju_id, act_id
        for i in range(0,24):
            time_dt = datetime.datetime.strptime(start_time,'%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=i)
            #time_dt = item_c_time + datetime.timedelta(hours=i)
            time_s = time_dt.strftime('%Y-%m-%d %H:%M:%S')
            filepath = filepath_m + time.strftime('%Y/%m/%d/%H/',time.strptime(time_s, "%Y-%m-%d %H:%M:%S")) + '%s_item/%s/'%(str(act_id),str(ju_id))
            crawl_date = time_dt.strftime('%Y-%m-%d')
            crawl_hour = time_dt.strftime('%H')
            sql_list_updatetotalstock.append((int(ju_id),crawl_date, crawl_hour))
            sql_list = []
            sql_list.append((int(ju_id),crawl_date, crawl_hour))
            self.mysqlAccess.update_item_totalstock(sql_list)
            if os.path.exists(filepath):
                file_list = os.listdir(filepath)
                for f in file_list:
                    #f_item_dy = None
                    #m = re.search(r'\d+-\d+_item-dynamic_\d+.htm', f, flags=re.S)
                    #if m:
                    #    f_item_dy = filepath + f
                    f_item_page = None
                    m = re.search(r'\d+-\d+_item-home-hour_\d+.htm', f, flags=re.S)
                    if m:
                        f_item_page = filepath + f
                        need_fix_file_list.append((f_item_page, time_s))
                        fout = open(f_item_page, 'r')
                        s = fout.read()
                        fout.close()
                        item.itemLock(s)
                        sql = item.outSqlForLock()
                        if sql:
                            s_list = []
                            s_list.append((sql[0],time_s,sql[2]))
                            self.mysqlAccess.updateJhsItem(s_list)
            else:
                print '# file path not find: ',filepath
        print '# num file:', len(need_fix_file_list)

        #i = 0
        #sql_list = []
        #for need_file in need_fix_file_list:
        #    i += 1
        #    if need_file[0]:
        #        fout = open(need_file[0], 'r')
        #        s = fout.read()
        #        fout.close()
        #        item.itemLock(s)
        #        sql = item.outSqlForLock()
        #        if sql:
        #            sql_list.append((sql[0],need_file[1],sql[2]))
                    

        #if len(sql_list_updatetotalstock) > 0:
            #print sql_list_updatetotalstock
        #    self.mysqlAccess.update_item_totalstock(sql_list_updatetotalstock)
        #if len(sql_list) > 0:
        #    self.mysqlAccess.updateJhsItem(sql_list)
            

    def run_fix(self):
        try:
            time_start = '2015-03-25'
            time_end = '2015-03-26'
            #sql = 'select c.start_time, a.item_juid, c.act_id from nd_jhs_parser_activity_item a join nd_jhs_mid_item_info b on a.item_juid = b.item_juid join nd_jhs_parser_activity c on a.act_id = c.act_id where c.start_time > \'%s\' and c.start_time < \'%s\' order by c.start_time,c.act_id'%(time_start,time_end)
            time_start = '2015-03-24 20:00:00'
            sql = 'select c.start_time, a.item_juid, c.act_id from nd_jhs_parser_activity_item a join nd_jhs_mid_item_info b on a.item_juid = b.item_juid join nd_jhs_parser_activity c on a.act_id = c.act_id where c.start_time = \'%s\' order by c.start_time,c.act_id'%(time_start)
            item_results = self.mysqlAccess.selectSQL(sql)

            print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            i_results = []
            for item in item_results:
                i_results.append((str(item[0]),int(item[1]),int(item[2])))
                #self.fix_stock((str(item[0]),int(item[1]),int(item[2])))
                #print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            print '# item num:',len(i_results)
            #print i_results
            print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

                
            pool = ThreadPool(8)
            pool.map(self.fix_stock,i_results)
            pool.close()
            pool.join()
        except Exception as e:
            self.traceback_log()

    def traceback_log(self):
        print '#####--Traceback Start--#####'
        tp,val,td = sys.exc_info()
        for file, lineno, function, text in traceback.extract_tb(td):
            print "exception traceback err:%s,line:%s,in:%s"%(file, lineno, function)
            print text
        print "exception traceback err:%s,%s,%s"%(tp,val,td)
        print '#####--Traceback End--#####'


if __name__ == '__main__':
    f = FixLockTotalstock()
    f.run_fix()



