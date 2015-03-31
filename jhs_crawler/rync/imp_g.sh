#!/bin/bash

#yesterday=`date -d -1days +"%Y-%m-%d"`
today=`date +"%Y-%m-%d"`

if [ $# = 0 ]; then
	theday=$today
else
	theday=$1
fi
# To unzip compressed dump file
gz_file=jhs_${theday}.tar.gz
tar zxvf ${gz_file}

while read line
do
	comment=${line:0:1}
	if [ $comment = "#" ]
	then
		continue
	fi
	
	imp_t.sh $line $theday
done < ./jhs_tbl.list
