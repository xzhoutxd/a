#!/bin/bash

DIR=/home/har/jhs/crawler_v2/jhsdata/dump/sql
yesterday=`date -d -1days +"%Y-%m-%d"`

if [ $# = 0 ]; then
	theday=$today
else
	theday=$1
fi

cd $DIR

# To unzip compressed dump file
#gz_file=jhs_${theday}.tar.gz
#tar zxvf ${gz_file}

while read line
do
	comment=${line:0:1}
	if [ $comment = "#" ]
	then
		continue
	fi
	
	/bin/sh $DIR/imp_t_day.sh $line $theday
done < $DIR/jhs_tbl_day.list
