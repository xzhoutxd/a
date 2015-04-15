#!/bin/sh

DATESTR=`date +"%Y%m%d%H"`

if [ $# = 0 ]; then
    echo " Usage: $0 master|slave" 
    echo " e.g. : $0 m|s" 
    exit 1
else
    m_type=$1
fi
DIR=`pwd`
cd $DIR
LOG=add_hourBrands
/bin/sh $DIR/k.sh JHSBrandHour

/usr/local/bin/python $DIR/JHSBrandHour.py $m_type > ../../logs/jhs/brand_hour/${LOG}_${DATESTR}.log
