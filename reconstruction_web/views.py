# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from django.http import StreamingHttpResponse

from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.utils import parseaddr, formataddr
import smtplib 

import os
import thread
import time
import Queue
import socket
import json
import numpy as np
import processSaxs as ps
#from sastbx.zernike_model import model_interface
#import zalign


# Create your views here.
q = Queue.Queue(0)
tag=True

def is_number(s):
    try:
        float(s)  # for int, long and float
    except ValueError:
        return False
    return True

def index(request):
    pass
    return render(request, "index.html")

def history(request):
    pass
    return render(request, "history.html")

def samples_withRmax(request):
    pass
    return render(request, "samples_withRmax.html")

def samples_withoutRmax(request):
    pass
    return render(request, "samples_withoutRmax.html")

def checkhistory(request):
    if request.method == "GET":
        joblogf=open('joblog.txt','r')
        joblogs=joblogf.readlines()
        check_path = "./reconstruction_web/media/result/"
        returnData = {"rows": []}
        check_files = os.listdir(check_path)
        check_files.sort(reverse=True)
        for check_file in check_files:
            status = 'running'
            downloadlink=''
            job_name=''
            if '.' not in check_file:
                date_time = time.localtime(float(check_file))
                date_time = time.strftime('%Y-%m-%d', date_time)
                dirs = os.listdir(check_path+check_file)

                for dir in dirs:
                    if '.tar.gz' in dir:
                        status = 'finished'
                        downloadlink = dir
                        break
                for joblog in joblogs:
                    if joblog.strip().split(',')[0]==check_file:
                        job_name=joblog.strip().split(',')[1]
                        break
                returnData['rows'].append({
                    "job_name": job_name,
                    "status": status,
                    "downloadlink": downloadlink,
                    "date_time": date_time
                })
    return HttpResponse(json.dumps(returnData))

def showsamples(request):
    if request.method == "GET":
        sampletype = request.GET["sampletype"]
        if sampletype=='withRmax':
            checkpath = './reconstruction_web/media/samples_withrmax'
            returnData = {"rows": []}
            samplenames = os.listdir(checkpath)
            samplenames.sort()
            ccfile = open('./reconstruction_web/media/samples_withrmax/CC.txt','r')
            ccdata = ccfile.readlines()
            ccdict = {}
            for line in ccdata:
                temp = line.strip().split(' ')
                ccdict[str(temp[0])] = float(temp[1])
            for samplename in samplenames:
                if 'SAS' in samplename:
                    returnData['rows'].append({
                        "samplename": str(samplename),
                        "cc": ccdict[str(samplename)]
                    })
        elif sampletype=='withoutRmax':
            checkpath = './reconstruction_web/media/samples_withoutrmax'
            returnData = {"rows": []}
            samplenames = os.listdir(checkpath)
            samplenames.sort()
            ccfile = open('./reconstruction_web/media/samples_withoutrmax/CC.txt','r')
            ccdata = ccfile.readlines()
            ccdict = {}
            for line in ccdata:
                temp = line.strip().split(' ')
                ccdict[str(temp[0])] = float(temp[1])
            rmaxfile = open('./reconstruction_web/media/samples_withoutrmax/RMAX.txt', 'r')
            rmaxdata = rmaxfile.readlines()
            rmaxdict = {}
            for line in rmaxdata:
                temp = line.strip().split(' ')
                rmaxdict[str(temp[0])] = [float(temp[2]),float(temp[4])]
            for samplename in samplenames:
                if 'SAS' in samplename:
                    returnData['rows'].append({
                        "samplename": str(samplename),
                        "cc": ccdict[str(samplename)],
                        "findrmax": int(rmaxdict[str(samplename)][0]),
                        "realrmax": int(rmaxdict[str(samplename)][1]),
                    })

    return HttpResponse(json.dumps(returnData))

def readFile(filename, chunk_size=512):
    with open(filename, 'rb') as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break


