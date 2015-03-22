#!/bin/sh

DATESTR=`date +"%Y%m%d%H"`

DIR=/usr/local/ju_spider/jhs_crawler
cd $DIR
/bin/sh $DIR/k.sh python JHSBrandDay

/usr/bin/python $DIR/JHSBrandDay.py > $DIR/log/brand_day/add_dayBrands_${DATESTR}.log
