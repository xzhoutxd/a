#!/bin/sh

DATESTR=`date +"%Y%m%d%H"`

DIR=`pwd`
cd $DIR
/bin/sh $DIR/k.sh python JHSBrandMain

/usr/local/bin/python $DIR/JHSBrandMain.py > $DIR/log/main/add_Brands_${DATESTR}.log
