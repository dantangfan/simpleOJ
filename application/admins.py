#coding=utf-8
from application import admin, models, db
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose
from urlparse import urljoin
import flask_login
from flask import request
import urllib2,re
import json
import sys
from datetime import datetime



class MyModelView(ModelView):
    def is_accessible(self):
        if flask_login.current_user.get_id() is None:
            return False
        return flask_login.current_user.is_admin()

class MyProblemModelView(ModelView):
    can_create = False
    column_list = ('owner_contest_id', 'owner_road_id', 'original_oj', 'original_oj_id', 'title', 'hint')
    def is_accessible(self):
        if flask_login.current_user.get_id() is None:
            return False
        return ('manage problem' in flask_login.current_user.group.split('|'))

class MyUserModelView(ModelView):
    def is_accessible(self):
        if flask_login.current_user.get_id() is None:
            return False
        return ('manage user' in flask_login.current_user.group.split('|'))

class MyNewsModelView(ModelView):
    def is_accessible(self):
        if flask_login.current_user.get_id() is None:
            return False
        return ('manage news' in flask_login.current_user.group.split('|'))

class MyContestModelView(ModelView):
    list_template = "admin/list_contest.html"
    def is_accessible(self):
        if flask_login.current_user.get_id() is None:
            return False
        return ('manage contest' in flask_login.current_user.group.split('|'))

    @expose('/submit', methods=('GET','POST',))
    def submit(self):
        if request.method == 'POST':
            try:
                contest_id = int(request.form['id'])
                if contest_id != 0:
                    cont = models.Contest.query.get(contest_id)
                    cont.title = request.form['title']
                    cont.description = request.form['description']
                    cont.start_time = request.form['start_time']
                    cont.end_time = request.form['end_time']
                else:
                    cont = models.Contest(request.form['title'],request.form['description'],request.form['start_time'],request.form['end_time'])
                    db.session.add(cont)
                db.session.commit()
                return json.dumps({"result" : "ok"})
            except Exception, e:
                db.session.rollback()
                return json.dumps({"result" : "Adding contest failed." + str(e)})
    @expose('/del_problem', methods=('GET','POST',))
    def del_problem(self):
        if request.method == 'POST':
            try:
                problem_id = int(request.form['pid'])
                contest_id = int(request.form['cid'])
                cont = models.Contest.query.get(contest_id)
                if cont is None: raise Exception('contest not found.')
                problems = map(int, cont.problems.split('|'))
                problems.remove(problem_id)
                txt = ""
                for x in problems:
                    if txt != "": txt = txt + "|"
                    txt = txt + str(x)
                cont.problems = txt
                db.session.commit()
                return json.dumps({"result" : "ok"})
            except Exception, e:
                db.session.rollback()
                return json.dumps({"result" : "delete problem failed." + str(e)})

    @expose('/modify/<int:id>')
    def request_1(self, id):
        try:
            cont = models.Contest.query.get(id)
            if cont is None: raise("contest not found.")
            problem_list = []
            if cont.problems is not None and cont.problems != "":
                problem_list=map(int,cont.problems.split('|'))
            problems=[]
            for item in problem_list:
                problems.append(models.Problem.query.get(item))
            return self.render('admin/edit_contest.html', 
                contest=cont,
                number_list=range(0,len(problem_list)),
                problems=problems,
                contest_id=cont.id)
        except Exception, e:
            return self.render('exception.html', message=str(e))

class MySubmissionModelView(ModelView):
    can_create = False
    def is_accessible(self):
        if flask_login.current_user.get_id() is None:
            return False
        return ('manage submission' in flask_login.current_user.group.split('|'))
        
class MyForumModelView(ModelView):
    can_create = False
    def is_accessible(self):
        if flask_login.current_user.get_id() is None:
            return False
        return ('manage forum' in flask_login.current_user.group.split('|'))

