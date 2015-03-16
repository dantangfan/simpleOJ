#!/bin/bash

sudo kill `ps -aux | grep worker.py | awk '{print $2}'`
for((i=0;i<4;i++))
do
    nohup python run_judger.py &
done