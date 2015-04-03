#!/bin/bash

DIR=`pwd`
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

if [ ! -d ${DIR}/${day}/day_${day} ]; then
	echo " Directory ${DIR}/${day}/day_${day} is not existed"
	exit 2
fi

db_user=bduser
db_passwd=newword!@#
db_name=bigdata

echo "To import ${day}/day_${day}/${tbl_name}_${day}.sql to ${db_name}.${tbl_name}"
/usr/bin/mysql -u$db_user -p"$db_passwd" $db_name < ${DIR}/${day}/day_${day}/${tbl_name}_${day}.sql
