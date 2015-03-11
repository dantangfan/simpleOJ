#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import lorun
import logging
from compile import compile
from db import db
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
    user_id = info['user_id']
    language = info['compiler']
    problem_id = info['problem_id']
    if not compile(user_id, submission_id, language):
        return {'result':RESULT_STR[7]}
    testcase_count = get_total_testcase_count(problem_id)
    exe_name = '%s_%s' % (user_id, submission_id)
    for i in range(testcase_count):
        sample_input_path = os.path.join(config.problem_dir, str(problem_id), '%s.in' % i)
        sample_output_path = os.path.join(config.problem_dir, str(problem_id), '%s.out' % i)
        if os.path.isfile(sample_input_path) and os.path.isfile(sample_output_path):
            rst = run_one(exe_name, sample_input_path, sample_output_path, problem_id, language)
            rst['result'] = RESULT_STR[rst["result"]]
        else:
            print 'testdata:%s incompleted' % i
            os.remove(exe_name)
            return {'result':RESULT_STR[8]}
    return rst
    os.remove(exe_name)

run_cmd = {
    'gcc':'./%s',
    'g++':'./%s',
    'python':'python %s'
}

def run_one(exe_name, sample_input_path, sample_output_path, problem_id, language):
    fin = open(sample_input_path)
    ftemp = open(exe_name+'temp.out','w')
    info = db.get("select time_limit, memory_limit from problem where id = %s", problem_id)
    # 这里的time和limit都有单位，以后改成没有单位
    time_limit = info['time_limit']
    memory_limit = info['memory_limit']
    time_limit = int(time_limit[0:-1])
    memory_limit = int(memory_limit[0:-1])
    runcfg = {
        'args':[run_cmd[language]%exe_name],
        'fd_in':fin.fileno(),
        'fd_out':ftemp.fileno(),
        'timelimit':time_limit*1000,
        'memorylimit':memory_limit*1024
    }
    rst = lorun.run(runcfg)
    fin.close()
    ftemp.close()
    if not rst['result']:
        ftemp = open(exe_name+'temp.out')
        fout = open(sample_output_path)
        crst = lorun.check(fout.fileno(),ftemp.fileno())
        fout.close()
        ftemp.close()
        os.remove(exe_name+'temp.out')
        if crst != 0:
            return {"result": crst}
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

