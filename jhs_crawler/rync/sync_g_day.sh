#!/bin/bash

DIR=`pwd`
yesterday=`date -d -1days +"%Y-%m-%d"`

now_time=$(date +%Y-%m-%d-%H:%M:%S)
echo "-- sync day start...time:$now_time"

if [ $# = 0 ]; then
	theday=$yesterday
else
	theday=$1
fi

cd $DIR

# Remote host
remote_user=netdata
remote_host=qzj01
remote_path=/home/netdata/workspace/datasync/jhs/sql/data 

# The mysql table dump file
dmp_dir=day_${theday}
tar_file=jhs_day_${theday}.tar
gz_file=jhs_day_${theday}.tar.gz

# To sync the compressed file
cd $DIR/$theday
tar cvf ${tar_file} ${dmp_dir}
gzip -9f ${tar_file}

echo "To sync the gzip file ${gz_file}"
scp ${gz_file} ${remote_user}@${remote_host}:${remote_path}

now_time=$(date +%Y-%m-%d-%H:%M:%S)
echo "-- sync day end...time:$now_time"
exit;
