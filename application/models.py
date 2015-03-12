#!/usr/bin/env python
# coding=utf-8
from application import db
from datetime import datetime


class User(db.Model):
    """entity for user"""
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    hj_oj_username = db.Column(db.String(128), unique=True)
    last_login_time = db.Column(db.DateTime)
    group = db.Column(db.Text, default='user')

    def is_authenticated(self):
        if 'user' in self.group.split('|'):
            return True
        else:
            return False

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def get_email(self):
        return unichr(self.email)

    def is_admin(self):
        if 'admin' in self.group.split('|'):
            return True
        else:
            return False


    def __init__(self, username="", password="", email="", hj_oj_username="", last_login_time=datetime.now()):
        self.username = username
        self.password = password
        self.email = email
        self.hj_oj_username = hj_oj_username
        self.last_login_time = last_login_time
        
    def __repr__(self):
        return "<user %r>" % self.username

class News(db.Model):
    """entity for news"""
    __tablename__ = "news"
    id = db.Column(db.Integer, primary_key=True)
    publish_time = db.Column(db.DateTime, nullable=False)
    title = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text)


    def __init__(self, publish_time=datetime.now(), title="", content=""):
        self.publish_time = publish_time
        self.title = title
        self.content = content

    def __repr__(self):
        return "<news %r>" % self.title
        
    
class Problem(db.Model):
    """entity for problem"""
    __tablename__ = "problem"
    id = db.Column(db.Integer, primary_key=True)
    owner_contest_id = db.Column(db.Integer)  # if has value, this problem will not show in the public problem list
    owner_road_id = db.Column(db.Integer)
    title = db.Column(db.Text, nullable = False)
    memory_limit = db.Column(db.Text)
    time_limit = db.Column(db.Text)
    description = db.Column(db.Text)
    input = db.Column(db.Text)
    output = db.Column(db.Text)
    sample_input = db.Column(db.Text)
    sample_output = db.Column(db.Text)
    hint = db.Column(db.Text)

    def __init__(self, owner_contest_id, owner_road_id, title, memory_limit, time_limit, description, input, output, sample_input, sample_output, hint):
        self.owner_contest_id = owner_contest_id
        self.owner_road_id = owner_road_id
        self.title = title
        self.memory_limit = memory_limit
        self.time_limit = time_limit
        self.description = description
        self.input = input
        self.output = output
        self.sample_input = sample_input
        self.sample_output = sample_output
        self.hint = hint

        
        
class Contest(db.Model):
    """entity for contest"""
    __tablename__ = "contest"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    problems = db.Column(db.Text, default="")  # split with '|'
    private = db.Column(db.Boolean, nullable=False)  # if is true, only contestants can reach the contest, else every can
    contestants = db.Column(db.Text)  # user invited
    ranklist = db.Column(db.Text)

    def __init__(self, title="", description="", start_time=datetime.now(), end_time=datetime.now(), problems="", private=False, contestants="", ranklist=""):
        self.title = title
        self.description = description
        self.start_time = start_time
        self.end_time = end_time
        self.problems = problems
        self.private = private
        self.contestants = contestants
        self.ranklist = ranklist



class Submission(db.Model):
    """entity for submission"""
    __tablename__ = "submission"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('submissions', lazy='dynamic'))
    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'))
    problem = db.relationship('Problem', backref=db.backref('submissions', lazy='dynamic'), lazy='select')
    submit_time = db.Column(db.DateTime, nullable=False)
    compiler = db.Column(db.Text, nullable=False)
    result = db.Column(db.Text, nullable=False)
    memory_used = db.Column(db.Text)
    time_used = db.Column(db.Text)
    code = db.Column(db.Text,nullable=False)
    judger_status = db.Column(db.Integer, default=0)

    def get_id(self):
        return self.id
    
    def __init__(self, user, problem, submit_time, compiler, code, result, memory_used, time_used, judger_status):
        self.user = user
        self.problem = problem
        self.submit_time = submit_time
        self.compiler = compiler
        self.result = result
        self.memory_used = memory_used
        self.time_used = time_used
        self.code = code
        self.judger_status = judger_status


class Forum(db.Model):
    """docstring for Forum"""
    __tablename__ = "forum"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    content = db.Column(db.Text, nullable=False)
    publish_time = db.Column(db.DateTime, nullable=False)
    father_node = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('posts', lazy='dynamic'))
    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'))
    problem = db.relationship('Problem', backref=db.backref('posts', lazy='dynamic'), lazy='select')
    last_reply = db.Column(db.Text, default=None)
    last_update_time = db.Column(db.DateTime, nullable=False)

    def __init__(self, title, content, publish_time, father_node, user, problem):
        self.title = title
        self.content = content
        self.publish_time = publish_time
        self.father_node = father_node
        self.user = user
        self.problem = problem
        self.last_update_time = publish_time
        






