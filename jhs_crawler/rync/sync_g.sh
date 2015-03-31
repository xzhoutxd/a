#!/bin/bash

#yesterday=`date -d -1days +"%Y-%m-%d"`
today=`date +"%Y-%m-%d"`

if [ $# = 0 ]; then
	theday=$today
else
	theday=$1
fi

# Remote host
remote_user=mysql
remote_host=192.168.1.112
remote_path=/home/mysql/dump 

# The mysql table dump file
dmp_dir=${theday}
gz_file=jhs_${dmp_dir}.tar.gz

# To sync the compressed file
tar cvf jhs_$dmp_dir.tar $dmp_dir
gzip -9 jhs_$dmp_dir.tar

echo "To sync the gzip file $gz_file"
scp ${gz_file} ${remote_user}@${remote_host}:${remote_path}
