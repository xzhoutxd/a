#-*- coding:utf-8 -*-
#!/usr/bin/env python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import traceback
import MysqlPool
import base.Config as Config

class MysqlAccess():
    '''A class of mysql db access'''
    def __init__(self):
        # 聚划算
        self.jhs_db = MysqlPool.g_jhsDbPool

    def __del__(self):
        # 聚划算
        self.jhs_db = None

    # 新加活动
    def insertJhsAct(self, args):
        try:
            sql  = 'replace into nd_jhs_parser_activity(crawl_time,act_id,category_id,category_name,act_position,act_platform,act_channel,act_name,act_url,act_desc,act_logopic_url,act_enterpic_url,act_status,act_sign,_act_ids,seller_id,seller_name,shop_id,shop_name,discount,act_soldcount,act_remindnum,act_coupon,act_coupons,brand_name,juhome,juhome_position,start_time,end_time,c_begindate,c_beginhour) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            self.jhs_db.execute(sql, args)
        except Exception, e:
            print '# insert Jhs Act exception:', e

    # 新加商品
    def insertJhsItem(self, args):
        try:
            sql = 'replace into nd_jhs_parser_item(crawl_time,item_juid,act_id,act_name,act_url,item_position,item_ju_url,item_juname,item_judesc,item_jupic_url,item_id,item_url,seller_id,seller_name,shop_id,shop_name,shop_type,item_oriprice,item_actprice,discount,item_remindnum,item_soldcount,item_stock,item_prepare,item_favorites,item_promotions,cat_id,brand_name) value(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            self.jhs_db.execute(sql, args)
        except Exception, e:
            print '# insert Jhs Item exception:', e

    # 即将上线活动
    def insertJhsActComing(self, args):
        try:
            sql  = 'replace into nd_jhs_parser_activity_coming(crawl_time,act_id,category_id,category_name,act_position,act_platform,act_channel,act_name,act_url,act_desc,act_logopic_url,act_enterpic_url,act_status,act_sign,_act_ids,seller_id,seller_name,shop_id,shop_name,discount,act_soldcount,act_remindnum,act_coupon,act_coupons,brand_name,juhome,juhome_position,start_time,end_time,c_begindate,c_beginhour) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            self.jhs_db.execute(sql, args)
        except Exception, e:
            print '# insert Jhs Act for Coming soon exception:', e

    # 执行SQL
    def executeSql(self, sql):
        try:
            self.jhs_db.execute(sql)
        except Exception, e:
            print '# execute Sql exception:', e

    # 需要每天抓取的活动
    def insertJhsActDayalive(self, args):
        try:
            sql = 'replace into nd_jhs_parser_activity_alive_day(act_id,act_name,act_url,_start_time,_end_time,c_begindate,c_beginhour) values(%s,%s,%s,%s,%s,%s,%s)'
            self.jhs_db.execute(sql, args)
        except Exception, e:
            print '# insert Jhs alive act for day exception:', e


    # 查找需要每天抓取的活动
    def selectJhsActDayalive(self, args):
        # 非俪人购
        # 当前时间减一天小于结束时间，需要每天抓取
        try:
            sql = 'select * from nd_jhs_parser_activity_alive_day where _end_time >= %s'
            self.jhs_db.execute(sql, args)
        except Exception, e:
            print '# select Jhs alive act for day exception:', e

    # 需要小时抓取的活动
    def insertJhsActHouralive(self, args):
        try:
            sql = 'replace into nd_jhs_parser_activity_alive_hour(act_id,act_name,act_url,_start_time,_end_time,c_begindate,c_beginhour) values(%s,%s,%s,%s,%s,%s,%s)'
            self.jhs_db.execute(sql, args)
        except Exception, e:
            print '# insert Jhs alive act for hour exception:', e


    # 查找需要小时抓取的活动
    def selectJhsActHouralive(self, args):
        # 非俪人购
        # 当前时间减去最大时间段小于开始时间，当前时间减去最小时间段大于开始时间，需要每小时抓取
        try:
            sql = 'select * from nd_jhs_parser_activity_alive_hour where _start_time > %s and _start_time < %s'
            self.jhs_db.execute(sql, args)
        except Exception, e:
            print '# select Jhs alive act for hour exception:', e

    # 每天抓取商品
    def insertJhsItemForDay(self, args):
        try:
            sql = 'replace into nd_jhs_parser_item_day(crawl_time,item_juid,act_id,act_name,act_url,item_juname,item_ju_url,item_id,item_url,item_oriprice,item_actprice,item_soldcount,item_stock,c_begindate,c_beginhour) value(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            self.jhs_db.execute(sql, args)
        except Exception, e:
            print '# insert Jhs Item for day exception:', e

    # 每小时抓取商品
    def insertJhsItemForHour(self, args):
        try:
            sql = 'replace into nd_jhs_parser_item_hour(crawl_time,item_juid,act_id,act_name,act_url,item_juname,item_ju_url,item_id,item_url,item_oriprice,item_actprice) value(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            self.jhs_db.execute(sql, args)
        except Exception, e:
            print '# insert Jhs Item for hour exception:', e

    # 更新每小时商品销量
    def updateJhsItemSoldcountForHour(self, args):
        try:
            sql = 'update nd_jhs_parser_item_hour set %s=%s where crawl_time = %s and item_juid = %s and act_id = %s'
            self.jhs_db.execute(sql, args)
        except Exception, e:
            print '# update Jhs Item for hour exception:', e

if __name__ == '__main__':
    my = MysqlAccess()
