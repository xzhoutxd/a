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
        self.db = MySQLdb.connect("192.168.1.35","root","zhouxin","jhs_113",charset='utf8')
        #self.db = MySQLdb.connect("192.168.1.113","jhs","123456","jhs",charset='utf8')

        # prepare a cursor object using cursor() method
        self.db_cursor = self.db.cursor()

    def fix_stock(self,item):
        filepath_m = '/home/har/jhs/jhsdata/page/item/main/'

        item_c_time = item[0]
        ju_id = item[1]
        act_id = item[2]
        print item_c_time,ju_id,act_id

        need_file = ''
        time_s = item_c_time.strftime('%Y-%m-%d %H:%M:%S')
        filepath = filepath_m + time.strftime('%Y/%m/%d/%H/',time.strptime(time_s, "%Y-%m-%d %H:%M:%S")) + '%s_item/%s/'%(str(act_id),str(ju_id))
        if os.path.exists(filepath):
            file_list = os.listdir(filepath)
            for f in file_list:
                m = re.search(r'\d+-\d+_item-home_\d+.htm', f, flags=re.S)
                if m:
                    need_file = (filepath + f, str(ju_id), str(act_id))
        else:
            print '# file path not find: ',filepath

        item_list = []
        if need_file and need_file != '':
            fout = open(need_file[0], 'r')
            s = fout.read()
            fout.close()

            i_page = s
            item_sellerId, item_sellerName = '', ''
            # 商品卖家Id, 商品卖家Name
            m = re.search(r'<a class="sellername" href=".+?user_number_id=(.+?)".+?>(.+?)</a>', i_page, flags=re.S)
            if m:
                item_sellerId, item_sellerName = m.group(1), m.group(2)
            else:
                m = re.search(r'<a href=".+?user_number_id=(.+?)".+?>(.+?)</a>', i_page, flags=re.S)
                if m:
                    item_sellerId, item_sellerName = m.group(1), m.group(2)

            item_juName = ''
            # 商品聚划算Name
            m = re.search(r'<title>(.+?)-(.+?)</title>', i_page, flags=re.S)
            if m:
                item_juName = m.group(1)
            else:
                m = re.search(r'data-shortName="(.+?)"', i_page, flags=re.S)
                if m:
                    item_juName = m.group(1)
                else:
                    m = re.search(r'<h2 class="[name|title]+">(.+?)</h2>', i_page, flags=re.S)
                    if m:
                        item_juName = m.group(1).strip()

            item_actPrice = ''
            # 商品活动价
            m = re.search(r'<.+? class="currentPrice.+?>.+?</small>(.+?)</.+?>', i_page, flags=re.S)
            if m:
                item_actPrice = m.group(1).strip()
            else:
                m = re.search(r'data-itemprice="(.+?)"', i_page, flags=re.S)
                if m:
                    item_actPrice = m.group(1)

            if item_sellerId != '' and item_sellerName != '' and item_juName != '' and item_actPrice != '':
                item_list.append((need_file[1],need_file[2],item_juName,item_sellerId,item_sellerName,item_actPrice))
            else:
                print '# no get item params:',need_file[1],need_file[2],item_sellerId,item_sellerName,item_juName,item_actPrice

        print '# stock item num:', len(item_list)

        for r in item_list:
            #print r
            update_sql = 'update nd_jhs_parser_item set item_juname=\'%s\',seller_id=\'%s\',seller_name=\'%s\',item_actprice=\'%s\' where item_juid = %s and act_id = %s'%(str(r[2]),str(r[3]),str(r[4]),str(r[5]),str(r[0]),str(r[1]))
            #print update_sql
            try:
                self.db_cursor.execute(self.SET_NAMES_QUERY)
                self.db_cursor.execute(update_sql)
                self.db.commit()
            except StandardError as err:
                self.db.rollback()
                print err

            update_sql = 'update nd_jhs_parser_item_hour set item_juname=\'%s\',item_actprice=\'%s\' where item_juid = %s and act_id = %s'%(str(r[2]),str(r[5]),str(r[0]),str(r[1]))
            #print update_sql
            try:
                self.db_cursor.execute(self.SET_NAMES_QUERY)
                self.db_cursor.execute(update_sql)
                self.db.commit()
            except StandardError as err:
                self.db.rollback()
                print err

            update_sql = 'update nd_jhs_parser_item_stock_h set item_juname=\'%s\',item_actprice=\'%s\' where item_juid = %s and act_id = %s'%(str(r[2]),str(r[5]),str(r[0]),str(r[1]))
            #print update_sql
            try:
                self.db_cursor.execute(self.SET_NAMES_QUERY)
                self.db_cursor.execute(update_sql)
                self.db.commit()
            except StandardError as err:
                self.db.rollback()

    def run_fix(self):
        time_start = '2015-02-10 19:00:00'
        stock_sql = 'select crawl_time, item_juid, act_id from nd_jhs_parser_item where crawl_time > \'%s\''%(time_start)

        try:
            self.db_cursor.execute(self.SET_NAMES_QUERY)
            self.db_cursor.execute(stock_sql)
            results = self.db_cursor.fetchall()
        except StandardError as err:
            print err

        print '# date:',time_start
        print '# item num:',len(results)
        #print results

        s_results = []
        for item in results:
            #s_results.append((item[0].strftime('%Y-%m-%d %H:%M:%S'),item[1],item[2]))
            #s_results.append((str(item[0]),item[1],item[2]))
            self.fix_stock(item)
            
        self.db_cursor.close()
        #关闭    
        self.db.close()

if __name__ == '__main__':
    f = FixStock()
    f.run_fix()



