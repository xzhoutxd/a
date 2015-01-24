#!/bin/sh

DATESTR=`date +"%Y%m%d%H"`

/usr/bin/python /usr/local/ju_spider/jhs_crawler/JHSMain.py > /usr/local/ju_spider/jhs_crawler/log/brand/brands_${DATESTR}.log
