#!/bin/bash

#yesterday=`date -d -1days +"%Y-%m-%d"`
DIR=`pwd`
today=`date +"%Y-%m-%d"`
hour=`date -d -1hours +"%H"`

now_time=$(date +%Y-%m-%d-%H:%M:%S)
echo "-- exp hour start...time:$now_time"

if [ $# = 0 ]; then
	theday=$today
	thehour=$hour
else
	theday=$1
	thehour=$2
fi

cd $DIR

while read line
do
	comment=${line:0:1}
	if [ $comment = "#" ]
	then
		continue
	fi
	/bin/sh $DIR/exp_t_hour.sh $line $theday $thehour
done < $DIR/jhs_tbl_hour.list


/bin/sh $DIR/sync_g_hour.sh $theday $thehour
now_time=$(date +%Y-%m-%d-%H:%M:%S)
echo "-- exp hour end...time:$now_time"
exit;
