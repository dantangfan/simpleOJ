#coding=utf-8
from application import db
from application.models import Submission
from judger.judger_base import SCPC_Judger
from sqlalchemy.exc import SQLAlchemyError
import judger
import HTMLParser  
import urlparse  
import urllib  
import urllib2  
import cookielib  
import string  
import re 
import time
import sys

class PKUOJ(SCPC_Judger):
    """poj.org"""
    oj_name = "PKUOJ"
    oj_username = ""
    oj_password = ""
    oj_last_submission_id = None
    account = None
    submission = None
    stillRuning = True
    done = False

    def __init__(self, account):
        reload(sys)
        sys.setdefaultencoding('utf-8')
        SCPC_Judger.__init__(self)
        self.oj_username = account['username']
        self.oj_password = account['password']
        self.account = account

    def judge(self, submission):
        self.submission = submission
        return self

    def submit(self):
        while True:
            login_url = "http://poj.org/login";
            submit_url = "http://poj.org/submit";
            try:
                #cookie处理器
                cookieJar = cookielib.LWPCookieJar()  
                cookie_support = urllib2.HTTPCookieProcessor(cookieJar)  
                opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)  
                urllib2.install_opener(opener)  

                #打开登录主页面
                urllib2.urlopen(login_url, timeout=5)  

                #header  
                headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:14.0) Gecko/20100101 Firefox/14.0.1', 'Referer' : '******'}  

                #Post数据 
                postData = {'user_id1' : self.oj_username, 'password1' : self.oj_password, 'B1' : 'login', 'url' : '.'}   
                postData = urllib.urlencode(postData)  

                # Login
                request = urllib2.Request(login_url, postData, headers)  
                response = urllib2.urlopen(request, timeout=5) 

                # Compiler 
                compiler = '1'
                if self.submission.compiler == 'gcc': compiler = '1'
                if self.submission.compiler == 'g++': compiler = '0'
                if self.submission.compiler == 'java': compiler = '2'

                #Post数据 
                postData = {'problem_id' : self.submission.original_oj_id, 'language' : compiler, 'source' : self.submission.code, 'submit':'Submit'}   
                postData = urllib.urlencode(postData)

                #urllib2.urlopen(submit_url)  

                # Submit
                request = urllib2.Request(submit_url, postData, headers)  
                response = urllib2.urlopen(request, timeout=5)
                #print response.read()
                return True
            except Exception, e:
                print "Warning: PKUOJ.submit()"
                print e
                continue
        

    def request_last_submission(self):
        last_sub = []
        while self.stillRuning:
            try:
                login_url = "http://poj.org/login";
                """
                #cookie处理器
                cookieJar = cookielib.LWPCookieJar()  
                cookie_support = urllib2.HTTPCookieProcessor(cookieJar)  
                opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)  
                urllib2.install_opener(opener)  

                #打开登录主页面
                urllib2.urlopen(login_url)  

                #header  
                headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:14.0) Gecko/20100101 Firefox/14.0.1', 'Referer' : '******'}  

                #Post数据 
                postData = {'user_id1' : self.oj_username, 'password1' : self.oj_password, 'B1' : 'login', 'url' : '.'}   
                postData = urllib.urlencode(postData)  

                # Login
                request = urllib2.Request(login_url, postData, headers)  
                response = urllib2.urlopen(request) 
                """
                
                headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:14.0) Gecko/20100101 Firefox/14.0.1', 'Referer' : '******'}  
                status_url = "http://poj.org/status?user_id=" + self.oj_username
                request = urllib2.Request(status_url, None, headers)  
                response = urllib2.urlopen(request, timeout=5)
                text  = response.read()
                match = re.compile('<tr align=center><td>(.*?)<\/td><td>.*?<font.*?>(.*?)<\/font>.*?<td>(.*?)<\/td.*?td>(.*?)<\/td>', re.M | re.S)
                last_sub = match.findall(text)
                #print "               ", last_sub[0]
            except Exception, e:
                print "Warning: PKUOJ.request_last_submission()"
                print e
            if last_sub == None or last_sub == []:
                time.sleep(1)
                continue
            #print last_sub
            return last_sub
        
    def run(self):
        try:
            self.oj_last_submission_id = self.request_last_submission()[0][0]
            #print "[Task %s]: Last ID: %s" % (self.submission.id, self.oj_last_submission_id)
            if self.submit() == False:
                raise Exception("Error: Submit failed.")
            while self.stillRuning:
                current_sub = self.request_last_submission()
                if self.oj_last_submission_id == current_sub[0][0]:
                    time.sleep(2)
                    continue
                if self.stillRuning == False: raise Exception("thread has already been killed.")
                if current_sub[0][1] != 'Compiling' and current_sub[0][1] != 'Running & Judging' and current_sub[0][1] != 'Waiting':
                    session = db.create_scoped_session()
                    session.execute("UPDATE submission set result='%s', judger_status=-1, memory_used='%s', time_used='%s', original_oj_submit_id=%s WHERE id=%d" % (current_sub[0][1],('0K' if current_sub[0][2] == '' else current_sub[0][2]),('0S' if current_sub[0][3] == '' else current_sub[0][3]),current_sub[0][0],self.submission.id))
                    session.flush()
                    session.commit()
                    self.done = True
                    break
                session = db.create_scoped_session()
                session.execute("UPDATE submission set result='%s' WHERE id=%d" % (current_sub[0][1],self.submission.id))
                session.flush()
                if self.stillRuning == False: raise Exception("thread has already been killed.")
                session.commit()
        except SQLAlchemyError, e:
            print "Warning: PKUOJ.run()"
            print "rollback"
            db.session.rollback()
            print e
        except Exception, e:
            print "Warning: PKUOJ.run()"
            print e










