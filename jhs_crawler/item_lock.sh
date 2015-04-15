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
LOG=add_itemlock
/bin/sh $DIR/k.sh JHSBrandItemLock

/usr/local/bin/python $DIR/JHSBrandItemLock.py $m_type > ../../logs/jhs/item_lock/${LOG}_${DATESTR}.log
