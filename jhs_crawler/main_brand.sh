#!/bin/sh

DATESTR=`date +"%Y%m%d%H"`

DIR=`pwd`
cd $DIR
LOG=add_mainBrands
/bin/sh $DIR/k.sh JHSBrandMain

/usr/local/bin/python $DIR/JHSBrandMain.py > $DIR/log/main/${LOG}_${DATESTR}.log
