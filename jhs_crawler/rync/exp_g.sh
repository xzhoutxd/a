#!/bin/bash

#yesterday=`date -d -1days +"%Y-%m-%d"`
today=`date +"%Y-%m-%d"`

if [ $# = 0 ]; then
	theday=$today
else
	theday=$1
fi

while read line
do
	comment=${line:0:1}
	if [ $comment = "#" ]
	then
		continue
	fi
	exp_t.sh $line $theday
done < ./jhs_tbl.list
