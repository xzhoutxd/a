#!/bin/sh

DATESTR=`date +"%Y%m%d%H"`

/usr/bin/python /usr/local/ju_spider/jhs_crawler/JHSMainComing.py > /usr/local/ju_spider/jhs_crawler/log/brand_coming/brand_test_coming_${DATESTR}.log
