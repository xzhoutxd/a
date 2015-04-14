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
/bin/sh $DIR/k.sh python JHSBrandHour

/usr/bin/python $DIR/JHSBrandHour.py $m_type > $DIR/log/brand_hour/add_hourBrands_${DATESTR}.log
