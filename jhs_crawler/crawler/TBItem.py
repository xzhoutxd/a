#-*- coding:utf-8 -*-
#!/usr/bin/env python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
#sys.path.append('../')

import re
import base.Common as Common
#import Common
import base.Config as Config
#import Config
from Item import Item

class TBItem(Item):
    '''A class to crawl taobao item'''
    def __init__(self):
        # parent construct
        Item.__init__(self)

        # 店铺类型
        self.shop_type = Config.TAOBAO_TYPE
        
        # 抓取设置
        #self.deal_pageSize   = Config.taobao_dealPageSize
        #self.deal_maxPages   = Config.taobao_dealMaxPages        

    # 商品页面
    def itemPage(self, url, refers=''):
        # 商品链接
        self.item_url = url

        # 商品详情页
        page = self.crawler.getData(url, refers)
        if not page or page == '': raise Common.InvalidPageException("Invalid Item Found")

        # 没有找到相应的商品信息 - 淘宝
        m = re.search(r'<div class="error-notice-hd">很抱歉，您查看的宝贝不存在，可能已下架或者被转移。</div>', page, flags=re.S)
        if m:
            self.item_page = None
            raise Common.NoItemException("# itemPage : No tb item found")

        # 匹配shop_id, item_id
        #<div id="LineZing" pagetype="2" shopid="73217422" tmplid="" itemid="40348828982"></div>
        m = re.search(r'<div id="LineZing".*?shopid="(\d+)".*?itemid="(\d+)"></div>', page)
        if m:
            self.item_page = page
            self.shop_id, self.item_id = m.group(1), m.group(2)
        else:
            raise Common.InvalidPageException("# itemPage %s : Invalid shop/item id found" %self.item_url)

        # 保存商品页
        #self.item_pages.append(('%s-item-home' %self.shop_type, self.item_url, self.item_page))
        self.item_pages['item-home'] = (self.item_url, self.item_page)

    def itemConfig(self):
        page = self.item_page

        # 商品名称
        m = re.search(r'<title>(.+?)</title>', page, flags=re.S)
        if m:
            title = Common.htmlDecode_s(m.group(1).strip())
            self.item_name = title.split('-淘宝网')[0].strip()

        # 卖家ID
        m = re.search(r'sellerId:"(\d+)"', page)
        if m: self.item_sellerId = m.group(1)

        # 商品PC页
        m = re.search(r'"wholeSibUrl":"(\S+?)"', page)
        if m:
            wholeSib_url = m.group(1) + '&callback=' + Common.jsonCallback()

            detail_page = self.crawler.getData(wholeSib_url, self.item_url)
            if not detail_page or detail_page == '':
                raise Common.InvalidPageException("# itemConfig : Invalid item detail page found")

            # 保存商品详情接口页
            #self.item_pages.append(('%s-item-detail' %self.shop_type, wholeSib_url, detail_page))
            self.item_pages['item-detail'] = (wholeSib_url, detail_page)

        # 成交数量页
        m = re.search(r'"apiItemInfo":"(.+?stm=\d+&id=\d+&sid=\d+&.+?)"', page)
        if m:
            dealnum_url = m.group(1) + '&callback=' + Common.jsonCallback()
            data = self.crawler.getData(dealnum_url, self.item_url)
            if data and data != '':
                #self.item_pages.append(('%s-item-dealnum' %self.shop_type, dealnum_url, data))
                self.item_pages['item-dealnum'] = (dealnum_url, data)

                r = re.search(r'quanity:\s*(\d+)\s*,', data, flags = re.S)
                if r: self.item_sellCount = r.group(1)

        # 评价数量页
        m = re.search(r'CounterApi:"(.+?keys=\S+,ICE_\d_feedcount-\d+,SM_\d+_dsr-\d+)"', page)
        if m:
            r_url = m.group(1) + '&callback=' + Common.jsonCallback()
            data = self.crawler.getData(r_url, self.item_url)

            if data and data != '':
                #self.item_pages.append(('%s-item-ratenum' %self.shop_type, r_url, data))
                self.item_pages['item-ratenum'] = (r_url, data)

        # 商品移动web页
        wap_url = 'http://hws.m.taobao.com/cache/wdetail/5.0/?id=%s' %(self.item_id)
        wap_refers = 'http://a.m.taobao.com/i%s.htm' %(self.item_id)
        wap_page = self.crawler.getData(wap_url, wap_refers, terminal='2')

        if not wap_page or wap_page == '': return
        #self.item_pages.append(('%s-item-wap' %self.shop_type, wap_url, wap_page))
        self.item_pages['item-wap'] = (wap_url, wap_page)

    # 商品收藏数
    def itemFavorites(self):
        page = self.item_page
        m = re.search(r'counterApi:"(.+?&keys=\S+?,\S+?,(\S+?),\S+?)"', page)
        if m:
            url = m.group(1) + '&callback=' + Common.jsonCallback()
            data = self.crawler.getData(url, self.item_url)

            if not data or data == '': return
            #self.item_pages.append(('%s-item-favorite' %self.shop_type, url, data))
            self.item_pages['item-favorite'] = (url, data)

    """
    # 成交记录SKU占比
    def dealSkuPercent(self):
        m = re.search(r'priceCutUrl:"\S+?(id=\d+&rootCatId=\d+)"', self.item_page)
        if m:
            deal_sku_id = m.group(1)
            deal_sku_url  = 'http://tds.alicdn.com/json/price_cut_data.htm?%s&unicode=true&v=1' %deal_sku_id
            data = self.crawler.getData(deal_sku_url, self.item_url)
            if not data or len(data) == 0: return
            # 保存成交记录SKU占比页
            #self.item_pages.append(('%s-item-dealsku' %self.shop_type, deal_sku_url, data))
            self.item_pages['item-dealsku'] = (deal_sku_url, data)

    def rateTagPercent(self):
        page = self.item_page
        m = re.search(r'data-commonApi="(.+?userNumId=\d+&auctionNumId=\d+&siteID=\d)"', page)
        if m:
            rate_tagUrl = m.group(1) + '&callback=' + Common.jsonCallback()
            data = self.crawler.getData(rate_tagUrl, self.item_url)
            if not data or data == '': return
            # 保存评价标签页
            #self.item_pages.append(('%s-item-ratetag' %self.shop_type, rate_tagUrl, data))
            self.item_pages['item-ratetag'] = (rate_tagUrl, data)

    def aDealRecord(self, data):
        # To check deal page
        if not data or data == '': 
            raise Common.InvalidPageException('# aDealRecord : Invalid deal page found')

        # 去掉转义符
        data = data.replace('\\', '')

        # 无成交记录
        m = re.search(r'<p class="attention naked">暂时还没有买家购买此宝贝。</p>', data)
        if m:
            #print '# aDealRecord : no deal', self.shop_type, self.item_id, data
            return

        # 系统太累了
        m = re.search(r'<p class=\"attention naked\">系统太累了，要不您过段时间再来看吧。</p>', data)
        if m:
            print '# aDealRecord : busy website', self.shop_type, self.item_id, data
            raise Common.InvalidPageException('# aDealRecord : busy website')

        # 有成交记录
        m = re.search(r'<table class="tb-list" summary="买家出价记录"', data)
        if not m:
            print '# aDealRecord : invalid deal page', self.shop_type, self.item_id, data            
            raise Common.InvalidPageException('# aDealRecord : Invalid deal page found')

        m = re.search(r'<tbody>(.+?)</tbody>', data)
        if m:
            html = m.group(1).replace(r'<span class=tb-anonymous>**</span>', r'**')
            p = re.compile(r'<tr .+?>(.+?)</tr>')
            
            for row in p.finditer(html):
                d = re.search(r'<td class="tb-start">(.+?)</td>', row.group(1))
                if d:
                    d_ctime = d.group(1)
                    d_timestamp = Common.str2timestamp(d_ctime)
    
                    # 到了截止时间2(本次抓取最早时间,追加抓取)，不再抓取
                    if self.deal_deadLine2 > Config.g_zeroValue and d_timestamp <= self.deal_deadLine2:
                        self.deal_stopCrawl = True
                        break

    def dealRecords(self):
        # 成交记录第1页
        data = self.crawler.getData(self.deal_url, self.item_url)
        self.aDealRecord(data)
        d_content = data

        # next pages
        monthly_deals = int(self.item_sellCount)
        if monthly_deals > self.deal_pageSize:
            d_url = self.deal_url
            pages = int(monthly_deals/self.deal_pageSize) + 1
            if pages > self.deal_maxPages: pages = self.deal_maxPages

            for i in range(1, pages):
                if self.deal_stopCrawl : break

                d_url = re.sub(r'bid_page='+str(i), r'bid_page='+str(i+1), d_url)
                data = self.crawler.getData(d_url, self.item_url)
                if not data or len(data) == 0: continue

                # 后续成交页面
                self.aDealRecord(data)
                d_header   = '<!-- url=%s -->\n' %d_url
                d_content += (d_header + data)

        # 保存成交页全部页
        #self.item_pages.append(('item.deal', self.deal_url, d_content))
        self.item_pages['item.deal'] = (self.deal_url, d_content)
    """

    # 解析商品内容
    def antPage(self, url):
        self.itemPage(url)
        if self.item_page and self.item_page != '':
            self.itemConfig()
            self.itemFavorites()
            #self.rateTagPercent()
            
            #self.crawler.useCookie(True)
            #self.dealSkuPercent()

# if __name__ == '__main__':
#     items = [41201797787]
#     for i_id in items:
#         url = 'http://item.taobao.com/item.htm?id=%d' %i_id
#         print '# ', i_id, url
#         i = TBItem()
#         i.antPage(url)
#         i.outItem()
