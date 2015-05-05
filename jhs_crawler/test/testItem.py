#-*- coding:utf-8 -*-
#!/usr/bin/env python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

sys.path.append('../')
import re
import random
import json
import time
import traceback
import threading
import base.Common as Common
import base.Config as Config
from db.MysqlAccess import MysqlAccess
from JHSItem import JHSItem

class testItem():
    '''A class of test item'''
    def __init__(self):
        # mysql
        self.mysqlAccess = MysqlAccess()

    def test(self):
        item = JHSItem()
        begin_time = Common.now()
        #url = 'http://detail.ju.taobao.com/home.htm?id=10000006139344&amp;item_id=41577218730'
        #item_id = '41577218730'
        #ju_id = '10000006139344'

        #url = 'http://detail.ju.taobao.com/home.htm?id=10000006179624&amp;item_id=43876136248'
        #item_id = '43876136248'
        #ju_id = '10000006179624'

        #url = 'http://detail.ju.taobao.com/home.htm?id=10000006194343&item_id=39105724540'
        #item_id = '39105724540'
        #ju_id = '10000006194343'

        #url = 'http://detail.ju.taobao.com/home.htm?id=10000006177132&amp;item_id=38397053227'
        #item_id = '38397053227'
        #ju_id = '10000006177132'

        # is lock
        #url = 'http://detail.ju.taobao.com/home.htm?id=10000006488668'
        #item_id = ''
        #ju_id = '10000006488668'
        
        #item = JHSItem()
        #_val = (ju_id,'',url,'',item_id,begin_time,1)
        #item.antPageLock(_val)
        #print item.outSqlForLock()

        """
        url = 'http://detail.ju.taobao.com/home.htm?id=10000006578995&item_id=43782195281'
        item_id = '43782195281'
        ju_id = '10000006578995'
        item = JHSItem()
        item.item_ju_url = url
        item.itemPage()
        """

        # info
        #_val = ('', '', '', '', 1, url, item_id, ju_id, '', begin_time, '', '')
        #item = JHSItem()
        #item.antPage(_val)
        #_iteminfosql_list = []
        #iteminfoSql = item.outTuple()
        #print iteminfoSql
        #_iteminfosql_list.append(iteminfoSql)
        #self.mysqlAccess.insertJhsItemInfo(_iteminfosql_list)
        #print item.item_juName,item.item_juDesc,',',item.item_sellerName

        """
        # day
        #self.item_juId,self.item_actId,self.item_actName,self.item_act_url,self.item_juName,self.item_ju_url,self.item_id,self.item_url,self.item_oriPrice,self.item_actPrice,self.crawling_begintime = val
        _val = (ju_id,'','','','',url,item_id,'','','',begin_time)
        item.antPageDay(_val)
        """

        # hour
        #_val = (ju_id,'',url,'',item_id,begin_time,1)
        #item.antPageHour(_val)
        #print item.crawler.history,len(item.crawler.history)
        #self.item_juId,self.item_actId,self.item_ju_url,self.item_act_url,self.item_id,self.crawling_begintime,self.hour_index = val

        """
        # update remind
        _val = (ju_id,'',url,'',item_id,begin_time)
        item.antPageUpdateRemind(_val)
        #self.item_juId,self.item_actId,self.item_ju_url,self.item_act_url,self.item_id,self.crawling_begintime = val
        """

        """
        url = 'http://detail.ju.taobao.com/home.htm?id=10000006662355&item_id=44528667214'
        item_id = '44528667214'
        ju_id = '10000006662355'
        item = JHSItem()
        item.item_ju_url = url
        item.item_groupCat_url = 'ju.taobao.com/jusp/nvzhuangpindao/tp.htm?#J_FixedNav'
        item.item_juId = ju_id
        item.item_id = item_id
        item.itemConfig()
        """
        page_data = '{"baseinfo":{"itemId":40436624435,"itemStatus":"blank","itemUrl":"//detail.ju.taobao.com/home.htm?id=10000006609266&item_id=40436624435","juId":10000006609266,"leftTime":"1天16小时7分钟","oetime":1430701199000,"ostime":1430445600000,"picGroup":["//gju2.alicdn.com/bao/uploaded/i2/10000078035589693/TB2TCpAcFXXXXc2XXXXXXXXXXXX_!!0-0-juitemmedia.jpg","//gju2.alicdn.com/bao/uploaded/i2/10000078472719326/TB274VscFXXXXc_XXXXXXXXXXXX_!!0-0-juitemmedia.jpg"],"picUrl":"//gju3.alicdn.com/bao/uploaded/i1/10000079981751900/TB2F.tocFXXXXb6XpXXXXXXXXXX_!!0-0-juitemmedia.jpg","picUrlM":"//gju3.alicdn.com/bao/uploaded/i1/10000079981751900/TB2F.tocFXXXXb6XpXXXXXXXXXX_!!0-0-juitemmedia.jpg","picUrlW":"//gju2.alicdn.com/bao/uploaded/i3/10000077503322787/TB26wFncFXXXXceXXXXXXXXXXXX_!!0-0-juitemmedia.jpg","push":false,"soldAmount":0},"bizTagText":"","merit":{"down":["束腰弹力 四季百搭"],"up":["不挑年龄身材","精选优质面料","五一满2件减3"]},"name":{"longName":"不挑年龄身材 穿出你的魅力，脱掉你的烦恼 精选优质面料 亲肤性极佳 轻薄防透 透气性强 耐穿不易变形 五一满2件减3 满3件减6元 满4件减11元 15天无理由退换，购物无忧","prefix":[],"shortName":"[ICCOJO]魔力百搭！弹力显瘦美腿打底裤 外穿小脚裤 不起球、不退色、不变形","tags":[{"tag":"by","text":"包邮"}],"title":"[ICCOJO]魔力百搭！弹力显瘦美腿打底裤 外穿小脚裤 不起球、不退色、不变形"},"price":{"actPrice":"39","discount":"2.1","discountText":"","hangtagPrice":false,"longerPrice":false,"origPrice":"189.00"},"promotion":{"coupon":"300"},"remind":{"fire":false,"remindNum":11172,"soldCount":0,"tag":"iyhq"}}'
        val = (page_data,1000,'女装','http://ju.taobao.com/jusp/nvzhuangpindao/tp.htm?#J_FixedNav','下装剧透',1)
        item = JHSItem()
        item.antPageGroupItem(val)
        print item.outGroupIteminfoSql()
        for v in item.outGroupIteminfoSql():
            print v
        


if __name__ == '__main__':
    t = testItem()
    t.test()


