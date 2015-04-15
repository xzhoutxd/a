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
LOG=add_startBrands
/bin/sh $DIR/k.sh JHSBrandStart

/usr/local/bin/python $DIR/JHSBrandStart.py $m_type > ../../logs/jhs/brand/${LOG}_${DATESTR}.log

