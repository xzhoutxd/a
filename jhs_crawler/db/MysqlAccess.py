#-*- coding:utf-8 -*-
#!/usr/bin/env python

from sys import path
path.append(r'../')

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

    def insertJhsAct(self, args):
        try:
            sql  = 'replace into nd_jhs_parser_activity(crawl_time,act_id,category_id,category_name,act_position,act_platform,act_channel,act_name,act_url,act_desc,act_logopic_url,act_enterpic_url,act_status,act_sign,_act_ids,seller_id,seller_name,shop_id,shop_name,discount,act_soldcount,act_remindnum,act_coupon,act_coupons,brand_name,juhome,juhome_position,start_time,end_time) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            self.jhs_db.execute(sql, args)
        except Exception, e:
            print '# insertVipAct exception:', e

    def insertJhsItem(self, args):
        try:
            sql = 'replace into nd_jhs_parser_item(crawl_time,item_juid,act_id,act_name,act_url,item_position,item_ju_url,item_juname,item_judesc,item_jupic_url,item_id,item_url,seller_id,seller_name,shop_id,shop_name,shop_type,item_oriprice,item_actprice,discount,item_remindnum,item_soldcount,item_stock,item_prepare,item_favorites,item_promotions,cat_id,brand_name) value(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            self.jhs_db.execute(sql, args)
        except Exception, e:
            print '# insertVipAct exception:', e

    def insertJhsItemForHour(self, args):
        try:
            sql = 'replace into nd_jhs_parser_item_h(crawl_time,item_juid,act_id,act_name,item_juname,item_judesc,item_id,seller_id,seller_name,shop_id,shop_name,shop_type,item_oriprice,item_actprice,discount,item_remindnum,item_soldcount,item_stock,item_prepare,item_favorites,item_promotions,cat_id,brand_name) value(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            self.jhs_db.execute(sql, args)
        except Exception, e:
            print '# insertVipAct exception:', e



    # 即将上线
    def insertJhsActNext(self, args):
        try:
            sql  = 'replace into nd_jhs_parser_activity_next(crawl_time,act_id,category_id,category_name,act_position,act_platform,act_channel,act_name,act_url,act_desc,act_logopic_url,act_enterpic_url,act_status,act_sign,_act_ids,seller_id,seller_name,shop_id,shop_name,discount,act_soldcount,act_remindnum,act_coupon,act_coupons,brand_name,juhome,juhome_position,start_time,end_time) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            self.jhs_db.execute(sql, args)
        except Exception, e:
            print '# insertVipAct exception:', e


if __name__ == '__main__':
    my = MysqlAccess()
