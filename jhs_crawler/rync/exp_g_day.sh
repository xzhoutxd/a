#!/bin/bash

DIR=`pwd`
yesterday=`date -d -1days +"%Y-%m-%d"`

now_time=$(date +%Y-%m-%d-%H:%M:%S)
echo "-- exp day start...time:$now_time"

if [ $# = 0 ]; then
	theday=$yesterday
else
	theday=$1
fi

cd $DIR

while read line
do
	comment=${line:0:1}
	if [ $comment = "#" ]
	then
		continue
	fi
	/bin/sh $DIR/exp_t_day.sh $line $theday
done < $DIR/jhs_tbl_day.list

/bin/sh $DIR/sync_g_day.sh $theday
now_time=$(date +%Y-%m-%d-%H:%M:%S)
echo "-- exp day end...time:$now_time"
exit;
