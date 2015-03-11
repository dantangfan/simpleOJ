#!/usr/bin/env python
# -*- coding:utf-8

from judger import judger
from dbmanager import db, redis_q
from config import submission_queue_key
def run():
    while True:
        submission_id = redis_q.brpop(submission_queue_key, 0)
        rst = judger(submission_id)
        write_back(submission_id, rst)


def write_back(submission_id, rst):
    if rst['result']=="Accepted":
        time_used = str(rst['timeused'])+'MS'
        memory_used = str(rst['memoryused'])+'K'
        sql = "update submission set memory_used = %s, time_used = %s, result = %s where id = %s limit 1"
        db.execute(sql, memory_used, time_used,rst['result'], submission_id)
    else:
        sql = "update submission set result = %s where id = %s limit 1"
        db.execute(sql, rst['result'], submission_id)

run()