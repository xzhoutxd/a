#!/bin/bash

#yesterday=`date -d -1days +"%Y-%m-%d"`
DIR=/home/har/jhs/crawler_v2/jhsdata/dump/sql
today=`date +"%Y-%m-%d"`
hour=`date -d -1hours +"%H"`

if [ $# = 0 ]; then
	theday=$today
	thehour=$hour
else
	theday=$1
	thehour=$2
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
	
	/bin/sh $DIR/imp_t_hour.sh $line $theday $thehour
done < $DIR/jhs_tbl_hour.list
