#!/bin/sh

DATESTR=`date +"%Y%m%d%H"`

DIR=`pwd`
cd $DIR
LOG=add_comingbrand
/bin/sh $DIR/k.sh JHSBrandComing

/usr/local/bin/python $DIR/JHSBrandComing.py > ../../logs/jhs/brand_coming/${LOG}_${DATESTR}.log
