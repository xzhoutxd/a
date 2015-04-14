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
/bin/sh $DIR/k.sh python JHSBrandDay

/usr/local/bin/python $DIR/JHSBrandDay.py $m_type > $DIR/log/brand_day/add_dayBrands_${DATESTR}.log
