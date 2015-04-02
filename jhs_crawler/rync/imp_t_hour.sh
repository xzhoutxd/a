#!/bin/bash

#yesterday=`date -d -1days +"%Y-%m-%d"`
DIR=/home/har/jhs/crawler_v2/jhsdata/dump/sql
today=`date +"%Y-%m-%d"`
hour=`date -d -1hours +"%H"`

if [ $# = 0 ]; then 
	echo " Usage: $0 TableName TheDate TheHour" 
	echo " e.g. : $0 nd_jhs_rpt_item_info 2015-02-28 00" 
	exit 1
elif [ $# = 1 ]; then
	tbl_name=$1
	day=$today
	hour=$hour
else
	tbl_name=$1
	day=$2
	hour=$3
fi

if [ ! -d $DIR/$day/$hour ]; then
	echo " Directory $DIR/$day/$hour is not existed"
	exit 2
fi

db_host=192.168.1.112
db_user=jhs
db_passwd=123456
db_name=jhs

echo "To import ${day}/${hour}/${tbl_name}_${day}.sql to $db_name.$tbl_name"
/usr/bin/mysql -h$db_host -u$db_user -p"$db_passwd" $db_name < $DIR/${day}/${hour}/${tbl_name}_${day}.sql
