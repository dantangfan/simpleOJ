#!/bin/bash

sudo kill `ps -aux | grep debug.py | awk '{print $2}'`
