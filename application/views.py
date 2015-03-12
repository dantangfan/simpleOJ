#coding=utf-8
from flask import g, render_template, redirect, url_for, request
from application import app,lm, cache, db
from application.forms import form_user_login
from application.models import User, News, Problem, Contest, Submission, Forum
from flask_login import login_user, logout_user, current_user, login_required
import json
import collections
import math
from datetime import datetime
from hashlib import md5
import clean_xss
from acmjudger.dbmanager import redis_q
from acmjudger.config import submission_queue_key

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user


@app.route('/user/<action>', methods=['GET', 'POST'])
def login(action):
    if action == "login_status":
        if g.user is not None and g.user.is_authenticated():
            return json.dumps({"login_status" : True, "username" : g.user.username, "email_hash" : g.user.email.split('|')[1], "admin":g.user.is_admin()})
        else:
            return json.dumps({"login_status" : False})
    elif action == "login_form":
        form = form_user_login()
        return render_template('form_login.html', form = form)
    elif action == "login":
        try:
            form = form_user_login()
            if form.validate_on_submit():
                form.username.data = form.username.data.lower()
                form.password.data = form.password.data.lower()
                password = form.password.data
                password_hash = md5()
                password_hash.update(password)
                password_hash = password_hash.hexdigest()
                u = User.query.filter_by(username=form.username.data, password=password_hash).first()
                if u is not None:
                    login_user(u)
                    return json.dumps({"result" : "ok", "username" : g.user.username})
        except Exception, e:
            raise e
            db.session.rollback()
        return json.dumps({"result" : "failed"})
        
    elif action == "logout":
        if g.user is not None and g.user.is_authenticated():
            logout_user()
            return json.dumps({"result" : "ok"})
        return json.dumps({"result" : "failed"})

    return redirect(url_for('index'))

@app.route('/news/<action>/<int:id>/')
@cache.cached(timeout=5)
def news(action, id):
    if action == "get":
        if type(id) is int:
            data = News.query.filter_by(id=id).first()
            return json.dumps(dict(
                id=data.id, 
                title=data.title, 
                content=data.content, 
                publish_time=str(data.publish_time))
            )

    return redirect(url_for('index'))

@app.route('/submit', methods=['POST'])
@login_required
def submit():
    if request.method == 'POST':
        try:
            if len(request.form['code']) < 50:
                raise Exception("Code is too short. 50+ required.")
            if request.form['compiler'] != 'gcc' and request.form['compiler'] != 'g++' and request.form['compiler'] != 'java':
                raise Exception("Please select compiler.")
            user = g.user
            problem = int(request.form['problem_id'])
            problem = Problem.query.get(problem)
            if problem is None:
                raise Exception("Problem not found.")
            if 0 != int(request.form['contest']):
                cont = Contest.query.get(int(request.form['contest']))
                if cont is None: raise Exception("Contest not found.")
                if problem.owner_contest_id != cont.id:
                    raise Exception("Problem does not belong to the contest.")
                if datetime.now() < cont.start_time: raise Exception("Contest has not begun.")
                if datetime.now() > cont.end_time: raise Exception("Contest had ended.")
                if cont.start_time < datetime.now() < cont.end_time:
                    if cont.private == True:
                        contestants = []
                        if cont.contestants is not None and cont.contestants != "":
                            contestants = map(int, cont.contestants.split('|'))
                        if g.user.id not in contestants:
                            raise Exception("This contest is private and you have not been invited.")
            if problem.owner_contest_id != None and 0 == request.form['contest']:
                raise Exception("This problem belongs to a contest. Please submit in the contest page.")    
            smt = Submission(user, problem, datetime.now(), request.form['compiler'], request.form['code'], 'pending', "0K", "0MS", 0, problem.original_oj, problem.original_oj_id)
            db.session.add(smt)
            db.session.commit()
            redis_q.lpush(submission_queue_key, smt.get_id())
            return json.dumps({"result": "ok"})
        except Exception, e:
            return json.dumps({"result": str(e)})
    return json.dumps({"result": "Only support POST request."})


