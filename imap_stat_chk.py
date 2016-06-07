# encoding:utf-8
import urllib,httplib,smtplib
import time
from datetime import date,datetime,timedelta
from setting import *

def sendmail(subject, content):

    try:
        svr = smtplib.SMTP(error_report_host)
        svr.set_debuglevel(False)
        svr.putcmd("HELO server")
        svr.putcmd('MAIL FROM: inotes_errorinfo')
        for (k,v) in error_rcpt.items():
            svr.putcmd('RCPT TO: ' + k)
        svr.putcmd("DATA")
        svr.putcmd("from: inotes_errorinfo")
        for (k, v) in error_rcpt.items():
            svr.putcmd("to: " + unicode(v.decode("utf-8")).encode("gbk"))
        svr.putcmd("subject: %s" % subject)
        svr.putcmd(content)
        svr.docmd(".")
        svr.getreply()
        svr.quit()
    except Exception,e:
        print "error report mail send failed on Host: %s" % error_report_host

def work():
    url = ''
    values = {'username':username,'password':password}
    data = urllib.urlencode(values)
    headers = {'Content-Type':'application/x-www-form-urlencoded','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}
    succ_count = 0
    fail_count = 0
    for host in hosts:
        try:
            httpclient = httplib.HTTPConnection(host,80,timeout=5)
            httpclient.request('POST','/names.nsf?Login',data,headers)
            reponse = httpclient.getresponse()
            status = reponse.status
            result = reponse.read()
            result = unicode(result.decode("utf-8"))
            if status == 200 and ('Invalid username or password was specified' in result or u'指定的用户名或密码无效' in result):  #send mail
                mail_subject = 'Login_error 200 on host IP: %s' % host
                mail_content = 'Invalid username or password was specified\nusername: %s\nhost:%s' % (username,host)
                sendmail(mail_subject,mail_content)
                print 'Host: %s inotes login failed with error 200: Invalid username or password was specified' % host
                fail_count += 1
            elif status == 302:
                print 'Host: %s inotes login successfully' % host
                succ_count += 1
            else:
                print "Host: %s inotes login failed with error %s" % (host,status)
                fail_count += 1
        except Exception,e:
            print 'Host: %s inotes login failed with error: %s' % (host,e)
            mail_subject = 'Othor error on host IP: %s' % host
            mail_content = '%s \nusername: %s\nhost:%s' % (e, username, host)
            sendmail(mail_subject, mail_content)
            fail_count += 1
        continue
    return [succ_count,fail_count]

def sleep_seconds(day,hour,mins,second):
    return second + mins*60 + hour*3600 + day*3600*24

def runTask(func,day=0,hour=0,min=0,second=0):
    period = timedelta(days=day,hours=hour,minutes=mins,seconds=second)
    sleep_secs = sleep_seconds(day,hour,mins,second)
    while True:
        iter_now = datetime.now()
        iter_now_time = iter_now.strftime('%Y-%m-%d %H:%M:%S')
        print "start work:%s" % iter_now_time
        cnt_list = work()
        print "task done"
        print "success count: %s" % cnt_list[0]
        print "failed count: %s" % cnt_list[1]
        now = datetime.now()
        iter_time = now + period
        strnext_time = iter_time.strftime('%Y-%m-%d %H:%M:%S')
        print "next_iter: %s" % strnext_time
        print '\n'
        time.sleep(sleep_secs)
        continue

runTask(work,day,hour,mins,second)