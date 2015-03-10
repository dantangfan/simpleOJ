
"""
status_url = "http://acm.hdu.edu.cn/status.php?user=" + "scpc1"
response = urllib2.urlopen(status_url)
text  = response.read()
match = re.compile(u'<input type=submit.*?<\/form>.*?height=22px>(.*?)<\/td><td>.*?<font.*?>(.*?)<\/font>.*?showproblem.*?<td>(.*?)<\/td><td>(.*?)<\/td>', re.M | re.S)
last_sub = match.findall(text)
print last_sub
"""
"""
from judger import guard
from judger.HDOJ import hdoj
a = guard.request_new_submission_by_databse()
print a.problem
hdoj.judge(a).start()
"""
from judger import guard
guard.start()
