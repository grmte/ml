import os, subprocess, time
from datetime import datetime
from termcolor import colored

from celery import Celery

commandStatus = dict()

app = Celery('dp', broker='amqp://guest@localhost//',backend='amqp://guest@localhost//')

@app.task
def add(x, y):
    return x + y

@app.task
def runCommand(pProgDefinationList):
    message = "\nExecuting>"+' '.join(pProgDefinationList)
    print colored(message,'red')
    tStart = datetime.now()
    returnState = subprocess.check_call(pProgDefinationList)
    tEnd = datetime.now()
    if(returnState < 0):
        print "Unrecoverable error code: " + str(returnState)
        os._exit(-1)
    else:
        print "Time taken to run the program is " + str(tEnd - tStart)

def printGroupStatus():
    global commandStatus
    numberOfCommandsNotCompleted = 0
    while(True):
        os.system('clear') # on linux / os x
        print "%10s->%s \n" % ("Status","Command")
        for k, v in commandStatus.iteritems():
            status = str(v.ready())
            print "%10s->%s \n" % (status,k)
            if(v.ready()==False):
                numberOfCommandsNotCompleted += 1
        if(numberOfCommandsNotCompleted > 0):
            time.sleep(1)
            numberOfCommandsNotCompleted = 0
            continue
        else:
            commandStatus = dict() # since this group has finished so now reinitializing the dict to empty
            break
