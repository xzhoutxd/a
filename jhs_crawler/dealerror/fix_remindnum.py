#-*- coding:utf-8 -*-
#!/usr/bin/env python

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re
import os
import json
import MySQLdb


#filepath_m = '/home/har/jhs/jhsdata/page/act/main/2015/02/02/09/'
#filename = 'add_newBrands_2015020209.log'
#filepath_m = '/home/har/jhs/jhsdata/page/act/main/2015/02/02/19/'
#filename = 'add_newBrands_2015020219.log'
#filepath_m = '/home/har/jhs/jhsdata/page/act/main/2015/03/03/09/'
"""
fout = open(filename, 'r')
s = fout.read()
fout.close()

act_idList = []
file_nameList = []
p = re.compile(r'#####A activity start#####.+?activity id:(\d+).+?items num.+?#####A activity end#####', flags=re.S)
for string in p.finditer(s):
    act_id = string.group(1)
    #print act_id
    act_idList.append(act_id)
    file_nameList.append((act_id+'_act',act_id))

SET_NAMES_QUERY = "set names utf8"
# Open database connection
#db = MySQLdb.connect("127.0.0.1","root","zhouxin","jhs",charset='utf8')
db = MySQLdb.connect("192.168.1.113","jhs","123456","jhs",charset='utf8')

# prepare a cursor object using cursor() method
db_cursor = db.cursor()

results = []
time_start = '2015-03-03 09:29:00'
time_end = '2015-03-03 09:50:00'
sql = 'select act_id from nd_jhs_parser_item where crawl_time > \'%s\' and crawl_time < \'%s\''%(time_start,time_end)

try:
    db_cursor.execute(SET_NAMES_QUERY)
    db_cursor.execute(sql)
    results = db_cursor.fetchall()
except StandardError as err:
    print err

#关闭    
db_cursor.close()
db.close()

print '# item num:',len(results)
#print results
"""

act_idList = []
file_nameList = []
for item in results:
    act_id = str(item[0])
    if act_id not in act_idList:
        act_idList.append(act_id)
        file_nameList.append((act_id+'_act',act_id))

print '# act nums:',len(act_idList)
print act_idList

need_fix_file_list = []
for files in file_nameList:
    filepath = filepath_m + files[0] + '/'
    act_id = files[1]
    print files
    file_list = os.listdir(filepath)
    for f in file_list:
        #4490489-act-home-floor-1_1422840705.htm
        m = re.search(r'\d+-act-home-floor-\d+_\d+.htm', f, flags=re.S)
        if m:
            need_fix_file_list.append((filepath + f, act_id))
        else:
            m = re.search(r'\d+-act-home_\d+.htm', f, flags=re.S)
            if m:
                need_fix_file_list.append((filepath + f, act_id))
print  need_fix_file_list
print '# num file:', len(need_fix_file_list)

remind_item_list = []
i = 0
for need_file in need_fix_file_list:
    i += 1
    act_id = need_file[1]
    #if i == 1:
    fout = open(need_file[0], 'r')
    s = fout.read()
    fout.close()

    #print need_file[0]

    #if int(act_id) != 5063903: continue
    print need_file[0]
    """ 
    m = re.search(r'<li class="item-small-v3">.+?</li>', s, flags=re.S)
    if m:
        continue
    else:
        m = re.search(r'.+?{"baseinfo":{.+?}}.+?', s, flags=re.S)
        if m:
            p = re.compile(r'({"baseinfo":{.+?}})', flags=re.S)
            for item_g in p.finditer(s):
            #print result
            #json_list = json.loads(result)
            #for j in json_list:
                #print j
                #if j.has_key('itemList'):
                #    item_list = j['itemList']
                #    for item in item_list:
                juId, itemId, remindNum = '', '', ''
                item = json.loads(item_g.group(1))
                if item.has_key('baseinfo'):
                    item_baseinfo = item['baseinfo']
                    if item_baseinfo.has_key('juId'):
                        juId = item_baseinfo['juId']
                    if item_baseinfo.has_key('itemId'):
                        itemId = item_baseinfo['itemId']
                if item.has_key('remind'):
                    item_remind = item['remind']
                    if item_remind.has_key('remindNum'):
                        remindNum = item_remind['remindNum']
                if juId != '' and itemId != '':
                    remind_item_list.append((act_id, juId, itemId, remindNum))
                print act_id, juId, itemId, remindNum
    """
    m = re.search(r'<li class="item-small-v3">.+?</li>', s, flags=re.S)
    if m:
        p = re.compile(r'<li class="item-small-v3">.+?<a.+?href="(.+?)".+?>.+?<span class="sold-num">(.+?)</span>.+?</li>', flags=re.S)
        for item_g in p.finditer(s):
        #p = re.compile(r'<li class="item-small-v3">.+?<a.+?href="(.+?)".+?>.+?<div class="prompt">\s+<span class="sold-num">\s+<em class="J_soldnum">(.+?)</em>人想买\s+</span>.+?</li>', flags=re.S)
            url, remindNum_str = item_g.group(1), item_g.group(2)
            juId, itemId = '', ''
            #id=10000005498162&amp;item_id=35051696179
            m = re.search(r'id=(\d+)', url)
            if m:
                juId = m.group(1)
            m = re.search(r'item_id=(\d+)', url)
            if m:
                itemId = m.group(1)
            m = re.search(r'<em class="J_soldnum">(.+?)</em>人想买', remindNum_str, flags=re.S)
            if m:
                remindNum = m.group(1)
            else:
                remindNum = 0
            remind_item_list.append((act_id, juId, itemId, remindNum))
    m = re.search(r'<div class="ju-itemlist">\s*<ul class="clearfix">(.+?)</ul>', s, flags=re.S)
    if m:
        bigitem = m.group(1)
        #print bigitem
        p = re.compile(r'<li class="item-big-v2">.+?<a .+?href="(.+?)".+?>.+?<em class="J_soldnum">(.+?)</em>人想买.+?</li>', flags=re.S)
        for item_g in p.finditer(bigitem):
            url, remindNum = item_g.group(1), item_g.group(2)
            juId, itemId = '', ''
            #id=10000005498162&amp;item_id=35051696179
            m = re.search(r'id=(\d+)', url)
            if m:
                juId = m.group(1)
            m = re.search(r'item_id=(\d+)', url)
            if m:
                itemId = m.group(1)
            #print act_id, juId, itemId, remindNum
                remind_item_list.append((act_id, juId, itemId, remindNum))

print '# remind item num:', len(remind_item_list)

SET_NAMES_QUERY = "set names utf8"
# Open database connection
#db = MySQLdb.connect("127.0.0.1","root","zhouxin","jhs",charset='utf8')
db = MySQLdb.connect("192.168.1.113","jhs","123456","jhs",charset='utf8')

# prepare a cursor object using cursor() method
db_cursor = db.cursor()

for r in remind_item_list:
    #print r
    #remind_item_list.append((act_id, juId, itemId, remindNum))
    update_sql = 'update nd_jhs_parser_item set item_remindnum = %s where item_juid = %s and act_id = %s and item_id = %s'%(str(r[3]),str(r[1]),str(r[0]),str(r[2]))
    #print update_sql
    try:
        db_cursor.execute(SET_NAMES_QUERY)
        db_cursor.execute(update_sql)
        db.commit()
    except StandardError as err:
        db.rollback()
        print err

#关闭    
db_cursor.close()
db.close()
