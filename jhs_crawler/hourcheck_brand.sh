#!/bin/sh

DATESTR=`date +"%Y%m%d%H"`

DIR=/usr/local/ju_spider/jhs_crawler
cd $DIR
/usr/bin/python $DIR/JHSBrandCheck.py > $DIR/log/brand_hourcheck/check_brand_${DATESTR}.log
