#!/bin/bash

process_list=`ps -ef | grep $1 | grep python | grep -v grep | awk '{print $2}'`
for p in $process_list; do
        echo kill -s 9 $p
        kill -s 9 $p
done;
