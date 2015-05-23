#!/bin/bash
today=`date +"%Y-%m-%d"`
hour=`date +"%H"`
#运行统计脚本
now_time=$(date +%Y-%m-%d-%H:%M:%S)
echo "-- run start...time:$now_time"
if [ $# = 0 ]; then
        p_crawl_date=$today
        str_hour=$hour
else
        p_crawl_date=$1
        str_hour=$2
fi

echo "date:$p_crawl_date"
echo "hour:$str_hour"

mysql -h 192.168.1.113 -u jhs -p123456 jhs<<EOF
       call sp_jhsitemgroup_stat_hour('$p_crawl_date',$str_hour);
       call sp_jhsitemgroup_stat_dim('$p_crawl_date',$str_hour);
EOF
now_time=$(date +%Y-%m-%d-%H:%M:%S)
echo "-- run end...time:$now_time"
exit;
