#!/usr/bin/env python
# -*- coding:utf-8 -*-

from xml.dom.minidom import parse
import os
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

from application import db
from application.models import Problem
from config import problem_dir, problem_xml_dir


def test_one():

    os.chdir(problem_xml_dir)
    DOMTree = parse("fps-A_plus_B.-Img-demo.xml")
    collection = DOMTree.documentElement
    problems = collection.getElementsByTagName("item")
    print len(problems)
    for problem in problems:
        title = problem.getElementsByTagName('title')
        title = title[0].childNodes[0].data
        print "Title: %s" % title
        description = problem.getElementsByTagName('description')
        description = description[0].childNodes[0].data
        print "description: %s" % description


def check_testdata_in():
    os.chdir(problem_xml_dir)
    pwd = os.getcwd()
    file_names = os.listdir(pwd)
    print len(file_names)
    i = 0
    not_in = []
    for one in file_names:
        content = open(one).read()
        if content.find("test_output"):
            i += 1
        else:
            not_in.append(one)
    print i


def make_problem():
    os.chdir(problem_dir)
    os.system("rm -rf *")
    os.chdir(problem_xml_dir)
    pwd = os.getcwd()
    file_names = os.listdir(pwd)
    count = 0
    for one in file_names:
        try:
            DOMTree = parse(one)
        except Exception, e:
            print one, e
            continue
        collection = DOMTree.documentElement
        problems = collection.getElementsByTagName("item")
        for problem in problems:
            try:
                title = problem.getElementsByTagName('title')
                title = title[0].childNodes
                if title:
                    title = title[0].data
                time_limit = problem.getElementsByTagName('time_limit')
                time_limit = time_limit[0].childNodes
                if time_limit:
                    time_limit = time_limit[0].data
                memory_limit = problem.getElementsByTagName('memory_limit')
                memory_limit = memory_limit[0].childNodes
                if memory_limit:
                    memory_limit = memory_limit[0].data
                description = problem.getElementsByTagName('description')
                description = description[0].childNodes
                if description:
                    description = description[0].data
                input = problem.getElementsByTagName('input')
                input = input[0].childNodes
                if input:
                    input = input[0].data
                output = problem.getElementsByTagName('output')
                output = output[0].childNodes
                if output:
                    output = output[0].data
                sample_input = problem.getElementsByTagName('sample_input')
                sample_input = sample_input[0].childNodes
                if sample_input:
                    sample_input = sample_input[0].data
                sample_output = problem.getElementsByTagName('sample_output')
                sample_output = sample_output[0].childNodes
                if sample_output:
                    sample_output = sample_output[0].data
                hint = problem.getElementsByTagName('hint')
                hint = hint[0].childNodes
                if hint:
                    hint = hint[0].data
                solution = problem.getElementsByTagName('solution')
                solution = solution[0].childNodes
                if solution:
                    solution = solution[0].data

                # make test cases
                test_input = problem.getElementsByTagName('test_input')
                test_output = problem.getElementsByTagName('test_output')
                if len(test_input) != len(test_output):
                    print "test_case error", len(test_input), len(test_output), one, title
                    continue
                if len(test_input) == 0:
                    print "no test cases", one, title
                    continue
                p = Problem(owner_contest_id=None,
                            owner_road_id=21,
                            title=title,
                            memory_limit=str(int(memory_limit)*1024)+"K",
                            time_limit=str(time_limit)+"S",
                            description=description,
                            input=input,
                            output=output,
                            sample_input=sample_input,
                            sample_output=sample_output,
                            hint=hint,
                            solution=solution,
                            submit_count=0,
                            acc_count=0)
                db.session.add(p)
                os.chdir(problem_dir)
                new_dir_name = str(count+1)
                os.mkdir(new_dir_name)
                os.chdir(new_dir_name)
                for index in range(len(test_input)):
                    case_in = test_input[index].childNodes
                    if case_in:
                        case_in = case_in[0].data
                    case_out = test_output[index].childNodes
                    if case_out:
                        case_out = case_out[0].data
                    fin = open(str(index)+'.in', 'w')
                    fout = open(str(index)+'.out', 'w')
                    fin.write(case_in)
                    fout.write(case_out)
                    fin.close()
                    fout.close()
                os.chdir(problem_xml_dir)
                '''
                print title
                print time_limit
                print memory_limit
                print description
                print input
                print output
                print sample_input
                print sample_output
                print hint
                print solution
                '''
                count += 1
                if count % 10:
                    db.session.commit()
            except Exception, e:
                print e, one, title
                continue
        if count >= 30:
            break


if __name__ == "__main__":
    # test_one()
    make_problem()