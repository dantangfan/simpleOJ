#!/bin/bash

sudo kill `ps -aux | grep worker.py | awk '{print $2}'`
for((i=0;i<4;i++))
do
    nohup python debug.py runserver --host 0.0.0.0 &
done