@app.route('/problems/')
@cache.cached(timeout=5)
def problems_no_page():
    return problems(0)

@app.route('/problems/<int:page>/')
@cache.cached(timeout=5)
def problems(page):
    if type(page) == int:
        page = 0 if page<1 else page-1
        data = Problem.query.filter(Problem.owner_contest_id == None).limit(10).offset(page*10).all()
        objects_list = []
        for row in data:
            d = collections.OrderedDict()
            d['id'] = row.id
            d['title'] = row.title
            d['memory_limit'] = row.memory_limit
            d['time_limit'] = row.time_limit
            d['description'] = row.description
            d['input'] = row.input
            d['output'] = row.output
            d['sample_input'] = row.sample_input
            d['sample_output'] = row.sample_output
            d['hint'] = row.hint
            objects_list.append(d)
        return render_template('problems.html', 
            problems = objects_list,
            total_page = int(math.ceil(Problem.query.filter(Problem.owner_contest_id == None).count()/10.0)),
            current_page = page + 1,
            site_name = app.config['SCPC_TS_SITE_NAME']
            )

    return redirect(url_for('index'))

@app.route('/problem/<int:id>/')
@cache.cached(timeout=5)
def problem(id):
    if type(id) == int:
        try:
            id = 1 if id < 1 else id
            p = Problem.query.get(id)
            if p is None: raise Exception("problem not found.")
            if p.owner_contest_id is not None: 
                raise Exception("The problem belongs to a contest. View it in the contest problem page.!")
            return render_template('problem.html',
                site_name = app.config['SCPC_TS_SITE_NAME'],
                problem = p
                )
        except Exception, e:
            return render_template('exception.html', message = str(e))
        


@app.route('/submissions/', defaults={'page': 1})
@app.route('/submissions/<int:page>/')
@cache.cached(timeout=3)
def submissions_1(page):
    return submissions(page, 'None', 0, 'None')

@app.route('/submissions/<string:user>:<int:problem>:<string:result>/<int:page>/')
@cache.cached(timeout=3)
def submissions(page=1, user="None", problem=0, result="None"):
    if type(page) == int:
        try:
            page = 0 if page<1 else page-1
            sql=""
            if(user!="None"):
                user1 = User.query.filter(User.username==user).first()
                user2 = User.query.filter(User.scpc_oj_username==user).first()
                if user1 is None and user2 is None: raise Exception("User not found.")
                if user1 is not None: 
                    user=user1
                else: 
                    user=user2
                sql = "user_id=%d" % user.id
            if(problem!=0):
                problem = Problem.query.get(problem)
                if problem is None: raise Exception("Problem not found.")
                if sql != "": sql = sql + " and "
                sql = sql + "problem_id=%d" % problem.id
            if(result!="None"):
                if sql != "": sql = sql + " and "
                if result == "Accepted" or result == "Wrong Answer":
                    sql = sql + "result = '%s'" % result
                elif result == "Others":
                    sql = sql + "result != 'Accepted' and result != 'Wrong Answer'"
                else:
                    raise Exception("Result filter error.")
            if sql != "": sql = "WHERE " + sql
            data = Submission.query.from_statement("SELECT * FROM submission %s ORDER BY id desc LIMIT %d,%d" % (sql,page*10,10) ).all()
            objects_list = []
            for row in data:
                d = collections.OrderedDict()
                d['id'] = row.id
                d['problem_title'] = row.problem_id
                d['username'] = row.user.username
                d['result'] = row.result
                d['memory_used'] = row.memory_used
                d['time_used'] = row.time_used
                d['compiler'] = row.compiler
                d['code'] = len(row.code)
                d['submit_time'] = row.submit_time
                objects_list.append(d)
            total = int(db.session.execute("SELECT COUNT(*) FROM submission %s"%sql).first()[0])
            return render_template('submissions.html', 
                submissions = objects_list,
                total_page = int(math.ceil(total/10.0)),
                current_page = page + 1,
                site_name = app.config['SCPC_TS_SITE_NAME']
                )
        except Exception, e:
            return render_template('exception.html', message=str(e))
        

