#!/bin/sh

DATESTR=`date +"%Y%m%d%H"`

DIR=`pwd`
cd $DIR
/bin/sh $DIR/k.sh python JHSBrandComing

/usr/local/bin/python $DIR/JHSBrandComing.py > $DIR/log/brand_coming/add_comingbrand_${DATESTR}.log
