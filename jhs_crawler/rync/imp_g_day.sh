#!/bin/bash

DIR=`pwd`
yesterday=`date -d -1days +"%Y-%m-%d"`

now_time=$(date +%Y-%m-%d-%H:%M:%S)
echo "-- imp day start...time:$now_time"

if [ $# = 0 ]; then
	theday=$yesterday
else
	theday=$1
fi

cd $DIR

if [ ! -d $DIR/$theday ]; then
        mkdir -p $DIR/$theday
fi

# To unzip compressed dump file
gz_file=${DIR}/data/jhs_day_${theday}.tar.gz
if [ ! -f ${gz_file} ]; then
        echo " File ${gz_file} is not existed"
        exit 1
fi
tar zxvf ${gz_file} -C ${DIR}/${theday}

while read line
do
	comment=${line:0:1}
	if [ $comment = "#" ]
	then
		continue
	fi
	
	/bin/sh $DIR/imp_t_day.sh $line $theday
done < $DIR/jhs_tbl_day.list

now_time=$(date +%Y-%m-%d-%H:%M:%S)
echo "-- imp day end...time:$now_time"
exit;