def download_file(request):
    download_name = request.GET["file"]
    download_path = request.GET["filepath"]
    #the_file_name = str(download_name).split(".")
    filename = os.path.join('./reconstruction_web/media/result/'+str(download_path)+'/'+str(download_name))
    response = StreamingHttpResponse(readFile(filename))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(str(download_name))
    return response

def submit(request):
    pass
    return render(request, "submit.html")
def totorial(request):
    pass
    return render(request, "tutorial.html")
def check(request):
    pass
    return render(request, "checkResults.html")

def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))

    try:
        #print "Send: {}".format(message)
        sock.sendall(message)

        #response = sock.recv(1024)
        #jresp = json.loads(response)
        #print "Recv: ",jresp
    finally:
        sock.close()

'''
def generatedata(request,cur_time):
    if request.method == "POST":
        cur_time = str(cur_time)
        file_obj = request.FILES["up_file"]
        job_name = request.POST.get('job_name')
        estimate_rmax=request.POST.get('estimate_rmax')
        send_email=request.POST.get('send_email')
        job_log=open('joblog.txt','a')
        print >> job_log, cur_time+','+job_name+','+send_email
        job_log.close()
        os.mkdir("./reconstruction_web/media/result/" + cur_time)
        file_path = "./reconstruction_web/media/result/" + cur_time + '/' + 'upload_saxs.'+file_obj.name.split('.')[-1]
        with open(file_path, "wb") as f1:
            for i in file_obj.chunks():
                f1.write(i)
        f1.close()
        process_result = ps.process(file_path)
        if len(process_result)==2:
            estimate_rmax=str(process_result[1])
        saxs_data = process_result[0]
        #saxs_data = np.loadtxt(file_path)
        saxs_data = list(saxs_data.astype(float).reshape(-1))
        saxs_data = str(saxs_data)
        sendmessage = [{'saxs_data': saxs_data, 'job_file': cur_time, 'estimate_rmax': estimate_rmax, 'send_email': send_email, 'job_name': job_name}]
        jsendmessage = json.dumps(sendmessage)


        HOST, PORT = "10.0.0.20", 50001
        #print "Send: {}".format(jsendmessage)
        client(HOST, PORT, jsendmessage)
'''
def generatedata(request,cur_time):
    if request.method == "POST":
        cur_time = str(cur_time)
        file_obj = request.FILES["up_file"]
        job_name = request.POST.get('job_name')
        estimate_rmax=request.POST.get('estimate_rmax')
        send_email=request.POST.get('send_email')
        job_log=open('joblog.txt','a')
        print >> job_log, cur_time+','+job_name+','+send_email
        job_log.close()
        os.mkdir("./reconstruction_web/media/result/" + cur_time)
        file_path = "./reconstruction_web/media/result/" + cur_time + '/' + 'upload_saxs.'+file_obj.name.split('.')[-1]
        with open(file_path, "wb") as f1:
            for i in file_obj.chunks():
                f1.write(i)
        f1.close()
        process_result = ps.process(file_path)
        if len(process_result)==2:
            estimate_rmax=str(process_result[1])
        saxs_data = process_result[0]

        iq_path="/root/sites/hhe-site/decodeSAXS/reconstruction_web/media/result/" + cur_time + '/' + 'processed.iq'
        np.savetxt(iq_path,saxs_data,fmt='%.3f')

        main_path='/root/sites/hhe-site/SAXS_reconstruction'
        outputpath='/root/sites/hhe-site/decodeSAXS/reconstruction_web/media/result/'+cur_time

        if is_number(estimate_rmax):
            Rmax = float(estimate_rmax)
            rec_cmd = ['sastbx.python %s/main.py > %s/logprint.txt --iq_path %s --output_folder %s --rmax %f' % (
            main_path, outputpath, iq_path, outputpath, Rmax), send_email, job_name, cur_time]
        else:
            rec_cmd = ['sastbx.python %s/main.py > %s/logprint.txt --iq_path %s --output_folder %s' % (
            main_path, outputpath, iq_path, outputpath), send_email, job_name, cur_time]
        
        q.put(rec_cmd)
        if tag:
            runproj()


