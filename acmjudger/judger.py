#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import lorun
import logging
from compile import compile
from dbmanager import db
import config
'''
try:
    os.setuid(int(os.popen("id -u %s" % "nobody").read()))
except:
    logging.error("please run this program as root.")
    sys.exit(-1)
'''

RESULT_STR = [
    'Accepted',
    'Presentation Error',
    'Time Limit Exceeded',
    'Memory Limit Exceeded',
    'Wrong Answer',
    'Runtime Error',
    'Output Limit Exceeded',
    'Compile Error',
    'System Error'
]


def judger(submission_id):
    sql = "select user_id, compiler, problem_id from submission where id=%s"
    info = db.get(sql, submission_id)
    if not info:
        logging.warn("no such submission %s" % submission_id)
        return {'result': RESULT_STR[7]}
    language = info['compiler']
    problem_id = info['problem_id']
    work_dir = str(submission_id)
    try:
        os.mkdir(work_dir)
        os.chdir(work_dir)
    except Exception, e:
        logging.error(e)
        return {'result': RESULT_STR[8]}
    try:
        rst = judge(submission_id, problem_id, language)
        os.chdir("../")
        os.system("rm -rf %s" % work_dir)
    except Exception, e:
        logging.error(e)
        rst = {'result': RESULT_STR[8]}
    return rst

def judge(submission_id, problem_id, language):
    if not compile(submission_id, language):
        return {'result': RESULT_STR[7]}
    testcase_count = get_total_testcase_count(problem_id)
    timeused = 0
    memoryused = 0
    info = db.get("select time_limit, memory_limit from problem where id = %s", problem_id)
    if not info:
        logging.warn("no such Problem %s" % (problem_id))
        return {'result':RESULT_STR[8]}
    # 这里的time和limit都有单位，以后改成没有单位
    time_limit = info['time_limit']
    memory_limit = info['memory_limit']
    time_limit = int(time_limit[0:-1])
    memory_limit = int(memory_limit[0:-1])
    if language == "python2" or language == "python3" or language == "java":
        time_limit *= 2
        memory_limit *= 2
    for i in range(testcase_count):
        sample_input_path = os.path.join(config.problem_dir, str(problem_id), '%s.in' % i)
        sample_output_path = os.path.join(config.problem_dir, str(problem_id), '%s.out' % i)
        if os.path.isfile(sample_input_path) and os.path.isfile(sample_output_path):
            rst = run_one(sample_input_path, sample_output_path, time_limit, memory_limit, language)
            rst['result'] = RESULT_STR[rst["result"]]
            if rst['result'] != RESULT_STR[0]:
                return rst
            if rst['timeused']>timeused:
                timeused = rst['timeused']
            if rst['memoryused']>memoryused:
                memoryused = rst['memoryused']
        else:
            logging.error('testdata:%s incompleted' % i)
            return {'result':RESULT_STR[8]}
    rst['timeused']=timeused
    rst['memoryused']=memoryused
    return rst



def run_one(sample_input_path, sample_output_path, time_limit, memory_limit, language):
    fin = open(sample_input_path)
    ftemp = open('temp.out', 'w')
    runcfg = {
        'args': get_runcmd(language),
        'fd_in': fin.fileno(),
        'fd_out': ftemp.fileno(),
        'timelimit': time_limit*1000,
        'memorylimit': memory_limit*1024
    }
    rst = {}
    try:
        rst = lorun.run(runcfg)
    except Exception, e:
        print 'lorun.run.error:', e
        logging.error(e)
        rst['result'] = 8
    fin.close()
    ftemp.close()
    if not rst['result']:
        ftemp = open('temp.out')
        fout = open(sample_output_path)
        try:
            crst = lorun.check(fout.fileno(), ftemp.fileno())
        except Exception, e:
            logging.error(e)
            rst['result'] = 8
        fout.close()
        ftemp.close()
        if crst != 0:
            return {"result": crst}
        os.remove('temp.out')
    return rst


def get_total_testcase_count(problem_id):
    full_path = os.path.join(config.problem_dir, str(problem_id))
    try:
        files = os.listdir(full_path)
    except OSError as e:
        logging.error(e)
        return False
    count = 0
    for item in files:
        if item.endswith('.in'):
            count += 1
    return count

def get_runcmd(language):
    if language == 'java':
        cmd = 'java Main'
    elif language == 'python2':
        cmd = 'python2 main.pyc'
    elif language == 'python3':
        cmd = 'python3 main.pyc'
    elif language == 'lua':
        cmd = "lua main"
    elif language == "ruby":
        cmd = "ruby main.rb"
    elif language == "perl":
        cmd = "perl main.pl"
    else:
        cmd = './main'
    return cmd.split()