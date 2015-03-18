#!/bin/bash

kill -s 9 `ps -ef|grep $1|grep $2|grep -v grep|awk '{print $2}'`
