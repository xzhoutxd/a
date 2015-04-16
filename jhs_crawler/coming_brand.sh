#!/bin/sh

DATESTR=`date +"%Y%m%d%H"`

DIR=`pwd`
cd $DIR
/bin/sh $DIR/k.sh JHSBrandComing

cd $DIR/../..
LOGDIR=`pwd`
LOGFILE=$LOGDIR/logs/jhs/brand_coming/add_comingBrands_${DATESTR}.log

cd $DIR
/usr/local/bin/python $DIR/JHSBrandComing.py > $LOGFILE
