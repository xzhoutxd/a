#!/bin/bash

#yesterday=`date -d -1days +"%Y-%m-%d"`
DIR=`pwd`
today=`date +"%Y-%m-%d"`
hour=`date -d -1hours +"%H"`

now_time=$(date +%Y-%m-%d-%H:%M:%S)
echo "-- imp hour start...time:$now_time"

if [ $# = 0 ]; then
	theday=$today
	thehour=$hour
else
	theday=$1
	thehour=$2
fi

cd $DIR

if [ ! -d $theday ]; then
	mkdir -p $theday
fi

# To unzip compressed dump file
gz_file=${DIR}/data/jhs_hour_${theday}_${thehour}.tar.gz
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
	
	/bin/sh $DIR/imp_t_hour.sh $line $theday $thehour
done < $DIR/jhs_tbl_hour.list

now_time=$(date +%Y-%m-%d-%H:%M:%S)
echo "-- imp hour end...time:$now_time"
exit;