@app.route('/road/')
def road():
    return render_template('road.html', site_name = app.config['SCPC_TS_SITE_NAME'])

@app.route('/forum/', defaults={'page': 1})
@app.route('/forum/<int:page>')
@cache.cached(timeout=3)
def forum(page):
    if type(page) == int:
        page = 0 if page<1 else page-1
        data = Forum.query.filter(Forum.father_node==0,Forum.problem==None).order_by(db.desc(Forum.id)).offset(page*10).limit(10).all()
        objects_list = []
        for row in data:
            d = collections.OrderedDict()
            d['id'] = row.id
            d['title'] = row.title
            d['content'] = row.content
            d['last_update_time'] = row.last_update_time
            d['user'] = row.user.username
            d['user_email_hash'] = row.user.email.split('|')[1]
            d['last_reply'] = row.last_reply
            objects_list.append(d)
        total_page = int(math.ceil(Forum.query.filter(Forum.father_node==0,Forum.problem==None).count()/10.0))
        if total_page == 0: total_page = 1
        return render_template('forum.html', 
            posts = objects_list,
            total_page = total_page,
            current_page = page + 1,
            site_name = app.config['SCPC_TS_SITE_NAME']
            )
    return redirect(url_for('index'))

@app.route('/forum/post/<int:id>/', defaults={'page': 1})
@app.route('/forum/post/<int:id>/<int:page>')
@cache.cached(timeout=5)
def post(id, page):
    if type(page) == int:
        page = 0 if page<1 else page-1
        if type(id) == int:
            id = 1 if id < 1 else id
            p = Forum.query.get(id)
            replys = Forum.query.filter(Forum.father_node == p.id).offset(page*10).limit(10).all()
            total_page = int(math.ceil(Forum.query.filter(Forum.father_node == p.id).count()/10.0))
            if total_page == 0: total_page = 1
            return render_template('post.html',
                site_name = app.config['SCPC_TS_SITE_NAME'],
                post = p,
                replys = replys,
                total_page = total_page,
                current_page = page + 1,
                email_hash = p.user.email.split("|")[1]
                )


@app.route('/forum/submit', methods=['POST'])
@login_required
def forum_submit():
    if request.method == 'POST':
        try:
            if len(request.form['content']) < 3:
                raise Exception("Content is too short. 3+ required.")
            father_node = int(request.form['father_node'])
            title = None
            if father_node == 0:
                title = request.form['title']
                if len(title) < 3: raise Exception("Title is too short. 3+ required.")
            user = g.user
            time_now = datetime.now()
            content = clean_xss.parsehtml(request.form['content'])
            pst = Forum(title, content, time_now, father_node, user, None)
            db.session.add(pst)
            if father_node != 0:
                father = Forum.query.get(father_node)
                father.last_update_time = time_now
                father.last_reply = user.username
            db.session.commit()
            return json.dumps({"result": "ok"})
        except Exception, e:
            return json.dumps({"result": str(e)})
    return json.dumps({"result": "Only support POST request."})



@app.route('/contests/')
@app.route('/contests/<int:page>/')
@cache.cached(timeout=3)
def contests(page=0):
    if type(page)==int:
        page=0 if page<1 else page-1
        data=Contest.query.order_by(db.desc(Contest.id)).limit(10).offset(page*10).all()
        objects_list=[]
        for row in data:
            d=collections.OrderedDict()
            d['id']=row.id
            d['title']=row.title
            d['description']=row.description
            d['start_time']=row.start_time
            d['end_time']=row.end_time
            d['problems']=row.problems
            d['private']=row.private
            d['contestants']=row.contestants
            d['ranklist']=row.ranklist
            objects_list.append(d)
        return render_template("contests.html",
            contests=objects_list,
            total_page = int(math.ceil(Contest.query.count()/10.0)),
            current_page = page + 1,
            ctime=datetime.now(),
            site_name = app.config['SCPC_TS_SITE_NAME']
        )
        
    return redirect(url_for('index'))


