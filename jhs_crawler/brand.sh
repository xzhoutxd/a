#!/bin/sh

DATESTR=`date +"%Y%m%d%H"`

DIR=/usr/local/ju_spider/jhs_crawler
cd $DIR
/bin/sh $DIR/k.sh python JHSMain

/usr/bin/python $DIR/JHSMain.py > $DIR/log/brand/add_newBrands_${DATESTR}.log

