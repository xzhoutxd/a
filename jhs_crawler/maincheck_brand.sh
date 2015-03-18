#!/bin/sh

DATESTR=`date +"%Y%m%d%H"`

DIR=/usr/local/ju_spider/jhs_crawler
cd $DIR
/bin/sh $DIR/k.sh python JHSBrandMainCheck

/usr/bin/python $DIR/JHSBrandMainCheck.py > $DIR/log/main_check/check_Brands_${DATESTR}.log
