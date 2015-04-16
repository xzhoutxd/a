#!/bin/sh

DATESTR=`date +"%Y%m%d%H"`

DIR=`pwd`
cd $DIR
LOG=check_brandhour
/bin/sh $DIR/k.sh JHSBrandHourCheck

cd $DIR/../..
LOGDIR=`pwd`
LOGFILE=$LOGDIR/logs/jhs/brand_hourcheck/check_hourBrands_${DATESTR}.log

cd $DIR
/usr/local/bin/python $DIR/JHSBrandHourCheck.py > $LOGFILE