@app.route('/contest/')
@app.route('/contest/<int:cid>/')
def contest(cid=1):
    if type(cid)==int:
        try:
            cont=Contest.query.get(cid)
            if cont is None: raise Exception("Contest not found.")
            if cont.start_time > datetime.now(): raise Exception("Contest has not begun.")
            if cont.private == True:
                contestants = []
                if cont.contestants is not None and cont.contestants != "":
                    contestants = map(int, cont.contestants.split('|'))
                if g.user.is_anonymous() == True:
                    raise Exception("This contest is private. Please login first.")
                
                if g.user.id not in contestants:
                    raise Exception("This contest is private and you have not been invited.")
            problem_list=[]
            if cont.problems is not None and cont.problems != "":
                problem_list=map(int,cont.problems.split('|'))
            idlist=[]
            number_list=range(0,len(problem_list))
            for item in number_list:
                idlist.append(chr(ord('A') + item))
            problems=[]
            solved=[]
            for item in problem_list:
                problems.append(Problem.query.get(item))
                user_id = -1 if g.user.is_anonymous() else g.user.id
                if int(db.session.execute("SELECT COUNT(*) FROM submission WHERE problem_id = %d and user_id=%d and result='Accepted'"%(item, user_id)).first()[0]) > 0:
                    solved.append(True)
                else:
                    solved.append(False)
            totaltime=math.ceil((cont.end_time-cont.start_time).total_seconds()/60)
            havetime=math.ceil((cont.end_time-datetime.now()).total_seconds()/60)
            if havetime<0:havetime=0
            elif havetime>totaltime:havetime=totaltime
            return render_template("contest.html",
                 title=cont.title,
                 start_time=cont.start_time,
                 end_time=cont.end_time,
                 description=cont.description,
                 problems=problems,             #待优化
                 idlist=idlist,
                 number_list=number_list,
                 totaltime=totaltime,
                 havetime=havetime,
                 solved=solved,
                 site_name = app.config['SCPC_TS_SITE_NAME']
                 )
        except Exception, e:
            return render_template('exception.html', message = str(e))
        



@app.route('/contest/<int:id>/submissions/', defaults={'page': 1})
@app.route('/contest/<int:id>/submissions/<int:page>')
@cache.cached(timeout=3)
def contest_submission(id, page):
    if type(page) == int:
        try:
            page = 0 if page<1 else page-1
            cont = Contest.query.get(id)
            if cont is None: raise Exception("contest not found.")
            if cont.private == True:
                contestants = []
                if cont.contestants is not None and cont.contestants != "":
                    contestants = map(int, cont.contestants.split('|'))
                if g.user.is_anonymous() == True:
                    raise Exception("This contest is private. Please login first.")
                if g.user.id not in contestants:
                    raise Exception("This contest is private and you have not been invited.")
            problems=[]
            if cont.problems is not None and cont.problems != "":
                problems=map(int,cont.problems.split('|'))
            sql = ""
            for x in problems:
                if sql != "": sql = sql + " or "
                sql = sql + "problem_id=%d" % x
            if sql == "": raise Exception("no problems.")
            data = Submission.query.from_statement("SELECT * FROM submission WHERE (%s) and submit_time >= '%s' and submit_time <= '%s' order by id desc limit %d,%d" % (sql, cont.start_time, cont.end_time, page*10, 10)).all()
            objects_list = []
            if data != []:
                for row in data:
                    d = collections.OrderedDict()
                    d['id'] = row.id
                    d['problem_title'] = "<a href='/contest/%d/problem/%s'>%s</a>" %(cont.id, chr(ord('A') + problems.index(row.problem_id)), chr(ord('A') + problems.index(row.problem_id)))
                    d['username'] = row.user.username
                    d['result'] = row.result
                    d['memory_used'] = row.memory_used
                    d['time_used'] = row.time_used
                    d['compiler'] = row.compiler
                    d['code'] = len(row.code)
                    d['submit_time'] = row.submit_time
                    objects_list.append(d)
            total_page = int(db.session.execute("SELECT COUNT(*) FROM submission WHERE %s" % sql).first()[0])
            total_page = int(math.ceil(total_page/10.0))
            if total_page <= 0: total_page = 1
            return render_template('contest_submission.html', 
                contest = cont,
                submissions = objects_list,
                total_page = total_page,
                current_page = page + 1,
                site_name = app.config['SCPC_TS_SITE_NAME']
                )
        except Exception, e:
            return render_template('exception.html', message = str(e))

