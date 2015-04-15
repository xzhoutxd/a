#!/bin/sh

DATESTR=`date +"%Y%m%d%H"`

DIR=`pwd`
cd $DIR
/bin/sh $DIR/k.sh python JHSBrandHourCheck

/usr/local/bin/python $DIR/JHSBrandHourCheck.py > $DIR/log/brand_hourcheck/check_brand_${DATESTR}.log
