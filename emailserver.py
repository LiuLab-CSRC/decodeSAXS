# -*- coding: utf-8 -*-
import socket
import threading
import SocketServer
import json, types,string
import os, time
import numpy as np
import re
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.utils import parseaddr, formataddr
import smtplib 

web_outpath=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reconstruction_web/media/result')

def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr(( \
        Header(name, 'utf-8').encode(), \
        addr.encode('utf-8') if isinstance(addr, unicode) else addr))


class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024)
        jdata = json.loads(data)
        job_file = jdata[0]['job_file'].encode("utf-8")
        send_email = jdata[0]['send_email'].encode("utf-8")
        from_addr = 'hehao1777@163.com'
        password = 'hehao1777'
        to_addr = send_email
        smtp_server = 'smtp.163.com'
        msg = MIMEMultipart()
        msg['From'] = _format_addr(u'decodeSAXS <%s>' % from_addr)
        msg['To'] = _format_addr(u'Users <%s>' % to_addr)
        msg['Subject'] = Header(u'the results of decodeSAXS', 'utf-8').encode()

        # add MIMEText:
        msg.attach(MIMEText('Thanks for using decodeSAXS, hope it helpful for you, any suggestions you can contact with us.\n', 'plain', 'utf-8'))
        msg.attach(MIMEText('''you can check your result here: <p><a herf="liulab.csrc.ac.cn:10005/check/">check</a></p>''', 'html', 'utf-8'))
        msg.attach(MIMEText('your job ID is : %s\n'%job_file, 'plain', 'utf-8'))
        # add file:
        with open('%s/%s/%s.tar.gz'%(web_outpath,job_file,job_file), 'rb') as f:
            att = MIMEBase('application', 'octet-stream')
            att.set_payload(f.read())
            att.add_header('Content-Disposition', 'attachment', filename = ('utf-8','','%s.tar.gz'%job_file))
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


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "0.0.0.0", 10006 
    
    SocketServer.TCPServer.allow_reuse_address = True
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    print "Server loop running in thread:", server_thread.name
    print " .... waiting to send email"
    server.serve_forever()
    
