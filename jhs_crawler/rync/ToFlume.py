#-*- coding:utf-8 -*-
#!/usr/bin/env python

import os
import threading
from multiprocessing.dummy import Pool as ThreadPool
from SFtp import SFtp

class ToFlume():
    '''A class of ToFlume, to gather log from spider node'''
    def __init__(self):
        self.mutex = threading.Lock()
        
        self.spider_nodes = {}
        self.time_range   = []

        self.rem_pathTmpl = '/home/netdata/data/qzj/' 
        self.loc_pathTmpl = '../../../data/qzj/temp/'

    def createPath(self, p):
        if self.mutex.acquire(1):
            if not os.path.exists(p): os.mkdir(p)
            self.mutex.release()

    def genNodes(self, start_id, stop_id):
        for i in range(start_id, stop_id+1):
            node_name = 'sp%02d' %i
            node_ip   = '192.168.7.%d' %i
            self.spider_nodes[node_ip] = node_name

    def timeRange(self, t_range):
        self.time_range = t_range

    def syncNode(self, v_node):
        # The node connect info
        ip, user, passwd, rem_path, loc_path, node_name = v_node 

        # To create sftp session
        s = SFtp()
        s.initSFtp(ip, user, passwd)
        s.sftpConnect()

        # To scan node dir time
        for t in self.time_range:
            rem_path = self.rem_pathTmpl + t
            loc_path = self.loc_pathTmpl + t
        
            # To create local path
            self.createPath(loc_path)

            if self.mutex.acquire(1):
                print '# syncNode : ', ip, node_name, rem_path, loc_path
                self.mutex.release()

            # To transfer file by sftp
            s.sftpMget(node_name, rem_path, loc_path)
            
        # To close sftp session
        s.sftpClose()
        s = None

    def syncNodes(self):
        # To generate node connect info
        v_nodes = []
        user, passwd = 'netdata', 'nd!@#$%^'

        for (ip, node_name) in self.spider_nodes.items():
            rem_path = self.rem_pathTmpl
            loc_path = self.loc_pathTmpl

            v = (ip, user, passwd, rem_path, loc_path, node_name)
            v_nodes.append(v)

        # To parallel gather qzj log file
        pool = ThreadPool(len(v_nodes))
        pool.map(self.syncNode, v_nodes)
        pool.close()
        pool.join()

if __name__ == '__main__':
    tf = ToFlume()
    t_day   = '20141213'
    t_range = []
    for i in xrange(0, 3):
        t_path = '%s%02d' %(t_day, i) 
        t_range.append(t_path)

    tf.genNodes(1, 10)
    tf.timeRange(t_range)
    tf.syncNodes()

    tf = None
