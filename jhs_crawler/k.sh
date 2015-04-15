#!/bin/bash

kill -s 9 `ps -ef | grep $1 | grep python | grep -v grep | awk '{print $2}'`
