import os, subprocess
from datetime import datetime
from termcolor import colored

def list_files(dir):                                                                                                  
    r = []                                                                                                            
    subdirs = [x[0] for x in os.walk(dir)]                                                                            
    for subdir in subdirs:                                                                                            
        files = os.walk(subdir).next()[2]                                                                             
        if (len(files) > 0):                                                                                          
            for file in files:                                                                                        
                if "design.ini" in file:
                    r.append(subdir + "/" + file)                                                                         
    return r       

def runCommand(pProgDefinationList,pRun,pRunType):
    if(pRun == "dry"):
        message = "\ndryrun>"+' '.join(pProgDefinationList)
        print colored(message,'red')
        return
    elif(pRunType == "dp"):
        message = "\nsubmitting>"+' '.join(pProgDefinationList)
        print colored(message,'red')
        import dp
        dp.commandStatus[' '.join(pProgDefinationList)] = dp.runCommand.delay(pProgDefinationList)
        return
    message = "\nexecuting>"+' '.join(pProgDefinationList)
    print colored(message,'red')
    tStart = datetime.now()
    returnState = subprocess.check_call(pProgDefinationList)
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
        newCommand = removeNullFieldsIntheList(command)
        runCommand(newCommand,run,sequence)
