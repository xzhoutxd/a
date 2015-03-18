#!/bin/sh

DATESTR=`date +"%Y%m%d%H"`

#/usr/bin/python /usr/local/ju_spider/jhs_crawler/JHSMainComing.py > /usr/local/ju_spider/jhs_crawler/log/brand_coming/add_comingbrand_${DATESTR}.log
DIR=/usr/local/ju_spider/jhs_crawler
cd $DIR
/bin/sh $DIR/k.sh python JHSBrandComing

/usr/local/bin/python $DIR/JHSBrandComing.py > $DIR/log/brand_coming/add_comingbrand_${DATESTR}.log
