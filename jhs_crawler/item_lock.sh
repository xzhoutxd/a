#!/bin/sh

DATESTR=`date +"%Y%m%d%H"`

DIR=`pwd`
/bin/sh $DIR/k.sh python JHSBrandItemLock

/usr/bin/python $DIR/JHSBrandItemLock.py > $DIR/log/item_lock/add_itemlock_${DATESTR}.log
