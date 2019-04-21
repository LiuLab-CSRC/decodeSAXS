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
import processSaxs as ps



# Create your views here.

def index(request):
    pass
    return render(request, "index.html")

def history(request):
    pass
    return render(request, "history.html")

def checkhistory(request):
    if request.method == "GET":
        check_path = "./reconstruction_web/static/download/"
        returnData = {"rows": []}
        check_files = os.listdir(check_path)
        check_files.sort(reverse=True)
        for check_file in check_files:
            status = 'running'
            downloadlink=''
            if '.' not in check_file:
                dirs = os.listdir(check_path+check_file)

                for dir in dirs:
                    if '.tar.gz' in dir:
                        status = 'finished'
                        downloadlink = dir
                        break

                returnData['rows'].append({
                    "job_ID": check_file,
                    "status": status,
                    "downloadlink": downloadlink,
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
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/download/'+the_file_name[0]+'/'+str(download_name))
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
        file_obj = request.FILES.get("up_file")
        #job_name = request.POST.get('job_name')
        estimate_rmax=request.POST.get('estimate_rmax')
        decode_threshold=request.POST.get('decode_threshold')
        send_email=request.POST.get('send_email')

        os.mkdir("./reconstruction_web/static/download/" + cur_time)
        file_path = "./reconstruction_web/static/download/" + cur_time + '/' + file_obj.name
        with open("./reconstruction_web/static/download/" + cur_time + '/' + file_obj.name, "wb") as f1:
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
        sendmessage = [{'saxs_data': saxs_data, 'job_file': cur_time, 'estimate_rmax': estimate_rmax, 'decode_threshold': decode_threshold, 'send_email': send_email}]
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
        check_path = "./reconstruction_web/static/download/" + check_id
        downloadlink = ''
        try:
            check_files = os.listdir(check_path)
            total_num = len(check_files)
            check_num = 0
            status = 'no'
            for dir in check_files:
                if '.tar.gz' in dir:
                    status = 'yes'
                    downloadlink = dir
                    break
                else:
                    check_num += 1
            if check_num == total_num:
                print 'not found or still process'
        except:status = 'wrong_jobid'
        context = {}
        context["status"] = status
        context["downloadlink"] = downloadlink

        #print context["downloadlink"]
        return render(request, "getresult.html", context)

