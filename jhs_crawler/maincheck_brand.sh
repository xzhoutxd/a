#!/bin/sh

DATESTR=`date +"%Y%m%d%H"`

DIR=`pwd`
cd $DIR
LOG=check_Brands
/bin/sh $DIR/k.sh JHSBrandMainCheck

/usr/local/bin/python $DIR/JHSBrandMainCheck.py > $DIR/log/main_check/${LOG}_${DATESTR}.log
