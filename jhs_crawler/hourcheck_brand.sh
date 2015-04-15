#!/bin/sh

DATESTR=`date +"%Y%m%d%H"`

DIR=`pwd`
cd $DIR
LOG=check_brandhour
/bin/sh $DIR/k.sh JHSBrandHourCheck

/usr/local/bin/python $DIR/JHSBrandHourCheck.py > $DIR/log/brand_hourcheck/${LOG}_${DATESTR}.log
