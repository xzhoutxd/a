#-*- coding:utf-8 -*-
#!/usr/bin/env python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re
import random
import json
import time

class JHSBrandTEMP():
    '''A class of brand'''
    def __init__(self):
        pass

    def temp(self, page):
        # 即将上线
        print '# coming Temp'
        b_url_valListcoming = self.activityListForComingTemp(page)
        # 马上开团
        print '# brand Temp'
        b_url_valList = self.activityListTemp(page)
        return b_url_valListcoming + b_url_valList

    # 聚划算开团活动列表模板
    def activityListTemp(self, page):
        # 数据接口URL list
        b_url_valList = []
        # 模板1
        m = re.search(r'<div id="floor\d+" class="l-floor J_Floor placeholder ju-wrapper" (.+?)>.+?</div>', page, flags=re.S)
        if m:
            b_url_valList = self.activityListTemp1(page)
        else:
            # 模板2
            m = re.search(r'<div id="(\d+)" class="l-floor J_Floor placeholder ju-wrapper" data-ajax="(.+?)">\s+<div class="l-f-title">\s+<div class="l-f-tbox">(.+?)</div>', page, flags=re.S)
            if m:
                b_url_valList = self.activityListTemp2(page)
            else:
                # 模板3
                m = re.search(r'<div id="floor(\d+_\d+)".+?data-spm="floor\d+_\d+".+?data-ids="(.+?)"', page, flags=re.S)
                if m:
                    b_url_valList = self.activityListTemp3(page)
                else:
                    m = re.search(r'"firstFloorData":{"brandList":\[{.+?}}\],.+?},"floorList"', page, flags=re.S)
                    if m:
                        b_url_valList = self.activityListTemp4(page)
                    else:
                        print '# err: not matching all templates.'

        return b_url_valList

    # 品牌团页面模板1
    def activityListTemp1(self, page):
        # 获取数据接口的URL
        url_valList = []
        p = re.compile(r'<div id="floor\d+" class="l-floor J_Floor placeholder ju-wrapper" (.+?)>.+?</div>', flags=re.S)
        for floor in p.finditer(page):
            floor_info = floor.group(1)
            f_name, f_catid, f_activitySignId = '', '', ''
            m = re.search(r'data-floorName="(.+?)"\s+', floor_info, flags=re.S)
            if m:
                f_name = m.group(1)

            m = re.search(r'data-catid=\'(.+?)\'\s+', floor_info, flags=re.S)
            if m:
                f_catid = m.group(1)

            m = re.search(r'data-activitySignId=\"(.+?)\"$', floor_info, flags=re.S)
            if m:
                f_activitySignId = m.group(1)

            if f_activitySignId == '':
                f_url = self.brand_page_url + '&page=1&frontCatIds=%s'%f_catid
                print '# brand activity floor:', f_name, f_catid, f_url
                url_valList.append((f_url, f_name, f_catid))
        return url_valList

    # 品牌团页面模板2
    def activityListTemp2(self, page):
        # 获取数据接口的URL
        url_valList = []
        p = re.compile(r'<div id="(\d+)" class="l-floor J_Floor placeholder ju-wrapper" data-ajax="(.+?)">\s+<div class="l-f-title">\s+<div class="l-f-tbox">(.+?)</div>', flags=re.S)
        for floor in p.finditer(page):
            f_name, f_catid, f_url, f_activitySignId = '', '', '', ''
            f_catid, f_url, f_name = floor.group(1), floor.group(2), floor.group(3)
            if f_url != '':
                print '# brand activity floor:', f_name, f_catid, f_url
                url_valList.append((f_url, f_name, f_catid))
        return url_valList

    # 品牌团页面模板3
    def activityListTemp3(self, page):
        #print page
        # 获取数据接口的URL
        floor_name = {}
        m = re.search(r'<div id="J_FixedNav" class="fixed-nav".+?>\s+<ul>(.+?)</ul>.+?</div>', page, flags=re.S)
        if m:
            floorname_info = m.group(1)
            p = re.compile(r'<li.+?>\s+<a href="#floor(\d+)".+?><span>(.+?)</span></a>\s+</li>', flags=re.S)
            for floor in p.finditer(floorname_info):
                i, name = floor.group(1), floor.group(2)
                floor_name[i] = name

        f_preurl = ''
        m = re.search(r'lazy.destroy\(\);\s+S\.IO\({\s+url: "(.+?)",\s+"data": {(.+?)},.+?\)}', page, flags=re.S)
        if m:
            url, data_s = m.group(1), ''.join(m.group(2).split())
            data_list = data_s.split(',"')
            add_data = ''
            for data in data_list:
                data = data.replace('"','')
                if data.find('brandIds') == -1:
                    add_data = add_data + "=".join(data.split(':')) + '&'
            f_preurl = url + '?' + add_data
        if f_preurl == '':
            f_preurl = 'http://ju.taobao.com/json/tg/ajaxGetBrandsV2.json?btypes=1,2&stype=bindex,saima1,biscore,bscore,sscore&reverse=down,down,down,down,down&showType=2&includeForecast=true&'

        url_valList = []
        p = re.compile(r'<div id="floor(\d+_\d+)"\s+data-spm="floor\d+_\d+"\s+data-ids="(.+?)"', flags=re.S)
        for floor in p.finditer(page):
            f_id, f_activitySignId = floor.group(1), floor.group(2)
            print '# activity floor:', f_id, f_activitySignId
            f_url = f_preurl + 'brandIds=%s'%f_activitySignId
            f_catid = f_id.split('_')[0]
            f_catname = ''
            if floor_name.has_key(f_catid):
                f_catname = floor_name[f_catid]
            url_valList.append((f_url,f_catname,f_catid))

        return url_valList

    # 品牌团页面模板4
    def activityListTemp4(self, page):
        #print page
        # 获取数据接口的URL
        url_valList = []
        p = re.compile(r'{"dataType":1,"elemNum":\d+,"floorName":"(.+?)","hasSubFloor":true,"kengType":0,"subFloorList":\[(.+?)\].+?}', flags=re.S)
        for floor in p.finditer(page):
            f_catname, sub_floor = floor.group(1), floor.group(2)
            if f_catname.find('即将上线') != -1: continue
            f_catid = -1
            s_p = re.compile(r'"dataUrl":"(.+?)"', flags=re.S)
            for s_floor in s_p.finditer(sub_floor):
                f_url = s_floor.group(1)
                url_valList.append((f_url,f_catname,f_catid))                
                print f_url,f_catname,f_catid
                
        p = re.compile(r'{"dataType":1,"dataUrl":"(.+?)","elemNum":\d+,"floorName":"(.+?)","hasSubFloor":false,"kengType":0.+?}', flags=re.S)
        for floor in p.finditer(page):
            f_url, f_catname = floor.group(1), floor.group(2)
            if f_catname.find('即将上线') != -1: continue
            f_catid = -1
            url_valList.append((f_url,f_catname,f_catid))
            print f_url,f_catname,f_catid

        return url_valList


    # 聚划算即将上线活动列表模板
    def activityListForComingTemp(self, page):
        # 数据接口URL list
        b_url_valList = []
        # 模板1
        m = re.search(r'<div.+?data-catid=\'(\d+)\' data-forecast="true">\s+<div class="f-sub-floor">\s+<span>(.+?)</span>\s+</div>', page, flags=re.S)
        if m:
            b_url_valList = self.activityListForComingTemp1(page)
        else:
            # 模板2
            m = re.search(r'<div.+?id="(subfloor\d+)" data-ajax="(.+?)">\s+<div class="f-sub-floor">\s+<span>(.+?)</span>\s+</div>', page, flags=re.S)
            if m:
                b_url_valList = self.activityListForComingTemp2(page)
            else:
                m = re.search(r'"firstFloorData":{"brandList":\[{.+?}}\],.+?},"floorList"', page, flags=re.S)
                if m:
                    b_url_valList = self.activityListForComingTemp3(page)
                else:
                    print '# err: not matching all templates.' 
        return b_url_valList
         
    # 品牌团页面模板1
    def activityListForComingTemp1(self, page):
        # 获取数据接口的URL
        url_valList = []
        p = re.compile(r'<div.+?data-catid=\'(\d+)\' data-forecast="true">\s+<div class="f-sub-floor">\s+<span>(.+?)</span>\s+</div>', flags=re.S)
        for sub_floor in p.finditer(page):
            f_name, f_catid = '', '', ''
            f_catid, f_name = sub_floor.group(1), sub_floor.group(2)

            print '# Coming activity floor:', f_name, f_catid
            if f_catid != '':
                page_num = 1
                f_url = self.brandcoming_page_url + '&page=%d'%page_num + '&frontCatIds=%s'%f_catid
                url_valList.append((f_url, f_name, f_catid))
        return url_valList

    # 品牌团页面模板2
    def activityListForComingTemp2(self, page):
        # 获取数据接口的URL
        url_valList = []
        p = re.compile(r'<div.+?id="(subfloor\d+)" data-ajax="(.+?)">\s+<div class="f-sub-floor">\s+<span>(.+?)</span>\s+</div>', flags=re.S)
        for sub_floor in p.finditer(page):
            f_url, f_name, f_catid = '', '', ''
            f_url, f_name = sub_floor.group(2), sub_floor.group(3)

            if f_url:
                m = re.search(r'frontCatIds=(\d+)', f_url)
                if m:
                    f_catid = m.group(1)
                print '# Coming activity floor:', f_name, f_catid, f_url
                url_valList.append((f_url, f_name, f_catid))
        return url_valList

    # 品牌团页面模板3
    def activityListForComingTemp3(self, page):
        #print page
        # 获取数据接口的URL
        url_valList = []
        p = re.compile(r'{"dataType":1,"elemNum":\d+,"floorName":"(.+?)","hasSubFloor":true,"kengType":0,"subFloorList":\[(.+?)\].+?}', flags=re.S)
        for floor in p.finditer(page):
            f_catname, sub_floor = floor.group(1), floor.group(2)
            if f_catname.find('即将上线') == -1: continue
            f_catid = -1
            s_p = re.compile(r'"dataUrl":"(.+?)".+?"floorName":"(.+?)"', flags=re.S)
            for s_floor in s_p.finditer(sub_floor):
                f_url, sub_f_catname = s_floor.group(1), s_floor.group(2)
                url_valList.append((f_url,sub_f_catname,f_catid))                
                print f_url,sub_f_catname,f_catid
                
        p = re.compile(r'{"dataType":1,"dataUrl":"(.+?)","elemNum":\d+,"floorName":"(.+?)","hasSubFloor":false,"kengType":0.+?}', flags=re.S)
        for floor in p.finditer(page):
            f_url, f_catname = floor.group(1), floor.group(2)
            if f_catname.find('即将上线') == -1: continue
            f_catid = -1
            url_valList.append((f_url,f_catname,f_catid))
            print f_url,f_catname,f_catid

        return url_valList


    # 聚划算开团活动列表中的Top推广位
    def activityTopbrandTemp(self, page):
        # Top 推广位的活动
        top_brands = {}
        # 模板1
        m = re.search(r'<div id="floor\d+" class="l-floor J_Floor placeholder ju-wrapper" (.+?)>.+?</div>', page, flags=re.S)
        if m:
            top_brands = self.activityTopbrandTemp1(page)
        else:
            # 模板2
            m = re.search(r'<div id="(todayBrand)|(custom\d+)".+?>\s+<div class="l-f-title">\s+<div class="l-f-tbox">(.+?)</div>', page, flags=re.S)
            if m:
                top_brands = self.activityTopbrandTemp2(page)
            else:
                print '# err: not find top brands all templates.'

        return top_brands

    # 品牌团页面Top推广位模板1
    def activityTopbrandTemp1(self, page):
        # 获取数据接口的URL
        top_brands = {}
        p = re.compile(r'<div id="floor\d+" class="l-floor J_Floor placeholder ju-wrapper" (.+?)>.+?</div>', flags=re.S)
        for floor in p.finditer(page):
            floor_info = floor.group(1)
            f_name, f_catid, f_activitySignId = '', '', ''
            m = re.search(r'data-floorName="(.+?)"\s+', floor_info, flags=re.S)
            if m:
                f_name = m.group(1)

            m = re.search(r'data-catid=\'(.+?)\'\s+', floor_info, flags=re.S)
            if m:
                f_catid = m.group(1)

            m = re.search(r'data-activitySignId=\"(.+?)\"$', floor_info, flags=re.S)
            if m:
                f_activitySignId = m.group(1)

            begin_page = 1
            if f_activitySignId != '':
                f_url = self.brand_page_url + '&page=%d'%begin_page + '&activitySignId=%s'%f_activitySignId.replace(',','%2C') + '&stype=ids'
                print '# brand activity floor: %s activitySignIds: %s, url: %s'%(f_name, f_activitySignId, f_url)
                act_ids = f_activitySignId.split(',')
                i = 1
                for act_id in act_ids:
                    print '# top brand: position:%s,id:%s'%(str(i),str(act_id))
                    top_brands[str(act_id)] = {'act_id':str(act_id),'position':today_i,'datatype':f_name}
                    i += 1
        return top_brands

    # 品牌团页面Top推广位模板2
    def activityTopbrandTemp2(self, page):
        top_brands = {}
        p = re.compile(r'<div id="(todayBrand)|(custom\d+)".+?>\s+<div class="l-f-title">\s+<div class="l-f-tbox">(.+?)</div>\s+</div>\s+<div class="ju-itemlist">\s+<ul.+?data-spm="floor\d+">(.+?)</ul>', flags=re.S)
        for floor in p.finditer(page):
            f_name, brand_list = floor.group(3), floor.group(4)
            f_name = re.sub('&amp;','',f_name)
            today_i = 1
            p = re.compile(r'<li class="brand.+?".+?>.+?<a.+?href="(.+?)".+?>.+?</a>.+?</li>', flags=re.S)
            for act in p.finditer(brand_list):
                act_url = act.group(1)
                act_id = -1
                m = re.search(r'act_sign_id=(\d+)', act_url, flags=re.S)
                if m:
                    act_id = m.group(1)
                    top_brands[str(act_id)] = {'act_id':str(act_id),'position':today_i,'url':act_url,'datatype':f_name}
                else:
                    top_brands[str(act_url)] = {'act_id':str(act_id),'position':today_i,'url':act_url,'datatype':f_name}
                print '# top brand: position:%s,id:%s,url:%s'%(str(today_i),str(act_id),act_url),f_name
                today_i += 1
        return top_brands


