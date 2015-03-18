#!/bin/sh

DATESTR=`date +"%Y%m%d%H"`

DIR=/usr/local/ju_spider/jhs_crawler
cd $DIR
/bin/sh $DIR/k.sh python JHSBrandHour

/usr/local/bin/python $DIR/JHSBrandHour.py > $DIR/log/brand_hour/add_hourBrands_${DATESTR}.log
