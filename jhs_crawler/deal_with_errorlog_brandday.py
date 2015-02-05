#-*- coding:utf-8 -*-
#!/usr/bin/env python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re
from JHSBrandDay import JHSBrandDay


crawl_act = {}
i = 1
for line in sys.stdin:
    try:
        if line.find('# retry too many times, no get item:') != -1:
            i += 1
            val = line.split('item: ')[1]
            p = re.compile(r'\n')
            _val = p.sub('', val)
            val_str = _val.replace('(','').replace(')','')
            val_list = val_str.split(', ')
            new_list = []
            for item in val_list:
                m = re.search(r'\d+L$', item)
                if m:
                    item = item.replace('L','')
                if item.find('u\'') != -1:
                    #new_list.append(item.decode('unicode_escape').replace('\'','').replace('u\'','\''))
                    new_list.append(item.replace('u\'','\'').decode('unicode_escape').replace('\'',''))
                else:
                    new_list.append((item.replace('\'','')).decode('string_escape'))
            t_val = tuple(new_list)
            #print i
            #print t_val
            # self.item_juId,self.item_actId,self.item_actName,self.item_act_url,self.item_juName,self.item_ju_url,self.item_id,self.item_url,self.item_oriPrice,self.item_actPrice
            if crawl_act.has_key(t_val[1]):
                crawl_list = crawl_act[t_val[1]][2]
                crawl_list.append(t_val)
            else:
                crawl_act[t_val[1]] = (t_val[1],t_val[2],[t_val])
    except StandardError as err:
        print err

all_crawl_list = []
for key in crawl_act.keys():
    print crawl_act[key]
    all_crawl_list.append((crawl_act[key][0],crawl_act[key][1],list(crawl_act[key][2])))

b = JHSBrandDay()
b.antPageForGiveup(all_crawl_list)


