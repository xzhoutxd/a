#!/bin/sh

DATESTR=`date +"%Y%m%d%H"`

/usr/bin/python /usr/local/ju_spider/jhs_crawler/JHSBrandDay.py > /usr/local/ju_spider/jhs_crawler/log/brand_day/add_dayBrands_${DATESTR}.log
