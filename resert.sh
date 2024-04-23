#!/bin/bash


# 在当前进程中查找 python qqbot 的进程号然后终止

pid=$(ps -ef | grep qqbot | grep -v grep | awk '{print $2}')
if [ -n "$pid" ]; then
    kill -9 $pid
    echo "kill qqbot process: $pid"
else
    echo "qqbot process not found"
fi

# 重新启动 qqbot
nohup python qqbot.py &