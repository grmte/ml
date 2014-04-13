import os, subprocess
from datetime import datetime
from termcolor import colored

from celery import Celery

app = Celery('dp', broker='amqp://guest@localhost//')

@app.task
def add(x, y):
    return x + y

@app.task
def runProgram(pProgDefinationList,run):
    message = "\nExecuting>"+' '.join(pProgDefinationList)
    print colored(message,'red')
    if(run == "dry"):
        return
    tStart = datetime.now()
    returnState = subprocess.check_call(pProgDefinationList)
    tEnd = datetime.now()
    if(returnState < 0):
        print "Unrecoverable error code: " + str(returnState)
        os._exit(-1)
    else:
        print "Time taken to run the program is " + str(tEnd - tStart)

