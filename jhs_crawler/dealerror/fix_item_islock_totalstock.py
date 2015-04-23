#-*- coding:utf-8 -*-
#!/usr/bin/env python

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

sys.path.append('../')
import traceback
import time
import datetime
import re
import os
import json
import base.Config as Config
from db.MysqlAccess import MysqlAccess
from JHSItem import JHSItem
from multiprocessing.dummy import Pool as ThreadPool
sys.path.append('../../db')
sys.path.append('../../base')
from MongoAccess import MongoAccess
class FixLockTotalstock():
    def __init__(self):
        self.SET_NAMES_QUERY = "set names utf8"
        # mysql
        self.mysqlAccess = MysqlAccess()
        self.mongoAccess = MongoAccess() # mongodb access

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
            crawl_date = time_dt.strftime('%Y-%m-%d')
            crawl_hour = time_dt.strftime('%H')
            sql_list_updatetotalstock.append((int(ju_id),crawl_date, crawl_hour))
            sql_list = []
            sql_list.append((int(ju_id),crawl_date, crawl_hour))

            item_hour_home_page = ''
            
            # mongo file
            key = '%s_%s_%s_%s_%s_%s' % (time.strftime('%Y%m%d%H',time.strptime(time_s, "%Y-%m-%d %H:%M:%S")),Config.JHS_TYPE,'1','item','itemlock',str(ju_id))
            item_pages = self.mongoAccess.findJHSPage(key)
            
            if item_pages and item_pages.has_key("pages") and item_pages["pages"].has_key("item-home-hour"):
                    #print item_pages["pages"]["item-home-hour"]
                    print 'item_page:',key
                    item_hour_home_page = item_pages["pages"]["item-home-hour"]
                    need_fix_file_list.append(key)
            else:
                print 'not find item_page:',key
            
            """
            # open file
            filepath = filepath_m + time.strftime('%Y/%m/%d/%H/',time.strptime(time_s, "%Y-%m-%d %H:%M:%S")) + '%s_item/%s/'%(str(act_id),str(ju_id))
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
                        item_hour_home_page = s
            else:
                print '# file path not find: ',filepath
            """

            
            if item_hour_home_page and item_hour_home_page != '':
                item.itemLock(item_hour_home_page)
                sql = item.outSqlForLock()
                if sql:
                    #s_list = []
                    #s_list.append((sql[0],time_s,sql[2]))
                    s = (sql[0],time_s,sql[2])
                    print sql[0],time_s,sql[2]
                    #self.mysqlAccess.updateJhsItem(s_list)
                    self.mysqlAccess.updateJhsItem(s)
                    #self.mysqlAccess.update_item_totalstock(sql_list)
            self.mysqlAccess.update_item_totalstock(sql_list)
        print '# num file:', len(need_fix_file_list)

    def run_fix(self):
        try:
            #time_start = '2015-03-25'
            #time_end = '2015-03-26'
            #sql = 'select c.start_time, a.item_juid, c.act_id from nd_jhs_parser_activity_item a join nd_jhs_mid_item_info b on a.item_juid = b.item_juid join nd_jhs_parser_activity c on a.act_id = c.act_id where c.start_time > \'%s\' and c.start_time < \'%s\' order by c.start_time,c.act_id'%(time_start,time_end)
            #time_start = '2015-03-24 20:00:00'
            #sql = 'select c.start_time, a.item_juid, c.act_id from nd_jhs_parser_activity_item a join nd_jhs_mid_item_info b on a.item_juid = b.item_juid join nd_jhs_parser_activity c on a.act_id = c.act_id where c.start_time = \'%s\' order by c.start_time,c.act_id'%(time_start)
            #sql = 'select c.start_time,a.item_juid,c.act_id from nd_jhs_rpt_item_info a join nd_jhs_mid_item_info b on a.item_juid = b.item_juid join nd_jhs_parser_activity c on b.activity_id = c.act_id where a.sell_through_rate > 100 and b.islock = 0 order by a.sell_through_rate desc;'
            #sql = 'select PA.start_time,RI.item_juid,RI.activity_id from nd_jhs_rpt_item_info RI join nd_jhs_parser_activity PA on RI.activity_id = PA.act_id left join nd_jhs_mid_item_info MI on RI.item_juid = MI.item_juid where RI.sell_through_rate is null and PA.act_id != 5652621 and MI.islock = 1 order by PA.start_time;'
            time_start = '2015-04-14 00:00:00'
            time_end = '2015-04-15 00:00:00 '
            sql = 'select b.start_time, a.item_juid, b.act_id from nd_jhs_mid_item_info a join nd_jhs_parser_activity b on a.activity_id = b.act_id where b.start_time >= \'%s\' and b.start_time < \'%s\' order by b.start_time,b.act_id'%(time_start,time_end)
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

                
            pool = ThreadPool(50)
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



