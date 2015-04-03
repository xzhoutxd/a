#!/bin/bash

DIR=`pwd`
#yesterday=`date -d -1days +"%Y-%m-%d"`
today=`date +"%Y-%m-%d"`
hour=`date -d -1hours +"%H"`

now_time=$(date +%Y-%m-%d-%H:%M:%S)
echo "-- sync hour start...time:$now_time"

if [ $# = 0 ]; then
	theday=$today
        thehour=$hour
elif [ $# = 1 ]; then
	echo " Usage: $0 TheDate TheHour" 
        echo " e.g. : $0 2015-02-28 00" 
        exit 1
else
	theday=$1
        thehour=$2
fi

cd $DIR

# Remote host
remote_user=netdata
remote_host=qzj01
remote_path=/home/netdata/workspace/datasync/jhs/sql/data 

# The mysql table dump file
dmp_dir=${thehour}
dmp_name=${theday}_${thehour}
tar_file=jhs_hour_$dmp_name.tar
gz_file=jhs_hour_${dmp_name}.tar.gz

# To sync the compressed file
cd $DIR/$theday
tar cvf ${tar_file} ${dmp_dir}
gzip -9f ${tar_file}

echo "To sync the gzip file ${gz_file}"
scp ${gz_file} ${remote_user}@${remote_host}:${remote_path}

now_time=$(date +%Y-%m-%d-%H:%M:%S)
echo "-- sync hour end...time:$now_time"
exit;
