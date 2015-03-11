#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
import torndb
from redisClient import RedisClient
from config import mysql_db_name,mysql_host,mysql_password,mysql_user,redis_server,redis_port

while 1:
    try:
        db = torndb.Connection(mysql_host, mysql_db_name, mysql_user, mysql_password)
        break
    except:
        logging.error("SQL connection error")

db.execute("set names utf8")

redis_q = RedisClient(host=redis_server,port=redis_port,db=0)