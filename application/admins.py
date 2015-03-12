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
    #can_create = False
    can_delete = False
    column_list = ('id', 'owner_contest_id', 'owner_road_id', 'title', 'memory_limit', 'time_limit','description', 'input', 'output', 'sample_input', 'sample_output','hint')
    def is_accessible(self):
        if flask_login.current_user.get_id() is None:
            return False
        return ('manage problem' in flask_login.current_user.group.split('|'))

class MyUserModelView(ModelView):
    can_delete = False
    can_create = False
    can_edit = False
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
    can_delete = False
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




admin.add_view(MyUserModelView(models.User, db.session))
admin.add_view(MyProblemModelView(models.Problem, db.session))
admin.add_view(MyNewsModelView(models.News, db.session))
admin.add_view(MyForumModelView(models.Forum, db.session))
admin.add_view(MyContestModelView(models.Contest, db.session))
admin.add_view(MySubmissionModelView(models.Submission, db.session))