def runproj():
    tag=False
    resultpath='/root/sites/hhe-site/decodeSAXS/reconstruction_web/media/result/'
    job_info = q.get(block=False)
    job_cmd = job_info[0]
    email_addr = job_info[1]
    job_nameinfo = job_info[2]
    job_fileinfo = job_info[3]
    try:
        run_stat = os.system(job_cmd)
    except:
        pass

    if run_stat == 0:
        try:
            os.system("cd %s/%s && rm log.txt && rm logprint.txt && rm out.pdb && mv final_saxs.txt finalfit.txt" % (
                resultpath, job_fileinfo))
            os.system("cd %s && tar -cvf %s.tar.gz %s && mv %s.tar.gz %s" % (resultpath, job_nameinfo, job_fileinfo,job_nameinfo,job_fileinfo))

            from_addr = 'hehao1777@163.com'
            password = 'hehao1777'
            to_addr = email_addr
            smtp_server = 'smtp.163.com'
            msg = MIMEMultipart()
            msg['From'] = _format_addr(u'decodeSAXS <%s>' % from_addr)
            msg['To'] = _format_addr(u'Users <%s>' % to_addr)
            msg['Subject'] = Header(u'the results of decodeSAXS', 'utf-8').encode()

            # add MIMEText:
            contenthtml="""<html><head><body><p>Thanks for using decodeSAXS, hope it helpful for you, any suggestions you can contact with us.</p><p>Your job ID is :""" + job_fileinfo + """</p><p>you can check your result here: </p><p><a href="http://liulab.csrc.ac.cn:10005/check/" mce_href="http://liulab.csrc.ac.cn:10005/check/">liulab.csrc.ac.cn:10005/check/</a></p></body></head></html>"""
            #msg.attach(MIMEText("Thanks for using decodeSAXS, hope it helpful for you, any suggestions you can contact with us.\nYour job ID is : %s\nyou can check your result here: liulab.csrc.ac.cn:10005/check/"%job_file, 'plain'))
            msg.attach(MIMEText(contenthtml, 'html'))
            # add file:
            filepath=resultpath+'/'+job_fileinfo
            files=os.listdir(filepath)
            job_name=job_nameinfo+'.tar.gz'

            '''
            for filei in files:
                if '.tar.gz' in filei:
                    job_name=filei
                    break
            '''
            with open('%s/%s/%s'%(resultpath,job_fileinfo,job_name), 'rb') as f:
                att = MIMEBase('application', 'octet-stream')
                att.set_payload(f.read())
                att.add_header('Content-Disposition', 'attachment', filename = ('utf-8','','%s'%job_name))
                encoders.encode_base64(att)
                msg.attach(att)

                #mime = MIMEBase('image', 'jpg', filename='0.jpg')
                #mime.add_header('Content-Disposition', 'attachment', filename='0.jpg')
                #mime.add_header('Content-ID', '<0>')
                #mime.add_header('X-Attachment-Id', '0')
                #mime.set_payload(f.read())
                #encoders.encode_base64(attachfile)
                #msg.attach(attachfile)
                

            server = smtplib.SMTP(smtp_server, 25)
            server.set_debuglevel(1)
            server.login(from_addr, password)
            try:
                server.sendmail(from_addr, [to_addr], msg.as_string())
            except smtplib.SMTPConnectError as e:
                print '邮件发送失败，连接失败:', e.smtp_code, e.smtp_error
            except smtplib.SMTPAuthenticationError as e:
                print '邮件发送失败，认证错误:', e.smtp_code, e.smtp_error
            except smtplib.SMTPSenderRefused as e:
                print '邮件发送失败，发件人被拒绝:', e.smtp_code, e.smtp_error
            except smtplib.SMTPRecipientsRefused as e:
                print '邮件发送失败，收件人被拒绝:', e.smtp_code, e.smtp_error
            except smtplib.SMTPDataError as e:
                print '邮件发送失败，数据接收拒绝:', e.smtp_code, e.smtp_error
            except smtplib.SMTPException as e:
                print '邮件发送失败, ', e.message
            except Exception as e:
                print '邮件发送异常, ', str(e)
            finally:
                server.quit()
        except:
            pass
    tag=True
    if not q.empty():
        runproj()






