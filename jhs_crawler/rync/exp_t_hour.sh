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
	mkdir -p $DIR/$day/$hour
fi

where_clause=update_date\=\"$day\"

db_host=db05
db_user=jhs
db_passwd=123456
db_name=jhs

echo "To export ${db_name}.${tbl_name} to ${day}/${hour}/${tbl_name}_${day}.sql"
/usr/bin/mysqldump -h$db_host -u$db_user -p"$db_passwd" $db_name $tbl_name -t -c -C --replace --compact -w"$where_clause" > ${DIR}/${day}/${hour}/${tbl_name}_${day}.sql
