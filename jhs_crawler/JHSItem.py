#-*- coding:utf-8 -*-
#!/usr/bin/env python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re
import random
import json
import time
import traceback
import threading
import base.Common as Common
import base.Config as Config
from base.TBCrawler import TBCrawler
from crawler.TBItem import TBItem
from crawler.TMItem import TMItem

class JHSItem():
    '''A class of Juhuasuan Item'''
    def __init__(self):
        # 商品页面抓取设置
        self.crawler = TBCrawler()
        self.crawling_time = Common.now() # 当前爬取时间
        self.crawling_begintime = '' # 本次抓取开始时间
        self.crawling_beginDate = '' # 本次爬取日期
        self.crawling_beginHour = '' # 本次爬取小时

        # 商品所在活动
        self.item_actId = '' # 商品所属活动Id
        self.item_actName = '' # 商品所属活动Name
        self.item_act_url = '' # 商品所属活动Url
        self.item_position = 0 # 商品所在活动位置
        self.item_act_starttime = 0.0 # 商品所在活动开团时间
        self.item_act_endtime = 0.0 # 商品所在活动结束时间

        # 商品信息
        self.item_juId = '' # 商品聚划算Id
        self.item_ju_url = '' # 商品聚划算链接
        self.item_id = '' # 商品Id
        self.item_url = '' # 商品链接
        self.item_juPic_url = '' # 商品聚划算展示图片链接
        self.item_juName = '' # 商品聚划算Name
        self.item_juDesc = '' # 商品聚划算说明
        self.item_catId = '' # 商品叶子类目Id
        self.item_catName = '' # 商品叶子类目Name
        self.item_brand = '' # 商品品牌
        self.item_isSoldout = 0 # 商品是否售罄 0:没有售罄,1:售罄
        self.item_isLock = 1 # 商品是否锁定 0:锁定,1:没有锁定 售罄和结束为0
        self.item_isLock_time = None # 抓到锁定的时间

        # 商品店铺
        self.item_sellerId = '' # 商品卖家Id
        self.item_sellerName = '' # 商品卖家Name
        self.item_shopId = '' # 商品店铺Id
        self.item_shopName = '' # 商品店铺Name
        self.item_shopType = 0 # 商品店铺类型 0:默认 1:天猫 2:集市

        # 商品交易
        self.item_oriPrice = '' # 商品原价
        self.item_actPrice = '' # 商品活动价
        self.item_discount = '' # 商品打折
        self.item_remindNum = '' # 商品关注人数
        self.item_soldCount = '' # 商品销售数量
        self.item_stock = '' # 商品库存
        self.item_promotions = [] # 商品其他优惠
        self.item_prepare = 0 # 商品活动前备货数
        self.item_favorites = 0 # 商品收藏数

        # 原数据信息
        self.item_pageData = '' # 商品所属数据项内容
        self.item_juPage = '' # 商品聚划算页面html内容
        self.item_pages = {} # 商品页面内请求数据列表

        # 每小时
        self.hour_index = 0 # 每小时的时刻

    # 商品初始化
    def initItem(self, page, actId, actName, actUrl, position, item_ju_url, item_id, item_juId, item_juPic_url, begin_time, start_time, end_time):
        # 商品所属数据项内容
        self.item_pageData = page
        self.item_pages['item-init'] = ('',page)
        # 商品所属活动Id
        self.item_actId = actId
        # 商品所属活动Name
        self.item_actName = actName
        # 商品所属活动Url
        self.item_act_url = actUrl
        # 商品所在活动位置
        self.item_position = position
        # 商品聚划算链接
        self.item_ju_url = item_ju_url
        # 商品Id
        self.item_id = item_id
        # 商品聚划算Id
        self.item_juId = item_juId
        # 商品活动展示图片Url
        self.item_juPic_url = item_juPic_url
        # 本次抓取开始时间
        self.crawling_begintime = begin_time
        # 商品所在活动的开团时间
        self.item_act_starttime = start_time
        # 商品所在活动的结束时间
        self.item_act_endtime = end_time

    # 聚划算商品页信息
    def itemConfig(self):
        # 聚划算商品页信息
        self.itemPage()
        page = self.item_juPage
        self.item_pages['item-home'] = (self.item_ju_url, page)
        m = re.search(r'<div id="content" class="detail">(.+?)</div> <!-- /content -->', page, flags=re.S)
        if m:
            i_page = m.group(1)
        else:
            i_page = page

        # 商品Id, 商品聚划算Id, 商品店铺类型 
        m = re.search(r'JU_DETAIL_DYNAMIC = {(.+?)};', i_page, flags=re.S)
        if m:
            m = re.search(r'"item_id": "(.+?)",.+?"id": "(.+?)",.+?"shopType": (.+?)\s+', i_page, flags=re.S)
            if m:
                self.item_id, self.item_juId, self.item_shopType = m.group(1), m.group(2), m.group(3)

        # 商品图片
        if self.item_juPic_url == '':
            m = re.search(r'<div class="item-pic-wrap">.+?<img.+?src="(.+?)".+?/>', i_page, flags=re.S)
            if m:
                self.item_juPic_url = m.group(1)
            else:
                m = re.search(r'<div class="normal-pic.+?<img.+?data-ks-imagezoom="(.+?)".+?/>', i_page, flags=re.S)
                if m:
                    self.item_juPic_url = m.group(1)

        # 商品链接
        m = re.search(r'<div class="normal-pic.+?<a href="(.+?)".+?>', i_page, flags=re.S)
        if m:
            self.item_url = m.group(1)
        else:
            m = re.search(r'<div class="pic-box soldout".+?<a href="(.+?)".+?>', i_page, flags=re.S)
            if m:
                self.item_url = m.group(1)

        # 商品卖家Id, 商品卖家Name
        m = re.search(r'<a class="sellername" href=".+?user_number_id=(.+?)".+?>(.+?)</a>', i_page, flags=re.S)
        if m:
            self.item_sellerId, self.item_sellerName = m.group(1), m.group(2)
        else:
            m = re.search(r'<a href=".+?user_number_id=(.+?)".+?>(.+?)</a>', i_page, flags=re.S)
            if m:
                self.item_sellerId, self.item_sellerName = m.group(1), m.group(2)

        # 商品聚划算Name
        m = re.search(r'data-shortName="(.+?)"', i_page, flags=re.S)
        if m:
            self.item_juName = m.group(1)
        else:
            m = re.search(r'<title>(.+?)-(聚划算.+?)</title>', i_page, flags=re.S)
            if m:
                self.item_juName = m.group(1)
            else:
                m = re.search(r'<h2 class="[name|title]+">(.+?)</h2>', i_page, flags=re.S)
                if m:
                    self.item_juName = m.group(1).strip()

        # 商品聚划算说明
        m = re.search(r'<div class="description">(.+?)</div>', i_page, flags=re.S)
        if m:
            description = Common.htmlContent(m.group(1).strip())
            self.item_juDesc = ' '.join(description.split())

        # 商品原价
        m = re.search(r'<.+? class="originPrice">(.+?)</.+?>', i_page, flags=re.S)
        if m:
            self.item_oriPrice = m.group(1).strip()
            if self.item_oriPrice.find(';') != -1:
                self.item_oriPrice = self.item_oriPrice.split(';')[1]
        else:
            m = re.search(r'data-originalprice="(.+?)"', i_page, flags=re.S)
            if m:
                self.item_oriPrice = m.group(1)

        # 商品活动价
        m = re.search(r'<.+? class="currentPrice.+?>.+?</small>(.+?)</.+?>', i_page, flags=re.S)
        if m:
            self.item_actPrice = m.group(1).strip()
        else:
            m = re.search(r'data-itemprice="(.+?)"', i_page, flags=re.S)
            if m:
                self.item_actPrice = m.group(1)

        # 商品打折
        m = re.search(r'data-polldiscount="(.+?)"', i_page, flags=re.S)
        if m:
            self.item_discount = m.group(1)

        if self.item_id == '' or self.item_juId == '' or self.item_url == '' or self.item_actPrice == '': raise Common.InvalidPageException("# itemConfig: not find ju item params,juid:%s,item_ju_url:%s,%s,%s,%s,%s,%s"%(str(self.item_juId), self.item_ju_url,self.item_id,self.item_juId,self.item_url,self.item_actPrice,self.item_discount))
        # 商品关注人数, 商品销售数量, 商品库存
        self.itemDynamic(i_page)

    # 商品详情页html
    def itemPage(self):
        if self.item_ju_url != '':
            page = self.crawler.getData(self.item_ju_url, self.item_act_url)
            if not page or page == '': raise Common.InvalidPageException("# antPageDay: not find ju item page,juid:%s,item_ju_url:%s"%(str(self.item_juId), self.item_ju_url))

            if re.search(r'<title>【聚划算】无所不能聚</title>', page, flags=re.S):
                raise Common.NoPageException("# itemConfig: not find ju item page, redirecting to juhuasuan home,juid:%s,item_ju_url:%s"%(str(self.item_juId), self.item_ju_url))
            elif type(self.crawler.history) is list and len(self.crawler.history) != 0 and re.search(r'302',str(self.crawler.history[0])):
                raise Common.NoPageException("# itemConfig: not find ju item page, redirecting to other page,juid:%s,item_ju_url:%s"%(str(self.item_juId), self.item_ju_url))
            self.item_juPage = page
        else:
            raise Common.NoPageException("# itemConfig: not find ju item page, url is null,juid:%s,item_ju_url:%s"%(str(self.item_juId), self.item_ju_url))

    def itemDynamic(self, page):
        # 商品关注人数, 商品销售数量, 商品库存
        i_getdata_url = ''
        ts = str(int(time.time()*1000)) + '_' + str(random.randint(0,9999))
        m = re.search(r'JU_DETAIL_DYNAMIC = {.+?"apiItemDynamicInfo": "(.+?)",.+?};', page, flags=re.S)
        if m:
            i_getdata_url = m.group(1) + '?item_id=%s'%self.item_id + '&id=%s'%self.item_juId + '&_ksTS=%s'%ts
        else:
            i_getdata_url = 'http://dskip.ju.taobao.com/detail/json/item_dynamic.htm' + '?item_id=%s'%self.item_id + '&id=%s'%self.item_juId + '&_ksTS=%s'%ts

        if i_getdata_url:
            json_str = self.crawler.getData(i_getdata_url, self.item_ju_url)
            if not json_str or json_str == '': raise Common.InvalidPageException("# itemDynamic: not find ju item dynamic page,juid:%s,item_ju_url:%s"%(str(self.item_juId), self.item_ju_url))
            self.item_pages['item-dynamic'] = (i_getdata_url, json_str)
            if json_str and json_str != '':
                m = re.search(r'"success":\s*"false"', json_str, flags=re.S)
                if m:
                    m = re.search(r'"data":\s*"NULL_ITEM.+?', json_str, flags=re.S)
                    if m:
                        print json_str
                        raise Common.NoItemException("# itemDynamic: find dynamic page null,juid:%s,item_ju_url:%s"%(str(self.item_juId), self.item_ju_url))
                    else:
                        raise Common.InvalidPageException("# itemDynamic: find dynamic page false,juid:%s,item_ju_url:%s"%(str(self.item_juId), self.item_ju_url))

                m = re.search(r'"soldCount":\s*"(.+?)",', json_str, flags=re.S)
                if m:
                    self.item_soldCount = m.group(1)

                m = re.search(r'"remindNum":\s*"(.+?)",', json_str, flags=re.S)
                if m:
                    remindNum = m.group(1)
                    if self.item_soldCount == '':
                        self.item_remindNum = remindNum
                    else:
                        if remindNum != '' and int(remindNum) != 0:
                            self.item_remindNum = remindNum

                m = re.search(r'"stock":\s*"(.+?)",', json_str, flags=re.S)
                if m:           
                    self.item_stock = m.group(1)

                if self.item_soldCount != '' and int(self.item_soldCount) != 0 and self.item_stock != '' and int(self.item_stock) == 0:
                    self.item_isSoldout = 1

    # 商品锁定信息
    def itemLock(self, page):
        if page != '':
            m = re.search(r'JU_DETAIL_DYNAMIC = {.+?"isLock":\s*"(.+?)",.+?};', page, flags=re.S)
            if m:
                isLock = m.group(1)
                if isLock != '':
                    self.item_isLock = isLock
                    self.item_isLock_time = Common.now()
            
    # 商品其他优惠信息
    def itemPromotiton(self):
        promot_url = 'http://dskip.ju.taobao.com/promotion/json/get_shop_promotion.do?ju_id=%s'%str(self.item_juId)
        promot_page = self.crawler.getData(promot_url, self.item_ju_url)
        if not promot_page and promot_page == '': raise Common.InvalidPageException("# itemPromotion: not find promotion page")
        if promot_page and promot_page != '':
            self.item_pages['item-shoppromotion'] = (promot_url,promot_page)
            result = json.loads(promot_page)
            if result.has_key('success') and result.has_key('model') and result['model'] != []:
                for model in result['model']:
                    title = ''
                    if model.has_key('title'):
                        title = model['title']
                    if model.has_key('promLevels') and model['promLevels'] != []:
                        for level in model['promLevels']:
                            if level.has_key('title'):
                                self.item_promotions.append('%s:%s'%(title,level['title']))

    # 执行
    def antPage(self, val):
        page, actId, actName, actUrl, position, item_ju_url, item_id, item_juId, item_juPic_url, begin_time, start_time,end_time = val
        self.initItem(page, actId, actName, actUrl, position, item_ju_url, item_id, item_juId, item_juPic_url, begin_time, start_time, end_time)
        self.itemConfig()
        self.itemPromotiton()
        page_datepath = 'item/main/' + time.strftime("%Y/%m/%d/%H/", time.localtime(self.crawling_begintime))
        self.writeLog(page_datepath)

    # Day
    def antPageDay(self, val):
        self.item_juId,self.item_actId,self.item_actName,self.item_act_url,self.item_juName,self.item_ju_url,self.item_id,self.item_url,self.item_oriPrice,self.item_actPrice,self.crawling_begintime = val

        # 本次抓取开始日期
        self.crawling_beginDate = time.strftime("%Y-%m-%d", time.localtime(self.crawling_begintime))
        # 本次抓取开始小时
        self.crawling_beginHour = time.strftime("%H", time.localtime(self.crawling_begintime))

        # 商品关注人数, 商品销售数量, 商品库存
        page = ''
        self.itemDynamic(page)
        if self.item_soldCount == '' or self.item_stock == '':
            # 聚划算商品页信息
            self.itemPage()
            self.item_pages['item-home-day'] = (self.item_ju_url, self.item_juPage)
            self.itemDynamic(self.item_juPage)
            if self.item_soldCount == '' or self.item_stock == '':
                print '# item not get soldcount or stock,item_juid:%s,item_id:%s,item_actid:%s'%(str(self.item_juId),str(self.item_id),str(self.item_actId))
        page_datepath = 'item/day/' + time.strftime("%Y/%m/%d/%H/", time.localtime(self.crawling_begintime))
        self.writeLog(page_datepath)

    # Hour
    def antPageHour(self, val):
        self.item_juId,self.item_actId,self.item_ju_url,self.item_act_url,self.item_id,self.crawling_begintime,self.hour_index = val
        # 商品关注人数, 商品销售数量, 商品库存
        self.itemDynamic(self.item_juPage)
        if self.item_soldCount == '' or self.item_stock == '':
            # 聚划算商品页信息
            self.itemPage()
            self.item_pages['item-home-hour'] = (self.item_ju_url, self.item_juPage)
            # 商品关注人数, 商品销售数量, 商品库存
            self.itemDynamic(self.item_juPage)
            if self.item_soldCount == '' or self.item_stock == '':
                print '# item not get soldcount or stock,item_juid:%s,item_id:%s,item_actid:%s'%(str(self.item_juId),str(self.item_id),str(self.item_actId))
        page_datepath = 'item/hour/' + time.strftime("%Y/%m/%d/%H/", time.localtime(self.crawling_begintime))
        self.writeLog(page_datepath)

    # item islock
    def antPageLock(self, val):
        self.item_juId,self.item_actId,self.item_ju_url,self.item_act_url,self.item_id,self.crawling_begintime,self.hour_index = val
        page = ''
        # 聚划算商品页信息
        self.itemPage()
        self.item_pages['item-home-hour'] = (self.item_ju_url, self.item_juPage)
        # 商品锁定信息
        self.itemLock(page)
        page_datepath = 'item/hour/' + time.strftime("%Y/%m/%d/%H/", time.localtime(self.crawling_begintime))
        self.writeLog(page_datepath)

    # update remind
    def antPageUpdateRemind(self, val):
        self.item_juId,self.item_actId,self.item_ju_url,self.item_act_url,self.item_id,self.crawling_begintime = val
        # 商品关注人数
        page = ''
        self.itemDynamic(page)
        if self.item_remindNum == '':
            # 聚划算商品页信息
            self.itemPage()
            self.item_pages['item-home-update'] = (self.item_ju_url, self.item_juPage)
            # 商品关注人数, 商品销售数量, 商品库存
            self.itemDynamic(self.item_juPage)
            if self.item_remindNum == '':
                print '# item not get remind num,item_juid:%s,item_id:%s,item_actid:%s'%(str(self.item_juId),str(self.item_id),str(self.item_actId))
        page_datepath = 'item/update/' + time.strftime("%Y/%m/%d/%H/", time.localtime(self.crawling_begintime))
        self.writeLog(page_datepath)

    # 输出item info SQL
    def outIteminfoSql(self):
        return (Common.time_s(self.crawling_time),str(self.item_juId),str(self.item_actId),self.item_actName,self.item_act_url,str(self.item_position),self.item_ju_url,self.item_juName,self.item_juDesc,self.item_juPic_url,self.item_id,self.item_url,str(self.item_sellerId),self.item_sellerName,str(self.item_shopType),str(self.item_oriPrice),str(self.item_actPrice),str(self.item_discount),str(self.item_remindNum),';'.join(self.item_promotions),self.item_act_starttime,self.item_act_endtime)

    # 每天的SQL
    def outSqlForDay(self):
        return (Common.time_s(self.crawling_time),str(self.item_juId),str(self.item_actId),self.item_actName,self.item_act_url,self.item_juName,self.item_ju_url,self.item_id,self.item_url,str(self.item_oriPrice),str(self.item_actPrice),str(self.item_soldCount),str(self.item_stock),self.crawling_beginDate,self.crawling_beginHour)

    # 每小时的SQL
    def outSqlForHour(self):
        return (Common.date_s(self.crawling_time),str(self.hour_index),str(self.item_juId),str(self.item_actId),str(self.item_soldCount),str(self.item_stock))

    # 商品锁定信息
    def outSqlForLock(self):
        try:
            return (self.item_juId,Common.time_s(self.item_isLock_time),self.item_isLock)
        except Exception as e:
            print '# out item Lock Sql err:',e
            return None

    # 更新item remind SQL
    def outSqlForUpdateRemind(self):
        return (str(self.item_juId),str(self.item_remindNum))

    # 输出Tuple
    def outTuple(self):
        #sql = self.outSql()
        #saleSql = self.outSaleSqlForHour()
        #stockSql = self.outStockSqlForHour()
        iteminfoSql = self.outIteminfoSql()
        #return (sql, saleSql, stockSql, iteminfoSql)
        return iteminfoSql

    # 输出每天Tuple
    def outTupleDay(self):
        sql = self.outSqlForDay()
        return sql

    # 输出每小时Tuple
    def outTupleHour(self):
        sql = self.outSqlForHour()
        lockSql = self.outSqlForLock()
        return (sql,lockSql)

    # 更新item remind Tuple
    def outTupleUpdateRemind(self):
        sql = self.outSqlForUpdateRemind()
        return sql

    # 输出商品的网页
    def outItemPage(self,crawl_type):
        if self.crawling_begintime != '':
            time_s = time.strftime("%Y%m%d%H", time.localtime(self.crawling_begintime))
        else:
            time_s = time.strftime("%Y%m%d%H", time.localtime(self.crawling_time))
        # timeStr_jhstype_webtype_item_crawltype_itemjuid
        key = '%s_%s_%s_%s_%s_%s' % (time_s,Config.JHS_TYPE,'1','item',crawl_type,str(self.item_juId))
        pages = {}
        for p_tag in self.item_pages.keys():
            p_url, p_content = self.item_pages[p_tag]
            f_content = '<!-- url=%s --> %s' %(p_url, p_content)
            pages[p_tag] = f_content.strip()
        return (key,pages)

    # 写html文件
    def writeLog(self,time_path):
        try:
            pages = self.outItemLog()
            for page in pages:
                filepath = Config.pagePath + time_path + page[2]
                Config.createPath(filepath)
                #if not os.path.exists(filepath):
                #    os.mkdir(filepath)
                filename = filepath + page[0]
                fout = open(filename, 'w')
                fout.write(page[3])
                fout.close()
        except Exception as e:
            print '# exception err in writeLog info:',e

    # 输出抓取的网页log
    def outItemLog(self):
        pages = []
        for p_tag in self.item_pages.keys():
            p_url, p_content = self.item_pages[p_tag]

            # 网页文件名
            f_path = '%s_item/%s/' %(self.item_actId, self.item_juId)
            f_name = '%s-%s_%s_%d.htm' %(self.item_actId, self.item_juId, p_tag, self.crawling_time)

            # 网页文件内容
            f_content = '<!-- url=%s -->\n%s\n' %(p_url, p_content)
            pages.append((f_name, p_tag, f_path, f_content))

        return pages

def test():
    #(itemdata, actId, actName, actUrl, position, item_ju_url, item_id, item_juId, item_juPic_url)

    url = 'http://detail.ju.taobao.com/home.htm?id=10000006058022&amp;item_id=42860458287'
    item_id = '42860458287'
    ju_id = '10000006058022'
    item = JHSItem()
    begin_time = Common.now()
    val = ('', '', '', '', 1, url, item_id, ju_id, '', begin_time, '', '')
    item.antPage(val)
    print item.outTuple()
    #item.outItem()
    #print item.item_remindNum
    #print item.item_soldCount
    #print item.item_stock

if __name__ == '__main__':
    test()

