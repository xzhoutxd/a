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
LOG=add_dayBrands
/bin/sh $DIR/k.sh JHSBrandDay

/usr/local/bin/python $DIR/JHSBrandDay.py $m_type > $DIR/log/brand_day/${LOG}_${DATESTR}.log
