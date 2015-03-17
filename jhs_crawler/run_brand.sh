#!/bin/sh

DATESTR=`date +"%Y%m%d%H"`

DIR=/usr/local/ju_spider/jhs_crawler
cd $DIR
/usr/bin/python $DIR/JHSBrandMain.py > $DIR/log/main/add_Brands_${DATESTR}.log
