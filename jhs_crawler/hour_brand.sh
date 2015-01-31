#!/bin/sh

DATESTR=`date +"%Y%m%d%H"`

/usr/bin/python /usr/local/ju_spider/jhs_crawler/JHSBrandHour.py > /usr/local/ju_spider/jhs_crawler/log/brand_hour/add_hourBrands_${DATESTR}.log