@app.route('/contest/<int:cid>/problem/<pid>/')
@cache.cached(timeout=3)
def contest_problem(cid, pid):
    try:
        cont = Contest.query.get(cid)
        if cont is None: raise Exception("contest not found.")
        if cont.private == True:
            contestants = []
            if cont.contestants is not None and cont.contestants != "":
                contestants = map(int, cont.contestants.split('|'))
            if g.user.is_anonymous() == True:
                raise Exception("This contest is private. Please login first.")
            if g.user.id not in contestants:
                raise Exception("This contest is private and you have not been invited.")
        problems=[]
        if cont.problems is not None and cont.problems != "":
            problems=map(int,cont.problems.split('|'))
        if len(pid) == 1: 
            pid = ord(pid) - ord('A')
            if not 0<=pid<len(problems): raise Exception("problem not found.")
            pid = problems[pid]
        else:
            pid = int(x)
            if not pid in problems: raise Exception("problem not found..")
        problem = Problem.query.get(pid)
        if problem is None: raise Exception("problem not found...")
        return render_template('contest_problem.html', 
            contest = cont,
            problem = problem,
            site_name = app.config['SCPC_TS_SITE_NAME']
            )
    except Exception, e:
        return render_template('exception.html', message = str(e))

@app.route('/contest/<int:cid>/ranklist/')
@cache.cached(timeout=15)
def contest_ranklist(cid):
    try:
        cont = Contest.query.get(cid)
        if cont is None: raise Exception("contest not found.")
        if cont.private == True:
            contestants = []
            if cont.contestants is not None and cont.contestants != "":
                contestants = map(int, cont.contestants.split('|'))
            if g.user.is_anonymous() == True:
                raise Exception("This contest is private. Please login first.")
            if g.user.id not in contestants:
                raise Exception("This contest is private and you have not been invited.")
        problems=[]
        if cont.problems is not None and cont.problems != "":
            problems=map(int,cont.problems.split('|'))
        sql = ""
        for x in problems:
            if sql != "": sql = sql + " or "
            sql = sql + "problem_id=%d" % x
        if sql == "": raise Exception("no problems.")
        data = Submission.query.from_statement("SELECT * FROM submission WHERE (%s) and submit_time >= '%s' and submit_time <= '%s' order by id" % (sql, cont.start_time, cont.end_time)).all()
        objects_list = {}
        if data != []:
            for row in data:
                if int(row.problem_id) not in problems:
                    continue
                if objects_list.get(row.user_id) is None:
                    d = collections.OrderedDict()
                    d['username'] = row.user.username
                    d['problems'] = collections.OrderedDict()
                    d['accepted'] = 0
                    for p in problems:
                        d['problems'][p] = {"accepted": False, "attempt":0, "accepted_time": 0}
                    objects_list[row.user_id] = d
                else:
                    d = objects_list.get(row.user_id)

                if d['problems'][row.problem_id]['accepted'] == True:
                    continue
                if row.result == "Accepted":
                    d['problems'][row.problem_id]['accepted'] = True
                    d['problems'][row.problem_id]['accepted_time'] = (row.submit_time-cont.start_time).total_seconds()
                    continue
                else:
                    d['problems'][row.problem_id]['attempt'] = 1 + d['problems'][row.problem_id]['attempt']
                    continue
            for x in objects_list.values():
                penalty = 0
                for p in x['problems'].values():
                    if p['accepted'] == True:
                        penalty = penalty + (60 * 20 * p['attempt']) + p['accepted_time']
                        p['accepted_time'] = "%.2d:%.2d:%.2d"%(p['accepted_time']/3600, (p['accepted_time']%3600)/60, p['accepted_time']%60)
                        x['accepted'] = x['accepted'] + 1
                x['penalty'] = "%.2d:%.2d:%.2d"%(penalty/3600, (penalty%3600)/60, penalty%60)

            objects_list = sorted(objects_list.values(), cmp=lambda x,y: cmp(x['accepted'],y['accepted']) if cmp(x['accepted'],y['accepted'])!=0 else cmp(y['penalty'],x['penalty']),reverse=True)
            tmp = objects_list[0]
            rank = 1
            for x in objects_list:
                if not (x['accepted'] == tmp['accepted'] and x['penalty'] == tmp['penalty']):
                    rank = rank + 1
                x['rank'] = rank
        return render_template('contest_ranklist.html', 
            contest = cont,
            problems = problems,
            contestants = objects_list,
            site_name = app.config['SCPC_TS_SITE_NAME']
            )
    except Exception, e:
        return render_template('exception.html', message = str(e))

