#!/bin/bash

#yesterday=`date -d -1days +"%Y-%m-%d"`
DIR=`pwd`
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
	echo " Directory ${DIR}/${day}/${hour} is not existed"
	exit 2
fi

db_user=bduser
db_passwd=newword!@#
db_name=bigdata

echo "To import ${day}/${hour}/${tbl_name}_${day}.sql to ${db_name}.${tbl_name}"
/usr/bin/mysql -u$db_user -p"$db_passwd" $db_name < ${DIR}/${day}/${hour}/${tbl_name}_${day}.sql
