#!/bin/bash
today=`date +"%Y-%m-%d"`
hour=`date +"%H"`
if [ $# = 0 ]; then
        p_crawl_date=$today
        str_hour=$hour
else
        p_crawl_date=$1
        str_hour=$2
fi

mysql -h 192.168.1.113 -u jhs -p123456 jhs <<EOF
       call sp_jhs_stat_dim($p_crawl_date,$str_hour);
       call sp_jhs_stat_hour($p_crawl_date,$str_hour);
EOF
exit;
