#!/usr/bin/env python
# -*- coding:utf-8

from judger import judger
from dbmanager import redis_q
from config import submission_queue_key
from application import db
from application.models import User, Problem, Submission
import logging
import datetime

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='judger.log',
                filemode='w')


def run():
    while True:
        submission_id = redis_q.brpop(submission_queue_key, 0)[1]
        rst = judger(submission_id)
        write_back(submission_id, rst)
        logging.info(str(datetime.datetime.now())+' '+str(submission_id)+' '+rst['result'])


def write_back(submission_id, rst):
    submission = Submission.query.filter_by(id=submission_id).first()
    user = User.query.filter_by(id=submission.user_id).first()
    problem = Problem.query.filter_by(id=submission.problem_id).first()
    if rst['result'] == "Accepted":
        time_used = str(rst['timeused'])+'MS'
        memory_used = str(rst['memoryused'])+'K'
        sql = "update submission set memory_used='%s', time_used='%s', result='%s' where id=%s limit 1"
        db.session.execute(sql % (memory_used, time_used, rst['result'], submission_id))
        sql = "update user set acc_count=%s where id=%s"
        db.session.execute(sql % (user.acc_count+1, user.id))
        sql = "update problem set acc_count=%s where id=%s"
        db.session.execute(sql % (problem.acc_count+1, problem.id))
    else:
        sql = "update submission set result = '%s' where id = %s"
        db.session.execute(sql % (rst['result'], submission_id))
    db.session.commit()

if __name__ == "__main__":
    run()