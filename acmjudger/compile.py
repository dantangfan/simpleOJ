#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import logging
from dbmanager import db
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

file_name = {
    "gcc": "main.c",
    "g++": "main.cpp",
    "java": "Main.java",
    'ruby': "main.rb",
    "perl": "main.pl",
    "pascal": "main.pas",
    "go": "main.go",
    "lua": "main.lua",
    'python2': 'main.py',
    'python3': 'main.py',
    "haskell": "main.hs"
}

build_cmd = {
    "gcc": "gcc main.c -o main -Wall -lm -O2 -std=c99 --static -DONLINE_JUDGE",
    "g++": "g++ main.cpp -O2 -Wall -lm --static -DONLINE_JUDGE -o main",
    "java": "javac Main.java",
    "ruby": "reek main.rb",
    "perl": "perl -c main.pl",
    "pascal": 'fpc main.pas -O2 -Co -Ct -Ci',
    "go": '/opt/golang/bin/go build -ldflags "-s -w"  main.go',
    "lua": 'luac -o main main.lua',
    "python2": 'python2 -m py_compile main.py',
    "python3": 'python3 -m py_compile main.py',
    "haskell": "ghc -o main main.hs",
}


def compile(submission_id, language):
    language = language.lower()
    if language not in build_cmd.keys():
        return False
    if not get_code(submission_id, language):
        return False
    if os.system(build_cmd[language]) != 0:
        return False
    return True


def get_code(submission_id, language):
    sql = "select code, judger_status from submission where id = %s"
    info = db.get(sql, submission_id)
    if not info:
        logging.warn("no such submission")
        return False
    code = info['code']
    f = open(file_name[language], 'w')
    f.write(code)
    f.close()
    return True


