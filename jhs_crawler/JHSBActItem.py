#-*- coding:utf-8 -*-
#!/usr/bin/env python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re
import random
import json
import time
import threading
import base.Common as Common
import base.Config as Config
from base.TBCrawler import TBCrawler

class JHSBActItem():
    '''A class of brand Item'''
    def __init__(self):
        # 品牌团抓取设置
        self.crawler    = TBCrawler()
        self.crawling_time   = Common.now()
        self.crawling_beginDate = ''
        self.crawling_beginHour = ''

        # 类别
        self.brandact_platform = '聚划算-pc' # 品牌团所在平台
        self.brandact_channel = '品牌闪购' # 品牌团所在频道
        self.brandact_catgoryId = 0 # 品牌团所在类别Id
        self.brandact_catgoryName = '' # 品牌团所在类别Name
        self.brandact_position = 0 # 品牌团所在类别位置

        # 是否在首页展示
        self.brandact_inJuHome = 0 # 是否在首页展示,0:不在,1:存在
        self.brandact_juHome_position = '' # 在首页展示的位置

        # 品牌团信息
        self.brandact_id = '' # 品牌团Id
        self.brandact_url = '' # 品牌团链接
        self.brandact_name = '' # 品牌团Name
        self.brandact_desc = '' # 品牌团描述
        self.brandact_logopic_url = '' # 品牌团Logo图片链接
        self.brandact_enterpic_url = '' # 品牌团展示图片链接
        self.brandact_starttime = 0.0 # 品牌团开团时间
        self.brandact_endtime = 0.0 # 品牌团结束时间
        self.brandact_status = '' # 品牌团状态
        self.brandact_sign = 1 # 品牌团标识 1:普通品牌团,2:拼团,3:俪人购
        self.brandact_other_ids = '' # 如果是拼团, 其他团的ID
        self.brandact_brand = '' # 品牌团品牌信息

        # 店铺信息
        self.brandact_sellerId = '' # 品牌团卖家Id
        self.brandact_sellerName = '' # 品牌团卖家Name (回填)
        self.brandact_shopId = '' # 品牌团店铺Id (回填)
        self.brandact_shopName = '' # 品牌团店铺Name (回填)

        # 品牌团交易信息
        self.brandact_soldCount = 0 # 品牌团成交数
        self.brandact_remindNum = 0 # 品牌团关注人数
        self.brandact_discount = '' # 品牌团打折
        self.brandact_coupon = 0 # 品牌团优惠券, 默认0没有
        self.brandact_coupons = [] # 优惠券内容list

        # 原数据信息
        self.brandact_pagedata = '' # 品牌团所在数据项所有内容
        self.brandact_page = '' # 品牌团页面html内容
        self.brandact_pages = {} # 品牌页面内请求数据列表

    # 品牌团初始化
    def initItem(self, page, catId, catName, position, begin_date, begin_hour):
        # 品牌团所在数据项内容
        self.brandact_pagedata = page
        self.brandact_pages['act-init'] = ('', page)
        # 品牌团所在类别Id
        self.brandact_catgoryId = catId
        # 品牌团所在类别Name
        self.brandact_catgoryName = catName
        # 品牌团所在类别位置
        self.brandact_position = position
        # 本次抓取开始日期
        self.crawling_beginDate = begin_date
        # 本次抓取开始小时
        self.crawling_beginHour = begin_hour

    # Configuration
    def itemConfig(self):
        # 基本信息
        if self.brandact_pagedata.has_key('baseInfo'):
            b_baseInfo = self.brandact_pagedata['baseInfo']
            if b_baseInfo.has_key('activityId') and b_baseInfo['activityId']:
                # 品牌团Id
                self.brandact_id = b_baseInfo['activityId']
            if b_baseInfo.has_key('activityUrl') and b_baseInfo['activityUrl']:
                # 品牌团链接
                self.brandact_url = b_baseInfo['activityUrl']
                if self.brandact_url.find('ladygo.tmall.com') != -1:
                    # 品牌团标识
                    self.brandact_sign = 3
            if b_baseInfo.has_key('ostime') and b_baseInfo['ostime']:
                # 品牌团开团时间
                self.brandact_starttime = b_baseInfo['ostime']
            if b_baseInfo.has_key('oetime') and b_baseInfo['oetime']:
                # 品牌团结束时间
                self.brandact_endtime = b_baseInfo['oetime']
            if b_baseInfo.has_key('activityStatus') and b_baseInfo['activityStatus']:
                # 品牌团状态
                self.brandact_status = b_baseInfo['activityStatus']
            if b_baseInfo.has_key('sellerId') and b_baseInfo['sellerId']:
                # 品牌团卖家Id
                self.brandact_sellerId = b_baseInfo['sellerId']
            if b_baseInfo.has_key('otherActivityIdList') and b_baseInfo['otherActivityIdList']:
                # 如果是拼团, 其他团的ID
                self.brandact_other_ids = str(self.brandact_id) + ',' + ','.join(b_baseInfo['otherActivityIdList'])
                # 品牌团标识
                self.brandact_sign = 2
            else:
                self.brandact_other_ids = str(self.brandact_id)

        if self.brandact_pagedata.has_key('materials'):
            b_materials = self.brandact_pagedata['materials']
            if b_materials.has_key('brandLogoUrl') and b_materials['brandLogoUrl']:
                # 品牌团Logo图片链接
                self.brandact_logopic_url = b_materials['brandLogoUrl']
            if b_materials.has_key('logoText') and b_materials['logoText']:
                # 品牌团Name
                self.brandact_name = b_materials['logoText']
            if b_materials.has_key('brandDesc') and b_materials['brandDesc']:
                # 品牌团描述
                self.brandact_desc = b_materials['brandDesc']
            if b_materials.has_key('newBrandEnterImgUrl') and b_materials['newBrandEnterImgUrl']:
                # 品牌团展示图片链接
                self.brandact_enterpic_url = b_materials['newBrandEnterImgUrl']
            elif b_materials.has_key('brandEnterImgUrl') and b_materials['brandEnterImgUrl']:
                # 品牌团展示图片链接
                self.brandact_enterpic_url = b_materials['brandEnterImgUrl']

        if self.brandact_pagedata.has_key('remind'):
            b_remind = self.brandact_pagedata['remind']
            if b_remind.has_key('soldCount') and b_remind['soldCount']:
                # 品牌团成交数
                self.brandact_soldCount = b_remind['soldCount']
            if b_remind.has_key('remindNum') and b_remind['remindNum']:
                # 品牌团想买人数
                self.brandact_remindNum = b_remind['remindNum']

        if self.brandact_pagedata.has_key('price'):
            b_price = self.brandact_pagedata['price']
            if b_price.has_key('discount') and b_price['discount']:
                # 品牌团打折
                self.brandact_discount = b_price['discount']
            if b_price.has_key('hasCoupon'):
                if b_price['hasCoupon']:
                  # 品牌团优惠券 有优惠券
                  self.brandact_coupon = 1
        
        # 品牌团页面html
        if self.brandact_url != '':
            data = self.crawler.getData(self.brandact_url, Config.ju_brand_home)
            if not data and data == '': raise Common.InvalidPageException("# itemConfig:not fing act page,actid:%s,act_url:%s"%(str(self.brandact_id), self.brandact_url))
            if data and data != '':
                self.brandact_page = data
                self.brandact_pages['act-home'] = (self.brandact_url, data)

    # 品牌团优惠券
    def brandActConpons(self):
        # 优惠券
        #m = re.search(r'<div id="content">(.+?)</div>\s+<div class="crazy-wrap">', self.brandact_page, flags=re.S)
        #if m:
        #    page = m.group(1)
        #    p = re.compile(r'<div class=".+?">\s*<div class="c-price">\s*<i>.+?</i><em>(.+?)</em></div>\s*<div class="c-desc">\s*<span class="c-title"><em>(.+?)</em>(.+?)</span>\s*<span class="c-require">(.+?)</span>\s*</div>', flags=re.S)
        #    for coupon in p.finditer(page):
        #        self.brandact_coupons.append(''.join(coupon.groups()))
        p = re.compile(r'<div class=".+?J_coupons">\s*<div class="c-price">(.+?)</div>\s*<div class="c-desc">\s*<span class="c-title">(.+?)</span>\s*<span class="c-require">(.+?)</span>\s*</div>', flags=re.S)
        for coupon in p.finditer(self.brandact_page):
            price, title, require = coupon.group(1).strip(), coupon.group(2).strip(), coupon.group(3).strip()
            i_coupons = ''
            m = re.search(r'<em>(.+?)</em>', price, flags=re.S)
            if m:
                i_coupons = i_coupons + m.group(1)
            else:
                i_coupons = i_coupons + ''.join(price.spilt())

            m = re.search(r'<em>(.+?)</em>(.+?)$', title, flags=re.S)
            if m:
                i_coupons = i_coupons + ''.join(m.groups())
                #i_coupons = i_coupons + str(m.group(1)) + str(m.group(2))
            else:
                i_coupons = i_coupons + ''.join(title.split())

            i_coupons = i_coupons + require

            self.brandact_coupons.append(i_coupons)

    # 执行
    #def antPage(self, page, catId, catName, position, begin_date, begin_hour):
    def antPage(self, val):
        page, catId, catName, position, begin_date, begin_hour = val
        self.initItem(page, catId, catName, position, begin_date, begin_hour)
        self.itemConfig()
        self.brandActConpons()
        #self.outItem()

    # 输出抓取的网页log
    def outItemLog(self):
        pages = []
        for p_tag in self.brandact_pages.keys():
            p_url, p_content = p_val

            # 网页文件名
            f_path = '%s_item/' %(self.brandact_id)
            f_name = '%s-%s_%d.htm' %(self.brandact_id, p_tag, self.crawling_time)

            # 网页文件内容
            f_content = '<!-- url=%s -->\n%s\n' %(p_url, p_content)
            pages.append((f_name, p_tag, f_path, f_content))

        return pages

    def outSql(self):
        #return (Common.time_s(self.crawling_time),str(self.brandact_id),str(self.brandact_catgoryId),self.brandact_catgoryName,str(self.brandact_position),self.brandact_platform,self.brandact_channel,self.brandact_name,self.brandact_url,self.brandact_desc,self.brandact_logopic_url,self.brandact_enterpic_url,self.brandact_status,str(self.brandact_sign),self.brandact_other_ids,str(self.brandact_sellerId),self.brandact_sellerName,str(self.brandact_shopId),self.brandact_shopName,self.brandact_discount,str(self.brandact_soldCount),str(self.brandact_remindNum),str(self.brandact_coupon),';'.join(self.brandact_coupons),self.brandact_brand,str(self.brandact_inJuHome),str(self.brandact_juHome_position),Common.time_s(float(self.brandact_starttime)/1000),Common.time_s(float(self.brandact_endtime)/1000))
        return (Common.time_s(self.crawling_time),str(self.brandact_id),str(self.brandact_catgoryId),self.brandact_catgoryName,str(self.brandact_position),self.brandact_platform,self.brandact_channel,self.brandact_name,self.brandact_url,self.brandact_desc,self.brandact_logopic_url,self.brandact_enterpic_url,self.brandact_status,str(self.brandact_sign),self.brandact_other_ids,str(self.brandact_sellerId),self.brandact_sellerName,str(self.brandact_shopId),self.brandact_shopName,self.brandact_discount,str(self.brandact_soldCount),str(self.brandact_remindNum),str(self.brandact_coupon),';'.join(self.brandact_coupons),self.brandact_brand,str(self.brandact_inJuHome),str(self.brandact_juHome_position),Common.time_s(float(self.brandact_starttime)/1000),Common.time_s(float(self.brandact_endtime)/1000),self.crawling_beginDate,self.crawling_beginHour)

    def outSqlForComing(self):
        return (Common.time_s(self.crawling_time),str(self.brandact_id),str(self.brandact_catgoryId),self.brandact_catgoryName,str(self.brandact_position),self.brandact_platform,self.brandact_channel,self.brandact_name,self.brandact_url,self.brandact_desc,self.brandact_logopic_url,self.brandact_enterpic_url,self.brandact_status,str(self.brandact_sign),self.brandact_other_ids,str(self.brandact_sellerId),self.brandact_sellerName,str(self.brandact_shopId),self.brandact_shopName,self.brandact_discount,str(self.brandact_soldCount),str(self.brandact_remindNum),str(self.brandact_coupon),';'.join(self.brandact_coupons),self.brandact_brand,str(self.brandact_inJuHome),str(self.brandact_juHome_position),Common.time_s(float(self.brandact_starttime)/1000),Common.time_s(float(self.brandact_endtime)/1000),self.crawling_beginDate,self.crawling_beginHour)

    def outItem(self):
        print 'self.brandact_platform,self.brandact_channel,self.crawling_time,self.brandact_catgoryId,self.brandact_catgoryName,self.brandact_position,self.brandact_id,self.brandact_url,self.brandact_name,self.brandact_desc,self.brandact_logopic_url,self.brandact_enterpic_url,self.brandact_starttime,self.brandact_endtime,self.brandact_status,self.brandact_sign,self.brandact_other_ids,self.brandact_sellerId,self.brandact_sellerName,self.brandact_shopId,self.brandact_shopName,self.brandact_soldCount,self.brandact_remindNum,self.brandact_discount,self.brandact_coupon,self.brandact_coupons'
        print '# brandActivityItem:',self.brandact_platform,self.brandact_channel,self.crawling_time,self.brandact_catgoryId,self.brandact_catgoryName,self.brandact_position,self.brandact_id,self.brandact_url,self.brandact_name,self.brandact_desc,self.brandact_logopic_url,self.brandact_enterpic_url,self.brandact_starttime,self.brandact_endtime,self.brandact_status,self.brandact_sign,self.brandact_other_ids,self.brandact_sellerId,self.brandact_sellerName,self.brandact_shopId,self.brandact_shopName,self.brandact_soldCount,self.brandact_remindNum,self.brandact_discount,self.brandact_coupon,self.brandact_coupons

        """
        print '原数据信息:'
        print 'brand activity pagedata'
        print self.brandact_pagedata
        print 'brand activity page'
        print self.brandact_page
        print 'brand activity pages'
        print self.brandact_pages
        """



def test():
    pass


#
if __name__ == '__main__':
    test()


