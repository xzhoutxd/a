#!/bin/sh

DATESTR=`date +"%Y%m%d%H"`

DIR=`pwd`
cd $DIR
/bin/sh $DIR/k.sh JHSBrandMarketing

cd $DIR/../..
LOGDIR=`pwd`
LOGFILE=$LOGDIR/logs/jhs/brand_position/add_Brandsposition_${DATESTR}.log

cd $DIR
/usr/local/bin/python $DIR/JHSBrandMarketing.py > $LOGFILE

