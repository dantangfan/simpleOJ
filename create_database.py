#coding=utf-8

from application import db
from application.models import User, News, Problem, Submission, Contest, Forum
from datetime import datetime
from hashlib import md5
from acmjudger.dbmanager import redis_q
from acmjudger.config import submission_queue_key


print 'Clearing old database...'
db.drop_all()

print 'create tables'
db.create_all()

print 'adding user'
users = []
for i in range(20):
    email = u'admin%s@dantangfan.com' % str(i)
    email_hash = md5()
    email_hash.update(email)
    email_hash = email_hash.hexdigest()
    password = u'password' + str(i)
    password_hash = md5()
    password_hash.update(password)
    password_hash = password_hash.hexdigest()
    u = User(u'user' + str(i),password_hash,"%s|%s"%(email,email_hash),None, datetime.now())
    users.append(u)

for i in range(20):
    db.session.add(users[i])
password = u'123456'
password_hash = md5()
password_hash.update(password)
password_hash = password_hash.hexdigest()
chenyi = User('admin', password_hash, 'chen_swust@foxmail.com|1ff531004d5ac7d9127a7ba9170ec323', 'scpc_oj_username', datetime.now())
chenyi.group = "admin|user|manage user|manage problem|manage contest|manage news"
db.session.add(chenyi)

print 'adding news'
news = []
for i in range(10):
    n = News(datetime.now(), u"新闻标题新闻标题新闻 " + str(i), u"新闻内容!新闻内容!新闻内容!新闻内容!新闻内容!新闻内容!新闻内容!新闻内容!新闻内容!新闻内容!新闻内容!新闻内容!新闻内容!新闻内容!新闻内容!新闻内容!新闻内容!新闻内容!新闻内容!新闻内容!新闻内容!新闻内容!新闻内容!新闻内容!新闻内容!新闻内容!新闻内容!新闻内容!新闻内容!新闻内容!新闻内容!新闻内容!新闻内容!新闻内容!新闻内容!")
    db.session.add(n)



print "adding problems"
p = None
for i in range(1):
    p = Problem(None, None, u"PKUOJ", u"1000", u"A + B Problem " + str(i), u"128k", u"1s", u"description", u"input", u"output", u"sample_input", u"sample_output", u"hint")
    db.session.add(p)

print "adding Contests"
p1 = None
for i in range(11):
    p1 = Contest(u"contests" + str(i), u"1000", datetime.now(), datetime.now(),"1|2|3",False, u"a|b|c|d|e", u"description")
    db.session.add(p1)


print "adding submission"
for i in range(5):
    s = Submission(users[5], p, datetime.now(), 'g++', '#include<stdio.h>\nint main(){\nint a,b;\nwhile(scanf(\"%d%d\",&a,&b)!=EOF){\nprintf(\"%d\\n\",a+b);\n}\n}\n', 'pending', None, None, 0, p.original_oj,p.original_oj_id)
    db.session.add(s)


print "adding forum.posts"
for i in range(20):
    po = Forum("title", "content", datetime.now(), 0, chenyi, None)
    db.session.add(po)

print "commiting..."
db.session.commit()

for i in range(1,6):
    redis_q.lpush(submission_queue_key, i)



