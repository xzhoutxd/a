#!/bin/sh

DATESTR=`date +"%Y%m%d%H"`

DIR=`pwd`
cd $DIR
LOG=add_mainBrands
/bin/sh $DIR/k.sh JHSBrandMain

/usr/local/bin/python $DIR/JHSBrandMain.py > ../../logs/jhs/main/${LOG}_${DATESTR}.log
