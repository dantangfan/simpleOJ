#!/usr/bin/env python
# coding=utf-8

from application import db
from application.models import User, News, Contest, Forum
from datetime import datetime
from hashlib import md5
from acmjudger.dbmanager import redis_q
from acmjudger.config import submission_queue_key
from acmjudger.makeProblem import make_problem
from acmjudger.dbmanager import db as updateDB


print 'Clearing old database...'
db.drop_all()

print 'create tables'
db.create_all()

print 'adding user'
users = []
for i in range(20):
    email = u'user%s@dantangfan.com' % str(i)
    email_hash = md5()
    email_hash.update(email)
    email_hash = email_hash.hexdigest()
    password = u'password' + str(i)
    password_hash = md5()
    password_hash.update(password)
    password_hash = password_hash.hexdigest()
    u = User(username=u'user' + str(i),
             password=password_hash,
             email="%s|%s" % (email, email_hash),
             hj_oj_username=None,
             last_login_time=datetime.now(),
             head_img=0,
             submit_count=0,
             acc_count=0)
    users.append(u)

for i in range(20):
    db.session.add(users[i])
password = u'123456'
password_hash = md5()
password_hash.update(password)
password_hash = password_hash.hexdigest()
dantangfan = User(username='admin',
                  password=password_hash,
                  email='dantangfan@gmail.com|1ff531004d5ac7d9127a7ba9170ec323',
                  hj_oj_username='HJ_oj_username',
                  last_login_time=datetime.now(),
                  head_img=1,
                  submit_count=0,
                  acc_count=0)
dantangfan.group = "admin|user|manage user|manage problem|manage contest|manage news|manage submission"
db.session.add(dantangfan)

print 'adding news'
news = []
for i in range(10):
    n = News(publish_time=datetime.now(), title="新闻标题新闻标题新闻 " + str(i), content="新闻内容!"*200)
    db.session.add(n)

print "adding problem"
make_problem()


print "adding Contests"
sql = "update problem set owner_contest_id=%s where id=%s"
p1 = Contest(u"contests" + str(1), u"description", datetime.now(), datetime.now(), "1|2|3", False, u"a|b|c|d|e")
updateDB.execute(sql, 1, 1)
updateDB.execute(sql, 1, 2)
updateDB.execute(sql, 1, 3)
db.session.add(p1)
p2 = Contest(u"contests" + str(2), u"description", datetime.now(), datetime.now(), "4|5|6", False, u"a|b|c|d|e")
updateDB.execute(sql, 2, 4)
updateDB.execute(sql, 2, 5)
updateDB.execute(sql, 2, 6)
db.session.add(p2)
p3 = Contest(u"contests" + str(3), u"description", datetime.now(), datetime.now(), "7|8|9|10", True, u"admin|user1")
updateDB.execute(sql, 3, 7)
updateDB.execute(sql, 3, 8)
updateDB.execute(sql, 3, 9)
updateDB.execute(sql, 3, 10)
db.session.add(p3)


print "adding forum.posts"
for i in range(20):
    po = Forum(title="title", content="content", publish_time=datetime.now(), father_node=0,
               user=dantangfan, problem=None)
    db.session.add(po)


print "commiting..."
db.session.commit()


print "adding submission into redis"
for i in range(1, 6):
    redis_q.lpush(submission_queue_key, i)


print "done"