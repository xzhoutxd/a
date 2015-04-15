#!/bin/sh

DATESTR=`date +"%Y%m%d%H"`

DIR=`pwd`
cd $DIR
/bin/sh $DIR/k.sh python JHSBrandMarketing

/usr/local/bin/python $DIR/JHSBrandMarketing.py > $DIR/log/brand_position/brands_position_${DATESTR}.log

