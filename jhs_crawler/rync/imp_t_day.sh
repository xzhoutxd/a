#!/bin/bash

DIR=/home/har/jhs/crawler_v2/jhsdata/dump/sql
yesterday=`date -d -1days +"%Y-%m-%d"`

if [ $# = 0 ]; then 
	echo " Usage: $0 TableName TheDate" 
	echo " e.g. : $0 nd_jhs_rpt_item_info 2015-02-28" 
	exit 1
elif [ $# = 1 ]; then
	tbl_name=$1
	day=$yesterday
else
	tbl_name=$1
	day=$2
fi

if [ ! -d $DIR/$day ]; then
	echo " Directory $DIR/$day is not existed"
	exit 2
fi

db_host=192.168.1.112
db_user=jhs
db_passwd=123456
db_name=jhs

echo "To import ${day}/${tbl_name}_${day}.sql to $db_name.$tbl_name"
/usr/bin/mysql -h$db_host -u$db_user -p"$db_passwd" $db_name < $DIR/${day}/${tbl_name}_${day}.sql
