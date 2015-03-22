#!/bin/sh

DATESTR=`date +"%Y%m%d%H"`

DIR=/usr/local/ju_spider/jhs_crawler
cd $DIR
/bin/sh $DIR/k.sh python JHSBrandMarketing

/usr/bin/python $DIR/JHSBrandMarketing.py > $DIR/log/brand_position/brands_position_${DATESTR}.log

