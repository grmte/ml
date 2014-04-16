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

def runCommand(pProgDefinationList,args):
    if(args.run == "dry"):
        message = "\ndryrun>"+' '.join(pProgDefinationList)
        print colored(message,'red')
        return
    elif(args.runType == "dp"):
        message = "\nsubmitting>"+' '.join(pProgDefinationList)
        print colored(message,'red')
        import dp
        dp.runCommand.delay(pProgDefinationList)
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


