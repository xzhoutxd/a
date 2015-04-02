#!/bin/bash

DIR=/home/har/jhs/crawler_v2/jhsdata/dump/sql
yesterday=`date -d -1days +"%Y-%m-%d"`

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
