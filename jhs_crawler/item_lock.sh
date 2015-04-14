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
/bin/sh $DIR/k.sh python JHSBrandItemLock

/usr/bin/python $DIR/JHSBrandItemLock.py $m_type > $DIR/log/item_lock/add_itemlock_${DATESTR}.log
