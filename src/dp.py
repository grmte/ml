import os, subprocess, time
from datetime import datetime
from termcolor import colored

from celery import Celery
from celery.task.control import inspect

commandStatus = dict()

# change 10.105.1.194 to the IP of the processing central server
app = Celery('dp', broker='amqp://guest@10.1.35.6//',backend='amqp://guest@10.1.35.6//')

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
    """
    this acts as a stop gate for a group of commands to be executed. So that a sequence can be maintained.
    """
    global commandStatus
    numberOfCommandsNotCompleted = 0
    while(True):
        os.system('clear') # on linux / os x
        print "%10s->%s \n" % ("Status","Command")
        for k, v in commandStatus.iteritems():
            status = str(v.ready())
            print "%10s->%s" % (status,k)
            if(v.ready()==False):
                numberOfCommandsNotCompleted += 1
        """        
        i = inspect()        
        print "Scheduled tasks"
        print i.scheduled()
        print "Active tasks"
        task = i.active()
        print task.keys()
        for t in task.values():
            print t[0]['args'] + " on " + t[0]['hostname']
        """
        if(numberOfCommandsNotCompleted > 0):
            time.sleep(1)
            numberOfCommandsNotCompleted = 0
            continue
        else:
            commandStatus = dict() # since this group has finished so now reinitializing the dict to empty
            break
