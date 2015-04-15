#!/bin/sh

DATESTR=`date +"%Y%m%d%H"`

DIR=`pwd`
cd $DIR
/bin/sh $DIR/k.sh python JHSBrandMainCheck

/usr/local/bin/python $DIR/JHSBrandMainCheck.py > $DIR/log/main_check/check_Brands_${DATESTR}.log
