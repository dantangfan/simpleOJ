#!/bin/bash

sudo kill `ps -aux | grep run_judger.py | awk '{print $2}'`
