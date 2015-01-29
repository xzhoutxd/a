#!/bin/sh

DATESTR=`date +"%Y%m%d%H"`

/usr/bin/python /usr/local/ju_spider/jhs_crawler/JHSMainComing.py > /usr/local/ju_spider/jhs_crawler/log/brand_coming/add_comingbrand_${DATESTR}.log
