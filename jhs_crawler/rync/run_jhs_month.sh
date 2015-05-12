#!/bin/bash
today=`date +"%Y-%m-%d"`

#运行统计脚本
now_time=$(date +%Y-%m-%d-%H:%M:%S)
echo "-- run start...time:$now_time"
if [ $# = 0 ]; then
        p_date=$today
else
        p_date=$1
fi

echo "date:$p_date"

mysql -h 192.168.1.113 -u jhs -p123456 jhs <<EOF
        call sp_jhs_stat_month('$p_date','$p_date');
EOF
now_time=$(date +%Y-%m-%d-%H:%M:%S)
echo "-- run end...time:$now_time"
exit;
