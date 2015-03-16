#!/bin/bash

sudo kill `ps -aux | grep worker.py | awk '{print $2}'`

nohup python debug.py runserver --host 0.0.0.0 &
