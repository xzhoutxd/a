#!/bin/sh

DATESTR=`date +"%Y%m%d%H"`

DIR=`pwd`
cd $DIR
/bin/sh $DIR/k.sh JHSBrandMainCheck

cd $DIR/../..
LOGDIR=`pwd`
LOGFILE=$LOGDIR/logs/jhs/main_check/check_comingBrands_${DATESTR}.log

cd $DIR
/usr/local/bin/python $DIR/JHSBrandMainCheck.py > $LOGFILE
