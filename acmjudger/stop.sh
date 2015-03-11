#!/bin/bash

sudo kill `ps -aux | grep worker.py | awk '{print $2}'`
