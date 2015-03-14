#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import logging
from dbmanager import db
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


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
    "python2": 'python -m py_compile %s',
    "python3": 'python3 -m py_compile %s',
    "haskell": "ghc -o main %s.hs",
}

subnames = {
    'gcc':'c',
    'g++':'cpp',
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
        if  os.system(build_cmd[language] % (file_name, exe_name))!=0:
            os.remove(file_name)
            return False
    elif language=="python2":
        if os.system(build_cmd[language] % (file_name)) != 0:
            os.remove(file_name)
            return False
        os.system('mv %s.pyc %s' % (exe_name,exe_name))
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
    file_name = "%s_%s.%s" % (user_id, submission_id, sub)
    f = open(file_name, 'w' )
    f.write(code)
    f.close()
    return True


