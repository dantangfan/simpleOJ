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

class HDOJ(SCPC_Judger):
    """acm.hdoj.edu.cn"""
    oj_name = "HDOJ"
    hdoj_username = ""
    hdoj_password = ""
    hdoj_last_submission_id = None
    account = None
    submission = None
    stillRuning = True
    done = False

    def __init__(self, account):
        reload(sys)
        sys.setdefaultencoding('utf-8')
        SCPC_Judger.__init__(self)
        self.hdoj_username = account['username']
        self.hdoj_password = account['password']
        self.account = account

    def judge(self, submission):
        self.submission = submission
        return self

    def submit(self):
        login_url = "http://acm.hdu.edu.cn/userloginex.php?action=login";
        submit_url = "http://acm.hdu.edu.cn/submit.php?action=submit";
        try:
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
            postData = {'username' : self.hdoj_username, 'userpass' : self.hdoj_password, 'login' : 'Sign In'}   
            postData = urllib.urlencode(postData)  

            # Login
            request = urllib2.Request(login_url, postData, headers)  
            response = urllib2.urlopen(request) 

            # Compiler 
            compiler = '1'
            if self.submission.compiler == 'gcc': compiler = '1'
            if self.submission.compiler == 'g++': compiler = '0'
            if self.submission.compiler == 'java': compiler = '5'

            #Post数据 
            postData = {'problemid' : self.submission.original_oj_id, 'check' : '', 'language' : compiler, 'usercode' : self.submission.code}   
            postData = urllib.urlencode(postData)

            urllib2.urlopen(submit_url)  

            # Submit
            request = urllib2.Request(submit_url, postData, headers)  
            response = urllib2.urlopen(request)
            return True
        except Exception, e:
            print "Warning: HDOJ.submit()"
            print e
            return False
        

    def request_last_submission(self):
        last_sub = []
        while self.stillRuning:
            try:
                login_url = "http://acm.hdu.edu.cn/userloginex.php?action=login";
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
                postData = {'username' : self.hdoj_username, 'userpass' : self.hdoj_password, 'login' : 'Sign In'}   
                postData = urllib.urlencode(postData)  

                # Login
                request = urllib2.Request(login_url, postData, headers)  
                response = urllib2.urlopen(request) 
                
                status_url = "http://acm.hdu.edu.cn/status.php?user=" + self.hdoj_username
                request = urllib2.Request(status_url, None, headers)  
                response = urllib2.urlopen(request)
                text  = response.read()
                match = re.compile('<input type=submit.*?<\/form>.*?height=22px>(.*?)<\/td><td>.*?<font.*?>(.*?)<\/font>.*?showproblem.*?<td>(.*?)<\/td><td>(.*?)<\/td>', re.M | re.S)
                last_sub = match.findall(text)
            except Exception, e:
                print "Warning: HDOJ.request_last_submission()"
                print e
            if last_sub == None or last_sub == []:
                time.sleep(2)
                continue
            #print last_sub
            return last_sub
        
    def run(self):
        try:
            self.hdoj_last_submission_id = self.request_last_submission()[0][0]
            #print "[Task %s]: Last ID: %s" % (self.submission.id, self.hdoj_last_submission_id)
            if self.submit() == False:
                raise Exception("Error: Submit failed.")
            while self.stillRuning:
                current_sub = self.request_last_submission()
                if self.hdoj_last_submission_id == current_sub[0][0]:
                    time.sleep(2)
                    continue
                if self.stillRuning == False: raise Exception("thread has already been killed.")
                if current_sub[0][1] != 'Queuing' and current_sub[0][1] != 'Running' and current_sub[0][1] != 'Compiling':
                    session = db.create_scoped_session()
                    session.execute("UPDATE submission set result='%s', judger_status=-1, memory_used='%s', time_used='%s', original_oj_submit_id=%s WHERE id=%d" % (current_sub[0][1],current_sub[0][3],current_sub[0][2],current_sub[0][0],self.submission.id))
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
            print "Warning: HDOJ.run()"
            print "rollback"
            db.session.rollback()
            print e
        except Exception, e:
            print "Warning: HDOJ.run()"
            print e