class Add_HDOJ_Problem_View(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/request_id.html')

    @expose('/submit', methods=('GET','POST',))
    def submit(self):
        if request.method == 'POST':
            try:
                cid = int(request.form['selected_contest'])
                if cid == -1: 
                    cid = None 
                else:
                    cont = models.Contest.query.get(cid)
                    if cont is None: raise Exception("The selected contest does not exsit.")
                p = models.Problem(cid, None, request.form['original_oj'], request.form['original_oj_id'], request.form['title'], request.form['memory_limit'], request.form['time_limit'], request.form['description'], request.form['input'], request.form['output'], request.form['sample_input'], request.form['sample_output'], request.form['hint'])
                db.session.add(p)
                db.session.commit()
                if cid != None:
                    if cont.problems != "":
                        cont.problems = cont.problems + "|"
                    cont.problems = cont.problems + str(p.id)
                    db.session.commit()
                return json.dumps({"result" : "ok"})
            except Exception, e:
                db.session.rollback()
                return json.dumps({"result" : "Adding problem failed."})
        

    @expose('/request/<int:hdoj_id>')
    def request_1(self, hdoj_id):
        last_sub = []
        try:
            reload(sys)
            sys.setdefaultencoding('gb2312')
            problem_url = "http://acm.hdu.edu.cn/showproblem.php?pid=" + str(hdoj_id)
            response = urllib2.urlopen(problem_url)
            text  = response.read()
            match = re.compile('<h1 style=\'color:#1A5CC8\'>(.*?)<\/h1>.*?Time Limit.*?\/(\d*).*?Problem Description.*?<div class=panel_content>(.*?)<\/div>.*?Input.*?<div class=panel_content>(.*?)<\/div>.*?Output.*?<div class=panel_content>(.*?)<\/div>.*?Sample Input.*?<div class=panel_content><pre>.*?>(.*?)<\/.*?<\/pre>.*?Sample Output.*?<pre>.*?>(.*?)<\/?div.*?<\/pre>', re.M | re.S)
            last_sub = match.findall(text)
            conts = models.Contest.query.filter(models.Contest.end_time > datetime.now()).all()
            problem = {}
            problem['title'] = last_sub[0][0]
            problem['original_oj_id'] = hdoj_id
            problem['original_oj'] = 'HDOJ'
            problem['time_limit'] = "1S"
            problem['memory_limit'] = "65535K"
            problem['description'] = last_sub[0][2]
            problem['input'] = last_sub[0][3]
            problem['output'] = last_sub[0][4]
            problem['sample_input'] = last_sub[0][5]
            problem['sample_output'] = last_sub[0][6]
            problem['hint'] = ""
            problem['sample_input'] = problem['sample_input'].replace('\r\n', '<br/>')
            problem['sample_output'] = problem['sample_output'].replace('\r\n', '<br/>')
            for item in problem:
                if type(problem[item]) != str: continue
                match = re.compile('<img\s*?src\s*?=\s*?\'?\"?(.*?)\'?\"?\s*?>', re.M | re.S)
                links = match.findall(problem[item])
                for link in links:
                    newUrl = urljoin("http://acm.hdu.edu.cn/", link)
                    problem[item] = problem[item].replace(link, newUrl)
            return self.render('admin/problem_form.html', problem=problem,contests=conts)
        except Exception, e:
            return self.render('exception.html', message=str(e))

    def is_accessible(self):
        if flask_login.current_user.get_id() is None:
            return False
        return ('manage problem' in flask_login.current_user.group.split('|'))

class Add_PKUOJ_Problem_View(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/request_id.html')

    @expose('/submit', methods=('GET','POST',))
    def submit(self):
        if request.method == 'POST':
            try:
                cid = int(request.form['selected_contest'])
                if cid == -1: 
                    cid = None
                else:
                    cont = models.Contest.query.get(cid)
                    if cont is None: raise Exception("The selected contest does not exsit.")
                p = models.Problem(cid, None, request.form['original_oj'], request.form['original_oj_id'], request.form['title'], request.form['memory_limit'], request.form['time_limit'], request.form['description'], request.form['input'], request.form['output'], request.form['sample_input'], request.form['sample_output'], request.form['hint'])
                db.session.add(p)
                db.session.commit()
                if cid != None:
                    if cont.problems != "":
                        cont.problems = cont.problems + "|"
                    cont.problems = cont.problems + str(p.id)
                    db.session.commit()
                return json.dumps({"result" : "ok"})
            except Exception, e:
                db.session.rollback()
                return json.dumps({"result" : "Adding problem failed."})
        

    @expose('/request/<int:oj_id>')
    def request_1(self, oj_id):
        last_sub = []
        try:
            reload(sys)
            sys.setdefaultencoding('utf-8')
            conts = models.Contest.query.filter(models.Contest.end_time > datetime.now()).all()
            problem_url = "http://poj.org/problem?id=" + str(oj_id)
            response = urllib2.urlopen(problem_url)
            text  = response.read()
            match = re.compile("<div style='position: absolute.*?<div class=\"ptt\".*?>(.*?)<\/div>.*?Description.*?<div class=\"ptx\".*?>(.*?)<\/div>.*?Input.*?<div class=\"ptx\".*?>(.*?)<\/div>.*?Output.*?<div class=\"ptx\".*?>(.*?)<\/div>.*?Sample Input.*?<pre.*?>(.*?)<\/pre>.*?Sample Output.*?<pre.*?>(.*?)<\/pre>", re.M | re.S)
            last_sub = match.findall(text)
            problem = {}
            problem['title'] = last_sub[0][0]
            problem['original_oj_id'] = oj_id
            problem['original_oj'] = 'PKUOJ'
            problem['time_limit'] = "1S"
            problem['memory_limit'] = "65535K"
            problem['description'] = last_sub[0][1]
            problem['input'] = last_sub[0][2]
            problem['output'] = last_sub[0][3]
            problem['sample_input'] = last_sub[0][4]
            problem['sample_output'] = last_sub[0][5]
            problem['hint'] = ""
            problem['sample_input'] = problem['sample_input'].replace('\r\n', '<br/>')
            problem['sample_output'] = problem['sample_output'].replace('\r\n', '<br/>')
            for item in problem:
                if type(problem[item]) != str: continue
                match = re.compile('<img\s*?src\s*?=\s*?\'?\"?(.*?)\'?\"?\s*?>', re.M | re.S)
                links = match.findall(problem[item])
                for link in links:
                    newUrl = urljoin("http://poj.org/", link)
                    problem[item] = problem[item].replace(link, newUrl)
            return self.render('admin/problem_form.html', problem=problem, contests=conts)
        except Exception, e:
            return self.render('exception.html', message=str(e))

    def is_accessible(self):
        if flask_login.current_user.get_id() is None:
            return False
        return ('manage problem' in flask_login.current_user.group.split('|'))
        



admin.add_view(MyUserModelView(models.User, db.session))
admin.add_view(MyProblemModelView(models.Problem, db.session, category='Problem'))
admin.add_view(MyNewsModelView(models.News, db.session))
admin.add_view(MyForumModelView(models.Forum, db.session))
admin.add_view(MyContestModelView(models.Contest, db.session))
admin.add_view(MySubmissionModelView(models.Submission, db.session))
admin.add_view(Add_HDOJ_Problem_View(name='Add HDOJ Problem', category='Problem'))
admin.add_view(Add_PKUOJ_Problem_View(name='Add PKU OJ Problem', category='Problem'))

        