def getform(request):
    try:
        cur_time = int(time.time())
        thread.start_new_thread(generatedata, (request,cur_time,))
    except:
        return render(request, "error.html")
    context = {}
    context["id"] = str(cur_time)
    return render(request, "submitresult.html", context)

def checkresult(request):
    if request.method == "POST":
        check_id = request.POST.get("check_id")
        check_id = check_id.strip()
        check_path = "./reconstruction_web/media/result/" + check_id
        downloadlink = ''
        status = 'no'
        havepdb = 'no'
        upload_saxs_path = ''
        try:
            check_files = os.listdir(check_path)
            total_num = len(check_files)
            check_num = 0
            for dir in check_files:
                if '.tar.gz' in dir:
                    status = 'yes'
                    downloadlink = dir
                    break
                else:
                    check_num += 1
            for dir in check_files:
                if 'upload_saxs' in dir:
                    upload_saxs_path=check_path+'/'+ dir
                    break
            if check_num == total_num:
                print 'not found or still process'
        except:status = 'wrong_jobid'
        context = {}
        context["status"] = status
        context["havepdb"] = havepdb
        context["downloadlink"] = downloadlink
        context["filepath"] = check_id
        sourcesaxsdata = ps.generatesaxsstr(upload_saxs_path)
        fit_saxs_path = check_path+'/finalfit.txt'
        fitsaxsdata = ps.generatesaxsstr(fit_saxs_path)
        context["sourcesaxsdata"] = sourcesaxsdata
        context["fitsaxsdata"] =fitsaxsdata
        #print context["sourcesaxsdata"]
        return render(request, "getresult.html", context)



def alignwithresult(request):
    if request.method == "POST":
        check_id = request.POST.get("job_number")
        downloadlink = ''
        pdbpath="./reconstruction_web/media/result/" + check_id
        pdb_obj = request.FILES['up_pdb']
        if '.pdb' in pdb_obj.name:
            with open("./reconstruction_web/media/result/" + check_id + '/' + 'upload_pdb.pdb', "wb") as f2:
                # f2.seek(0, 0)
                for j in pdb_obj.chunks():
                    f2.write(j)
        #pdbfile = '%s/out.ccp4'%pdbpath
        #cavitymodel = model_interface.build_model(pdbfile, 'pdb', 20, None)
        #shiftrmax=cavitymodel.rmax*0.9
        #args = ['fix=%s/out.ccp4'%pdbpath, 'typef=ccp4', 'mov=%s/upload_pdb.pdb'%pdbpath, 'rmax=%f'%shiftrmax]
        #zalign.run(args, pdbpath)
        os.system("sastbx.python /root/sites/hhe-site/decodeSAXS/reconstruction_web/run_zalign.py %s"%check_id)
        status = 'yes'
        havepdb = 'yes'

        context = {}
        context["status"] = status
        context["havepdb"] = havepdb
        context["filepath"] = check_id

        check_path = "./reconstruction_web/media/result/" + check_id
        upload_saxs_path=''
        check_files = os.listdir(check_path)
        for diri in check_files:
            if 'upload_saxs' in diri:
                upload_saxs_path=check_path+'/'+ diri
            if '.tar.gz' in diri:
                downloadlink = diri
        sourcesaxsdata = ps.generatesaxsstr(upload_saxs_path)
        fit_saxs_path = check_path+'/finalfit.txt'
        fitsaxsdata = ps.generatesaxsstr(fit_saxs_path)
        context["downloadlink"] = downloadlink
        context["sourcesaxsdata"] = sourcesaxsdata
        context["fitsaxsdata"] =fitsaxsdata

        return render(request, "getresult.html", context)

