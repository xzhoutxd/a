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
import base.Common as Common
import base.Config as Config
from db.MysqlAccess import MysqlAccess
from JHSBrandCheckObj import JHSBrandCheckObj
from JHSBActItemM import JHSBActItemM
from JHSItemM import JHSItemM

class JHSBrandMainCheck():
    '''A class of brand for every hour check'''
    def __init__(self):
        # mysql
        self.mysqlAccess = MysqlAccess()

        # 活动检查
        self.brand_checkobj = JHSBrandCheckObj()

        # 抓取开始时间
        self.begin_time = Common.now()

        # 需要检查的活动
        self.act_dict = {}
        self.all_itemjuid = {}

    def antPage(self):
        try:
            # 获取还没开团的活动
            act_results = self.mysqlAccess.selectJhsActNotStart()
            if act_results:
                print '# Main check activity num:',len(act_results)
            else:
                print '# Main check activity not found..'
                return None

            # 商品默认信息列表
            act_valList = []
            for act_r in act_results:
                # 只抓时尚女士,精品男士
                #if int(act_r[2]) != 261000 or int(act_r[2]) != 262000: continue
                act_valList.append((str(act_r[1]),act_r[7],act_r[8],self.begin_time,str(act_r[28]),str(act_r[29])))
                if not self.act_dict.has_key(str(act_r[1])):
                    self.act_dict[str(act_r[1])] = []
                # 按照活动Id找出商品
                item_results = self.mysqlAccess.selectJhsItemIdsOfActId((str(act_r[1]),))
                if item_results:
                    print '# act id:%s name:%s starttime:%s endtime:%s Items num:%s'%(str(act_r[1]),str(act_r[7]),str(act_r[28]),str(act_r[29]),str(len(item_results)))
                    itemid_list = []
                    if len(item_results) > 0:
                        for item in item_results:
                            itemid_list.append(str(item[0]))
                            itemid_list.append(str(item[1]))
                            self.all_itemjuid[str(item[0])] = str(act_r[1])
                    self.act_dict[str(act_r[1])] = itemid_list

            print '# Main check brands num:',len(act_valList)
            print '# ALL item num:',len(self.all_itemjuid)

            #print act_valList
            #print self.act_dict
            #self.run_brandAct(act_valList)
            self.brand_checkobj.antPage(act_valList, self.act_dict, self.all_itemjuid)
        except Exception as e:
            print '# exception err in antPage info:',e
            self.traceback_log()

    def traceback_log(self):
        print '#####--Traceback Start--#####'
        tp,val,td = sys.exc_info()
        for file, lineno, function, text in traceback.extract_tb(td):
            print "exception traceback err:%s,line:%s,in:%s"%(file, lineno, function)
            print text
        print "exception traceback err:%s,%s,%s"%(tp,val,td)
        print '#####--Traceback End--#####'


if __name__ == '__main__':
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    b = JHSBrandMainCheck()
    b.antPage()
    time.sleep(1)
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))


