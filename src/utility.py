import os, subprocess,time
from datetime import datetime
from termcolor import colored
import dp
def list_files(dir):                                                                                                  
    r = []                                                                                                            
    subdirs = [x[0] for x in os.walk(dir)]                                                                            
    for subdir in subdirs:                                                                                            
        files = os.walk(subdir).next()[2]                                                                             
        if (len(files) > 0):                                                                                          
            for file in files:                                                                                        
                if "design.ini" in file and "design.ini~" not in file:
                    r.append(subdir + "/" + file)                                                                         
    return r       

def runCommand(pProgDefinationList,pRun,pRunType):
    lModifiedProgDefinationList = removeNullFieldsIntheList(pProgDefinationList)
    if(pRun == "dry"):
        message = "\ndryrun>"+' '.join(lModifiedProgDefinationList)
        print colored(message,'red')
        return
    elif(pRunType == "dp"):
        message = "\nsubmitting>"+' '.join(lModifiedProgDefinationList)
        print colored(message,'red')
        dp.commandStatus[' '.join(lModifiedProgDefinationList)] = dp.runCommand.delay(lModifiedProgDefinationList)
        #print dp.commandStatus
        return
    message = "\nexecuting>"+' '.join(lModifiedProgDefinationList)
    print colored(message,'red')
    tStart = datetime.now()
    returnState = subprocess.check_call(lModifiedProgDefinationList)
    tEnd = datetime.now()
    if(returnState < 0):
        print "Unrecoverable error code: " + str(returnState)
        os._exit(-1)
    else:
        print "Time taken to run the program is " + str(tEnd - tStart)

def removeNullFieldsIntheList(pProgDefinationList):
    count = 0
    new_command = []
    loopLength = len(pProgDefinationList) - 1
    while( count < loopLength ):
        if pProgDefinationList[count+1] == None:
            print "Following field has value None :-" ,  pProgDefinationList[count]
            count = count + 1
        else:
            new_command.append( pProgDefinationList[count] )
        count = count + 1
    if count == loopLength:
        new_command.append(pProgDefinationList[count]) 
    return new_command
        
def runCommandList(pCommandList,pArgs):
    run = pArgs.run
    sequence = pArgs.sequence
    for command in pCommandList:
        if(isinstance(command[0],list)):
            runCommandList(command,pArgs)
            continue
        runCommand(command,run,sequence)

def runListOfCommandsWithMaxUtlilizationOfWorkers(pCommandList,pArgs,pNameOfCommandList,pNumberofWorkers):  #Instead of commandStatus use ListOfWorkers  throughout the code
    l_index_of_task = 0
    allMachinesFreeNow = True
#    print "PNameOfCommandList,"   #At Console We show column1 : workerInfo , Column2 : Status, Column3: NumberofTasksCompletedFromThisListOfCommands
    if(pArgs.run == "dry"):
        runCommandList(pCommandList,pArgs)
        return
    if(pArgs.sequence == "dp"):
        dp.commandStatus = {}
        runCommandList(pCommandList[0:min(len(pCommandList),pNumberofWorkers)],pArgs)
        l_index_of_task = min(len(pCommandList),pNumberofWorkers)
        lWorkersList = []
        for k, v in dp.commandStatus.iteritems():
            lWorkersList.append(v)
        while(True):
            lWorkersList = []
            for k, v in dp.commandStatus.iteritems():
                lWorkersList.append(v)
            for v in lWorkersList:
                if(v.ready() and l_index_of_task < len(pCommandList)):
                    for k, v1 in dp.commandStatus.iteritems():
                        if(v1 == v):
                            del dp.commandStatus[k]
                            break
                    runCommand(pCommandList[l_index_of_task],pArgs.run,pArgs.sequence)
                    l_index_of_task+=1
                    allMachinesFreeNow = False
                elif(v.ready() == False):
                    allMachinesFreeNow = False
            if(l_index_of_task==len(pCommandList) and allMachinesFreeNow == True):
                break
            os.system('clear')
            print "Main Task Name",pNameOfCommandList
            for k, v in dp.commandStatus.iteritems():
                status = str(v.ready())
                print "%10s->%s" % (status,k)
            allMachinesFreeNow = True
            time.sleep(1)
    dp.commandStatus = {}
    