@app.route('/code/<int:id>/')
@login_required
@cache.cached(timeout=5)
def showcode(id):
    if type(id) == int:
        try:
            id = 1 if id < 1 else id
            p = Submission.query.get(id)
            if p is None: raise Exception('Code not found.')
            if g.user.is_admin() == False:
                if p.user_id != g.user.id: raise Exception('You are not the author of the code.')
            return render_template('code.html',
                site_name = app.config['SCPC_TS_SITE_NAME'],
                submission = p
                )
        except Exception, e:
            return render_template('exception.html', message = str(e))

@app.route('/contest/<int:cid>/code/<int:sid>/')
@login_required
@cache.cached(timeout=5)
def showcode_contest(cid, sid):
    try:
        sid = 1 if sid < 1 else sid
        cid = 1 if cid < 1 else cid
        cont = Contest.query.get(cid)
        if cont is None: raise Exception("Contest not found.")
        p = Submission.query.get(sid)
        if p is None: raise Exception('Code not found.')
        if g.user.is_admin() == False:
            if p.user_id != g.user.id: raise Exception('You are not the author of the code.')
        return render_template('contest_code.html',
            site_name = app.config['SCPC_TS_SITE_NAME'],
            submission = p,
            contest = cont
            )
    except Exception, e:
        return render_template('exception.html', message = str(e))
@app.route('/orca.txt')
def orca():
    return "3cf2d9137c049a63"
   
@app.route('/')
@app.route('/index')
@cache.cached(timeout=5)
def index():
    news_list = News.query.order_by(db.desc(News.id)).limit(8).all()
    lenx=6
    data = Submission.query.order_by(db.desc(Submission.id)).offset(0).limit(lenx).all()
    status = []
    for row in data:
		d = collections.OrderedDict()
		d['id'] = row.id
		d['problem_id']=row.problem.id
		d['problem_title'] = row.problem.title
		d['username'] = row.user.username
		d['result'] = row.result
		d['memory_used'] = row.memory_used
		d['time_used'] = row.time_used
		d['compiler'] = row.compiler
		d['code'] = len(row.code)
		d['submit_time'] = row.submit_time
		status.append(d)
    return render_template("index.html", 
        news_list = news_list,
        site_name = app.config['SCPC_TS_SITE_NAME'],
        status=status
        )





