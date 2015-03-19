#!/bin/sh

DATESTR=`date +"%Y%m%d%H"`

DIR=/usr/local/ju_spider/jhs_crawler
cd $DIR
/bin/sh $DIR/k.sh python JHSBrandHourCheck

/usr/bin/python $DIR/JHSBrandHourCheck.py > $DIR/log/brand_hourcheck/check_brand_${DATESTR}.log
