#!/bin/sh

DATESTR=`date +"%Y%m%d%H"`

DIR=`pwd`
cd $DIR
LOG=brands_position
/bin/sh $DIR/k.sh JHSBrandMarketing

/usr/local/bin/python $DIR/JHSBrandMarketing.py > $DIR/log/brand_position/${LOG}_${DATESTR}.log

