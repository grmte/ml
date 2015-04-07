#!/usr/bin/python                                                                                                                                                                                                                           
import argparse, glob
import utility
import multiprocessing  # read https://medium.com/building-things-on-the-internet/40e9b2b36148
from functools import partial
import os,sys
import attribute
from configobj import ConfigObj

parser = argparse.ArgumentParser(description='This program will run mGenForE.py and pGenForE.py. An e.g. command line is \n \
    rGenForE.py -e ob/e/9.1/ -a glmnet -sequence serial -targetClass multinomial -skipM Yes -pd ob/data/ro/20140205 -skipP Yes', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-e', required=True,help='Directory of the experiment')
parser.add_argument('-td',required=True,help='Training Directory')
parser.add_argument("-orderQty",required=True,help="Order qty ")
parser.add_argument('-allSub',required=True,help="yes:-Run the program for all sub combinations , no:-Run Program for just one design file inside experiment main folder")
parser.add_argument('-run', required=True,help='dry or real')
parser.add_argument('-sequence', required=True,help='lp / dp / serial')
parser.add_argument('-nDays',required=True,help="Number of days present in the data set")
parser.add_argument('-e1', required=True,help='Directory of the Depth experiment ')
parser.add_argument('-a', required=False,help='Algorithm name')
parser.add_argument('-targetClass',required=False,help="binomial(target takes only true and false) / multinomial (target values takes more than 2 values)")
parser.add_argument('-skipT',required=False,help="yes or no , If you want to regenerated trade files then make this value no.  Defaults to yes")
parser.add_argument('-skipM',required=False,help="yes or no , If you want to regenerate already generated algorithm model file then make this value No")
parser.add_argument('-skipP',required=False,help="yes or no , If you want to regenerate already generated algorithm prediction file then make this value No")
parser.add_argument('-dt',required=False,help='No of day from start for which it is to be trained ')
parser.add_argument('-wt',required=False,help="default/exp , weight type to be given to different days")
parser.add_argument('-tickSize',required=False,help="Nse Currency = 25000 , Future Options = 5")
parser.add_argument('-t',required=False,help="TransactionCost")
parser.add_argument('-iT',required=False,help='Instrument name')
parser.add_argument('-sP',required=False,help='Strike price of instrument')
parser.add_argument('-oT',required=False,help='Options Type')
parser.add_argument("-nComputers",required=False,help="nComputers")
parser.add_argument('-pd',required=False,help="Prediction directory ")
parser.add_argument('-pdt',required=False,help="Number of prediction directory for which prediction is to be done")
parser.add_argument('-g', required=False,help='Generators directory')
parser.add_argument('-ls', required=False,help='lot size in qty')
parser.add_argument('-te', required=True,help='Trade Engine')
args = parser.parse_args()


#=========Initializing all param and everything ======================
if args.skipT == None:
    args.skipT = "yes"
if args.skipM == None:
    args.skipM = "yes"
if args.skipP == None:
    args.skipP = "yes"
if args.dt == None:
    args.dt = "1"
if args.wt == None:
    args.wt = "default"
if args.pd == None:
    args.pd = args.td
if args.pdt == None:
    args.pdt = args.nDays
if args.g == None:
    args.g = "ob/generators/"
if args.targetClass == None:
    args.targetClass = "binomial"
if args.ls == None:
    print "\nGoing with Lot Size 1"
    args.ls = "1"

if args.iT is not None and args.sP is None and args.oT is None:
    args.sP = "-1"
    args.oT = "0"
    
if "/nsecur/" in args.td:
    if args.t == None:
        args.t = "0.000015"
    if args.tickSize == None:
        args.tickSize = "25000"
elif "/nsefut/" in args.td:
    if args.t == None:
        args.t = "0.00008"
    if args.tickSize == None:
        args.tickSize = "5"

tradeEngine = "./" + args.te
print tradeEngine
entrylist = []
exitlist = []
lQtyList = args.orderQty.split(";")

#entrylist = ";".join(map(str, [37, 37, 37, 40, 37, 40, 40, 45, 45, 35, 30]))
#exitlist = ";".join(map(str, [30, 30, 30, 30, 30, 30, 35, 35, 35, 25, 25]))
entrycl2list = []#";".join(map(str, [30, 25, 25, 25, 30, 30, 35, 35, 30, 25, 25]))
exitcl2list = []#";".join(map(str, [30, 25, 20, 25, 25, 25, 30, 25, 25, 20, 20]))
for i in range(55,65,2):#range(45,53,2):#range(49,55,2):#
    for j in range(44,50,2):#range(40,50,2):#range(44,50,2):#
        for k in range(50,58,2):#range(40,50,2):#range(45,51,2):#
            for l in range(42,48,2):#range(37,43,2):#range(40,48,2):#
                if (i>j) and (j>l) and (k>l) and (i>k):
                    entrylist.append(str(i))
                    exitlist.append(str(j))
                    entrycl2list.append(str(k))
                    exitcl2list.append(str(l))
entrylist = ";".join(entrylist)
exitlist = ";".join(exitlist)
entrycl2list = ";".join(entrycl2list)
exitcl2list = ";".join(exitcl2list)
#entrylist = "37"
#exitlist = "30"
#entrycl2list = "30"
#exitcl2list = "25"
#entrylist=""
#exitlist=""
#for i in range(35,50,1):
#    for j in range(33,i,1):
#        exitlist = exitlist + str(j) + ";"
#        entrylist = entrylist + str(i) + ";"
#exitlist = exitlist[:-1]
#entrylist = entrylist[:-1]
totalCommandsToBeScheduledAtOneGo = 0    
if(args.sequence == "dp"):
    import dp
    if args.nComputers == None:
        print "Required number of computers in which workers are running"
        sys.exit(1)
        
    totalCommandsToBeScheduledAtOneGo = int(args.nComputers)
else:
    if(args.nComputers == None):
        args.nComputers = 1
if args.a is None:
    args.a = "glmnet" #Possible values = ['logitr','glmnet','randomForest']

attribute.initializeInstDetails(args.iT,args.sP,args.oT)
trainingDaysDirectory = attribute.getListOfTrainingDirectoriesNames( int(args.dt) , args.td ,args.iT)
print "Trainin"
predictionDaysDirectory = attribute.getListOfTrainingDirectoriesNames( int(args.pdt) , args.pd ,args.iT)
print predictionDaysDirectory
allDataDirectories = trainingDaysDirectory + predictionDaysDirectory

if args.allSub == "yes" and not os.path.exists(args.e+"/s/"):
    print "Sub directories of experiment does not exist and it is ran for all sub combination. Make allSub = no , or generate sub combination "
    sys.exit(1)
    
#==========Generating Features for all required days =======================
if(args.sequence == "dp"):

    experimentFolder = args.e
    experimentDepthFolder = args.e1
    dataFolder = args.td
    generatorsFolder = args.g
    commandList = []
    for directories in allDataDirectories:
        commandList.append(["aGenForE.py","-e",experimentFolder,"-d",directories,"-g",args.g,"-run",args.run,"-sequence",args.sequence,'-tickSize',args.tickSize,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP])
        pass
#    utility.runListOfCommandsWithMaxUtlilizationOfWorkers(commandList,args,"Best Feature Generation",totalCommandsToBeScheduledAtOneGo)
#    print dp.printGroupStatus()

#    for chunkNum in range(0,len(commandList),totalCommandsToBeScheduledAtOneGo):
#        l_sub_aGenForECodeGenList = commandList[chunkNum:chunkNum+totalCommandsToBeScheduledAtOneGo]
#        utility.runCommandList( l_sub_aGenForECodeGenList ,args)
#        print dp.printGroupStatus() 
    commandList = []
    for directories in allDataDirectories:
        commandList.append(["aGenForE.py","-e",experimentDepthFolder,"-d",directories,"-g",args.g,"-run",args.run,"-sequence",args.sequence,'-tickSize',args.tickSize,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP])
        pass
#    utility.runListOfCommandsWithMaxUtlilizationOfWorkers(commandList,args,"Depth Feature Generation",totalCommandsToBeScheduledAtOneGo)
    print dp.printGroupStatus()
    
#    for chunkNum in range(0,len(commandList),totalCommandsToBeScheduledAtOneGo):
#        l_sub_aGenForECodeGenList = commandList[chunkNum:chunkNum+totalCommandsToBeScheduledAtOneGo]
#        utility.runCommandList( l_sub_aGenForECodeGenList ,args)
#        print dp.printGroupStatus() 

else:
    def scriptWrapperForFeatureGeneration(trainingDirectory):
        utility.runCommand(["aGenForE.py","-e",args.e,"-d",trainingDirectory,"-g",args.g,"-run",args.run,"-sequence",args.sequence,'-tickSize',args.tickSize,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP],args.run,args.sequence)
        pass
#    results = map(scriptWrapperForFeatureGeneration,allDataDirectories)
    def scriptWrapperForFeatureGenerationDepth(trainingDirectory):
        utility.runCommand(["aGenForE.py","-e",args.e1,"-d",trainingDirectory,"-g",args.g,"-run",args.run,"-sequence",args.sequence,'-tickSize',args.tickSize,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP],args.run,args.sequence)
        pass
#    results = map(scriptWrapperForFeatureGenerationDepth,allDataDirectories)

#=======Finding number of feature in design file ====
config = ConfigObj(args.e+"/design.ini")
targetAttributes = attribute.getTargetVariableKeys(config)
one_feature_attributes = attribute.getFeatureVariableKeys(config , targetAttributes.keys()[0])
lengthOfFeatures = len(one_feature_attributes)

#==========Finding Experiment(s) folder for which it is to be run

experimentFolderDirectory = []
if args.allSub == "yes":
    indexOfFeatures = 2
    while indexOfFeatures <= lengthOfFeatures:
        lSubCombinationFolder = args.e+"/s/"+str(indexOfFeatures)+"c"
        designFiles = utility.list_files(lSubCombinationFolder)
        for designFile in designFiles:
            lExperimentFolderName = os.path.dirname(designFile) + "/"
            experimentFolderDirectory.append(lExperimentFolderName)
        indexOfFeatures += 1
            
else:
    experimentFolderDirectory.append(args.e)

print "Experiment Folder Lsit " , experimentFolderDirectory
#==========Running the model in serial mode and rest thing in serial , lp or dp mode as given                 
for lExperimentFolderName in experimentFolderDirectory:
#    utility.runCommand(["mRGenForE.py","-e",lExperimentFolderName,"-a",args.a,"-targetClass",args.targetClass,"-skipM",args.skipM,"-td",args.td, "-dt" , \
#                                  args.dt , '-wt' , args.wt,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP ] , args.run , "serial")
#    scriptName = lExperimentFolderName+"/train" + args.a + "-td." + os.path.basename(os.path.abspath(args.td)) + "-dt." + args.dt + "-wt." + args.wt + attribute.generateExtension() +".r"
#    trainingDataListString = ";".join(trainingDaysDirectory).replace("/ro/","/wf/")
#   
#    utility.runCommand([scriptName,"-d",trainingDataListString] , args.run , "serial")
#    os.system("cp "+args.e+"/*.model "+ args.e1)
    if args.sequence == "dp":
        #=========Putting all command in alist-========
        lRCodeGenCommandList = []
        lRCodeGenDepthCommandList = []
        lPGenRCodeList = []
        lPGenRCodeDepthList = []
        lTradingCommandList = []
        for i in range(len(predictionDaysDirectory)):
            predictionDirAfterLastTD = predictionDaysDirectory[i]
            lRCodeGenCommandList.append((["pRGenForE.py","-e",args.e,"-s",lExperimentFolderName,"-a",args.a,"-skipP",args.skipP,"-td",args.td , "-pd" , predictionDirAfterLastTD , "-dt" , args.dt ,\
                             "-targetClass" , args.targetClass , '-wt' , args.wt ,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP]))
            scriptName=lExperimentFolderName+"/predict" + args.a + "-td." + os.path.basename(os.path.abspath(args.td)) + "-dt." + args.dt +"-pd."  +\
                        os.path.basename(os.path.abspath(predictionDirAfterLastTD)) + "-wt." + args.wt  + attribute.generateExtension() +".r"
            lRCodeGenDepthCommandList.append((["pRGenForE.py","-e",args.e1,"-s",args.e1,"-a",args.a,"-skipP",args.skipP,"-td",args.td , "-pd" , predictionDirAfterLastTD , "-dt" , args.dt ,\
                             "-targetClass" , args.targetClass , '-wt' , args.wt ,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP]))
            scriptNameDepth=args.e1+"/predict" + args.a + "-td." + os.path.basename(os.path.abspath(args.td)) + "-dt." + args.dt +"-pd."  +\
                        os.path.basename(os.path.abspath(predictionDirAfterLastTD)) + "-wt." + args.wt  + attribute.generateExtension() +".r"
            dirName = predictionDirAfterLastTD.replace('/ro/','/wf/')
            lPGenRCodeList.append([scriptName,"-d",dirName])
            lPGenRCodeDepthList.append([scriptNameDepth,"-d",dirName])
            for lQty in lQtyList:
                lTradingCommandList.append([tradeEngine,"-e",args.e1, "-e1",args.e,"-skipT",args.skipT,"-a",args.a,"-entryCL",entrylist,"-exitCL",\
                    exitlist,"-entryCL2",entrycl2list,"-exitCL2",exitcl2list,"-orderQty",lQty,'-dt',args.dt,"-targetClass",args.targetClass,"-td",args.td , "-pd",predictionDirAfterLastTD,\
                                            '-tickSize',args.tickSize,'-wt',args.wt,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP, "-ls", args.ls ])
        #=============Running all command in dp one by one=======      
  
        print lTradingCommandList
#        utility.runListOfCommandsWithMaxUtlilizationOfWorkers(lRCodeGenCommandList,args,"Predict R Code Gen Best",totalCommandsToBeScheduledAtOneGo)
#        utility.runListOfCommandsWithMaxUtlilizationOfWorkers(lRCodeGenDepthCommandList,args,"Predict R Code Gen Depth",totalCommandsToBeScheduledAtOneGo)
#        utility.runListOfCommandsWithMaxUtlilizationOfWorkers(lPGenRCodeList,args,"Predict Best Experiment",totalCommandsToBeScheduledAtOneGo)
#        utility.runListOfCommandsWithMaxUtlilizationOfWorkers(lPGenRCodeDepthList,args,"Predict Depth Experiment",totalCommandsToBeScheduledAtOneGo)
#        utility.runListOfCommandsWithMaxUtlilizationOfWorkers(lTradingCommandList,args,"Running Trade Engine",totalCommandsToBeScheduledAtOneGo)
    else:
        def scriptWrapperForPredictRProgramGeneration(predictionDirAfterLastTD):
            utility.runCommand(["pRGenForE.py","-e",args.e,"-s",lExperimentFolderName,"-a",args.a,"-skipP",args.skipP,"-td",args.td , "-pd" , predictionDirAfterLastTD , "-dt" , args.dt ,\
                                 "-targetClass" , args.targetClass , '-wt' , args.wt ,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP],args.run,args.sequence)
           
        def scriptWrapperForPredictProgramRun(predictionDirAfterLastTD):
            scriptName=lExperimentFolderName+"/predict" + args.a + "-td." + os.path.basename(os.path.abspath(args.td)) + "-dt." + args.dt +"-pd."  +\
                        os.path.basename(os.path.abspath(predictionDirAfterLastTD)) + "-wt." + args.wt  + attribute.generateExtension() +".r"
            dirName = predictionDirAfterLastTD.replace('/ro/','/wf/')
            utility.runCommand([scriptName,"-d",dirName],args.run,args.sequence)

        def scriptWrapperForPredictRProgramGenerationDepth(predictionDirAfterLastTD):
            utility.runCommand(["pRGenForE.py","-e",args.e1,"-s",args.e1,"-a",args.a,"-skipP",args.skipP,"-td",args.td , "-pd" , predictionDirAfterLastTD , "-dt" , args.dt ,\
                                 "-targetClass" , args.targetClass , '-wt' , args.wt ,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP],args.run,args.sequence)
           
        def scriptWrapperForPredictProgramRunDepth(predictionDirAfterLastTD):
            scriptName= args.e1 +"/predict" + args.a + "-td." + os.path.basename(os.path.abspath(args.td)) + "-dt." + args.dt +"-pd."  +\
                        os.path.basename(os.path.abspath(predictionDirAfterLastTD)) + "-wt." + args.wt  + attribute.generateExtension() +".r"
            dirName = predictionDirAfterLastTD.replace('/ro/','/wf/')
            utility.runCommand([scriptName,"-d",dirName],args.run,args.sequence)

        def scripWrapperForTradingCommand(predictionDirAfterLastTD):
            
            global tradeEngine
            for lQty in lQtyList:
                utility.runCommand([tradeEngine,"-e",args.e1, "-e1",args.e,"-skipT",args.skipT,"-a",args.a,"-entryCL",entrylist,"-exitCL",\
                   exitlist,"-entryCL2",entrycl2list,"-exitCL2",exitcl2list,"-orderQty",lQty,'-dt',args.dt,"-targetClass",args.targetClass,"-td",args.td , "-pd",predictionDirAfterLastTD,\
                                            '-tickSize',args.tickSize,'-wt',args.wt,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP , "-ls", args.ls],args.run,args.sequence)
#                utility.runCommand(["./ob/quality/tradeE7Optimized.py","-e",lExperimentFolderName,"-skipT",args.skipT,"-a",args.a,"-entryCL",entrylist,"-exitCL",exitlist,"-orderQty",lQty,'-dt',args.dt,"-targetClass",args.targetClass,"-td",args.td , "-pd",predictionDirAfterLastTD,'-tickSize',args.tickSize,'-wt',args.wt,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP ],args.run,args.sequence)

#                utility.runCommand(["./ob/quality/tradeE7WithMultipleProbablities.py","-e",lExperimentFolderName,"-skipT",args.skipT,"-a",args.a,"-entryCL",entrylist,"-exitCL",\
#                    exitlist,"-entryCL2",entrycl2list,"-exitCL2",exitcl2list,"-orderQty",lQty,'-dt',args.dt,"-targetClass",args.targetClass,"-td",args.td , "-pd",predictionDirAfterLastTD,\
#                                            '-tickSize',args.tickSize,'-wt',args.wt,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP ],args.run,args.sequence)
            
        if args.sequence == "lp":
                # to run it in local parallel mode
            pool = multiprocessing.Pool() # this will return the number of CPU's
            results = pool.map(scriptWrapperForPredictRProgramGeneration,predictionDaysDirectory)
            results = pool.map(scriptWrapperForPredictProgramRun,predictionDaysDirectory)
            results = pool.map(scripWrapperForTradingCommand,predictionDaysDirectory)
        else:
            print "None"
#            results = map(scriptWrapperForPredictRProgramGeneration,predictionDaysDirectory)
#            results = map(scriptWrapperForPredictRProgramGenerationDepth,predictionDaysDirectory)
#            results = map(scriptWrapperForPredictProgramRun,predictionDaysDirectory)
#            results = map(scriptWrapperForPredictProgramRunDepth,predictionDaysDirectory)
            results = map(scripWrapperForTradingCommand,predictionDaysDirectory)
            
    if args.iT is not None:
        message = args.iT + "_ForExperimnet_" + lExperimentFolderName +"-Results. With DEPTH Pred"
    else:
        message = "ml_experiments"
        
    utility.runCommand(["accumulate_results.py","-e",args.e1,"-a",args.a,"-t",args.t,"-td",args.td, "-dt" , "1" , '-nD' , str(args.nDays) , "-m" ,message , "-f" , "1","-iT",args.iT,"-oT",args.oT,"-sP",args.sP],args.run,args.sequence)
    if args.sequence == "dp":
        print dp.printGroupStatus()
