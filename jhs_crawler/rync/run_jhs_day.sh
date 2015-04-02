#!/bin/bash
today=`date +"%Y-%m-%d"`

if [ $# = 0 ]; then
        p_crawl_date=$today
else
        p_crawl_date=$1
fi

mysql -h 192.168.1.113 -u jhs -p123456 jhs <<EOF
        call sp_jhs_stat_day(p_crawl_date);
EOF
exit;
