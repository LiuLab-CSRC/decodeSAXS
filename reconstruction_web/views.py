# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from django.http import StreamingHttpResponse
import os
import thread
import time
import socket
import json
import numpy as np
import processSaxs as ps
from sastbx.zernike_model import model_interface
import zalign


# Create your views here.

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
    the_file_name = str(download_name).split(".")
    filename = os.path.join('./reconstruction_web/media/result/'+the_file_name[0]+'/'+str(download_name))
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


def generatedata(request,cur_time):
    if request.method == "POST":
        cur_time = str(cur_time)
        file_obj = request.FILES["up_file"]
        job_name = request.POST.get('job_name')
        estimate_rmax=request.POST.get('estimate_rmax')
        send_email=request.POST.get('send_email')
        job_log=open('joblog.txt','a')
        print >> job_log, cur_time+','+job_name
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
        sendmessage = [{'saxs_data': saxs_data, 'job_file': cur_time, 'estimate_rmax': estimate_rmax, 'send_email': send_email}]
        jsendmessage = json.dumps(sendmessage)


        HOST, PORT = "10.0.0.20", 50001
        #print "Send: {}".format(jsendmessage)
        client(HOST, PORT, jsendmessage)


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
        check_path = "./reconstruction_web/media/result/" + check_id
        downloadlink = ''
        try:
            check_files = os.listdir(check_path)
            total_num = len(check_files)
            check_num = 0
            status = 'no'
            havepdb = 'no'
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
        context["filepath"] = downloadlink.split('.')[0]
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
        args = ['fix=%s/out.ccp4'%pdbpath, 'typef=ccp4', 'mov=%s/upload_pdb.pdb'%pdbpath, 'rmax=%f'%shiftrmax]
        zalign.run(args, pdbpath)
        #os.system("sastbx.python %s"%args)
        status = 'yes'
        havepdb = 'yes'
        downloadlink = check_id+'.tar.gz'

        context = {}
        context["status"] = status
        context["havepdb"] = havepdb
        context["downloadlink"] = downloadlink
        context["filepath"] = downloadlink.split('.')[0]

        return render(request, "getresult.html", context)

