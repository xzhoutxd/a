#!/bin/sh

DATESTR=`date +"%Y%m%d%H"`

DIR=`pwd`
cd $DIR
/bin/sh $DIR/k.sh JHSBrandMain

cd $DIR/../..
LOGDIR=`pwd`
LOGFILE=$LOGDIR/logs/jhs/main/add_mainBrands_${DATESTR}.log

cd $DIR
/usr/local/bin/python $DIR/JHSBrandMain.py > $LOGFILE
