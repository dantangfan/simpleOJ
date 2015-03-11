#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import logging
from dbmanager import db


build_cmd = {
    "gcc":
    "gcc %s -o %s ",
    "g++": "g++ %s -O2 -Wall -lm --static -DONLINE_JUDGE -o %s",
    "java": "javac %s.java",
    "ruby": "reek %s.rb",
    "perl": "perl -c %s.pl",
    "pascal": 'fpc %s.pas -O2 -Co -Ct -Ci',
    "go": '/opt/golang/bin/go build -ldflags "-s -w" %s.go',
    "lua": 'luac -o main %s.lua',
    "python2": 'python2 -m py_compile %s.py',
    "python3": 'python3 -m py_compile %s.py',
    "haskell": "ghc -o main %s.hs",
}

subnames = {
    'gcc':'c',
    'g++':'c++',
    'java':'java',
    'ruby':'rb',
    'perl':'pl',
    'pascal':'pas',
    'go':'go',
    'lua':'lua',
    'python2':'py',
    'python3':'py',
    'haskell':'hs'
}

def compile(user_id, submission_id, language):
    language = language.lower()
    if language not in build_cmd.keys():
        return False
    if not get_code(submission_id, user_id, language):
        return False
    exe_name = str(user_id)+'_'+str(submission_id)
    file_name = exe_name+'.'+subnames[language]
    if language=="gcc" or language=="g++":
        os.system(build_cmd[language] % (file_name, exe_name))
    elif language=="python":
        os.system(build_cmd[language] % (file_name))
        os.system('mv %s.pyc %s',(exe_name, exe_name))
    os.remove(file_name)
    return True

#file name is user_id+_+submission_id.*
def get_code(submission_id, user_id, language):
    sql = "select code, judger_status from submission where id = %s"
    info = db.get(sql, submission_id)
    code = info['code']
    status = info['judger_status']
    #if status==-1:
    #    return False
    sub = subnames[language]
    f = open('%s_%s.%s' % (user_id, submission_id, sub), 'w' )
    f.write(code)
    f.close()
    return True


