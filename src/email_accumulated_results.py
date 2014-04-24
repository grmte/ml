#============================================================[ Import Modules ]=================================================================

import smtplib, os, sys, commands, datetime
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders


#============================================================[ Main Coding ]===================================================================

def send_mail(p_send_from, p_send_to, p_send_cc, p_subject, p_text, p_files = [], p_server = "localhost"):
    try:
        assert type(p_send_to) == list
        assert type(p_send_cc) == list
        assert type(p_files) == list
    
        msg = MIMEMultipart()
        msg['From'] = p_send_from
        msg['To'] = COMMASPACE.join(p_send_to)
        msg['Cc'] = COMMASPACE.join(p_send_cc)
        msg['Date'] = formatdate(localtime = True)
        msg['Subject'] = p_subject
        msg.attach(MIMEText(p_text))
        
        for l_files in p_files:
            part = MIMEBase('application', "octet-stream")
            part.set_payload(open(l_files, "rb").read())
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(l_files))
            msg.attach(part)
    
        smtp = smtplib.SMTP(p_server)
        smtp.sendmail(p_send_from, p_send_to + p_send_cc, msg.as_string())
        smtp.close()
        print "Email successfully sent..!"
        
    except Exception, e:
        print "\n* EXCEPTION DURING EMAIL SENDING: ", e
        
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def start_mail(p_files,pExperimentNo,message):
    l_cur_date_time = datetime.datetime.now()
    l_msgbody_postfix = "Email sent on : " + str(l_cur_date_time)
    
    l_msg_body = "Dear All, " + "\n\n" + "Kindly find the attachment of ml experiment run . "+ message + " \n\nThanking you.\n\n" + l_msgbody_postfix
    
    l_subject = "Machine Learning Accumulated results of experiment" + pExperimentNo 
    l_send_to = ['ajay@spalgo.com', 'vikas@spalgo.com', 'mike@mbowles.com']
    l_send_to = ["dipika@spalgo.com"]
    l_send_cc = ['saptarshi@spalgo.com','tulasi@spalgo.com', 'rahul@spalgo.com']
    l_send_from = "MLDailyExperimentResult"
    send_mail(l_send_from, l_send_to, l_send_cc, l_subject, l_msg_body, p_files)
    
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
