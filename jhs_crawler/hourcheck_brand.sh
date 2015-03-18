#!/bin/sh

DATESTR=`date +"%Y%m%d%H"`

DIR=/usr/local/ju_spider/jhs_crawler
cd $DIR
/bin/sh $DIR/k.sh python JHSBrandCheck

/usr/local/bin/python $DIR/JHSBrandCheck.py > $DIR/log/brand_hourcheck/check_brand_${DATESTR}.log
