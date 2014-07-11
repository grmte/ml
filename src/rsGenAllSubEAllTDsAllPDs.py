#!/usr/bin/python

import itertools, os,argparse, subprocess, multiprocessing
from configobj import ConfigObj
from datetime import datetime
import rCodeGen, utility
import attribute
import aGenForE

parser = argparse.ArgumentParser(description='This program will get results for all the subexperiments. \n\
An e.g. command line is \n\
src/rsGenForAllSubE.py -e ob/e/nsecur/24/ -a glmnet -td ob/data/ro/nsecur/20140203/ -dt 10 -pd ob/data/ro/nsecur/20140318/ -run real -sequence lp -targetClass binomial -tickSize 25000 -wt exp -g ob/generators/',formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-e', required=True,help='Directory of the experiment')
parser.add_argument('-a', required=False,help='Algorithm name.')
parser.add_argument('-td', required=True,help='Training directory')
parser.add_argument('-g', required=True,help='Generators directory')
parser.add_argument('-dt',required=False,help='Number of days after start training day specified . Defaults to 1 ')
parser.add_argument('-run', required=True,help='dry (only show dont execute) or real (show and execute)')
parser.add_argument('-sequence', required=True,help='lp (Local parallel) / dp (Distributed parallel) / serial')
parser.add_argument('-targetClass',required=True,help="binomial(target takes only true and false) / multinomial (target values takes more than 2 values)")
parser.add_argument('-skipM',required=False,help="yes or no , If you want to regenerate already generated algorithm model file then make this value No.  Defaults to yes")
parser.add_argument('-skipP',required=False,help="yes or no , If you want to regenerate already generated algorithm prediction file then make this value No.  Defaults to yes")
parser.add_argument('-skipT',required=False,help="yes or no , If you want to regenerated trade files then make this value no.  Defaults to yes")
parser.add_argument('-mpMearge',required=False,help="yes or no , If you want to separate model and prediction files then make this no .  Defaults to yes") 
parser.add_argument('-tickSize',required=True,help="Nse Currency = 25000 , Future Options = 5")
parser.add_argument('-nDays',required=True,help="Number of days present in the data set")
parser.add_argument('-nComputers',required=True,help="Number of computers at which task has to be run present in the data set")
parser.add_argument('-t',required=False,help="TransactionCost")
args = parser.parse_args()

if args.t == None:
    args.t = "0.000015"
if args.skipM == None:
    args.skipM = "yes"
if args.skipP == None:
    args.skipP = "yes"
if args.skipT == None:
    args.skipT = "yes"
if args.mpMearge == None:
    args.mpMearge = "yes"
if args.dt == None:
    args.dt = "1"
                    
if(args.sequence == "dp"):
    import dp

config = ConfigObj(args.e+"/design.ini")
features = config["features"]

algo = rCodeGen.getAlgoName(args)

if args.a is not None:
    allAlgos = [args.a]
else:
    allAlgos = ['logitr','glmnet','randomForest']
    
config = ConfigObj(args.e+"/design.ini")
features = config["features"]
indexOfFeatures = len(features)
allDataDirectories = attribute.getListOfTrainingDirectoriesNames( int(args.nDays) , args.td )
dataFolder = args.td
generatorsFolder = args.g
commandList = []

experimentFolder = args.e
for trainingDirectory in allDataDirectories:
    commandList.extend(aGenForE.getCommandList(experimentFolder,trainingDirectory,generatorsFolder,args.tickSize))
# Seperate into 2 different list one for aGen and another for operateOnAttribute
aGenList = []
attribute.getGenerationCommands(commandList,aGenList)
totalGeneratorsWhichCanBeScheduled = 2 * int(args.nComputers)

for chunkNum in range(0,len(aGenList),totalGeneratorsWhichCanBeScheduled ):
    lSubGenList = aGenList[chunkNum:chunkNum+totalGeneratorsWhichCanBeScheduled]
    utility.runCommandList(lSubGenList,args)
    print dp.printGroupStatus()
     
operateOnAttributeList = []
attribute.getOperationCommands(commandList,operateOnAttributeList)
operateOnAttributeListAsPerPriority = attribute.getOperationCommandsInPriority(operateOnAttributeList)
operatorRunInParallel = []
LastRunDate = allDataDirectories[-1]
for operatorCommand in operateOnAttributeListAsPerPriority:
    operatorRunInParallel.append(operatorCommand) 
    if LastRunDate in operatorCommand :
        utility.runCommandList(operatorRunInParallel,args)
        dp.printGroupStatus() 
        operatorRunInParallel = []
        
for algo in allAlgos:
    while indexOfFeatures >= 2:
        lSubCombinationFolder = args.e+"/s/"+str(indexOfFeatures)+"c"
        designFiles = utility.list_files(lSubCombinationFolder)
        for designFile in designFiles:
            lExperimentFolderName = os.path.dirname(designFile) + "/"
            print lExperimentFolderName
            for wt in ['default']:
                lRCodeGenCommandList = []
                lMGenRCodeList = []
                lPGenRCodeList = []
                lTradingCommandList = [] 
                for i in range(len(allDataDirectories)-int(args.dt)):
                    args.td = allDataDirectories[i]
                    predictionDirLastTD = allDataDirectories[i + int(args.dt) - 1]
                    predictionDirAfterLastTD = allDataDirectories[i + int(args.dt)]

                    lRCodeGenCommandList.append(["mRGenForE.py","-e",lExperimentFolderName,"-a",algo,"-targetClass",args.targetClass,"-skipM",args.skipM,"-td",args.td, "-dt" , args.dt , '-wt' , wt])
                    lRCodeGenCommandList.append(["pRGenForE.py","-e",args.e,"-s",lExperimentFolderName,"-a",algo,"-skipP",args.skipP,"-td",args.td , "-pd" , predictionDirLastTD , "-dt" , args.dt , "-targetClass" , args.targetClass , '-wt' , wt])
                    lRCodeGenCommandList.append(["pRGenForE.py","-e",args.e,"-s",lExperimentFolderName,"-a",algo,"-skipP",args.skipP,"-td",args.td , "-pd" , predictionDirAfterLastTD , "-dt" , args.dt , "-targetClass" , args.targetClass , '-wt' , wt])

                    dirName = args.td.replace('/ro/','/wf/')
                    scriptName = lExperimentFolderName+"/train" + algo + "-td." + os.path.basename(os.path.abspath(args.td)) + "-dt." + args.dt + "-wt." + wt +".r"
                    trainingDataList = [] #";".join(allDataDirectories[i:i+ int(args.dt) ])
                    for trainDirs in allDataDirectories[i:i+ int(args.dt)]:
                        trainingDataList.append(trainDirs.replace('/ro/','/wf/'))
                    trainingDataListString = ";".join(trainingDataList)
                    lMGenRCodeList.append([scriptName,"-d",trainingDataListString])

                    dirName = predictionDirLastTD.replace('/ro/','/wf/')    
                    scriptName=lExperimentFolderName+"/predict" + algo + "-td." + os.path.basename(os.path.abspath(args.td)) + "-dt." + args.dt +"-pd."  + os.path.basename(os.path.abspath(predictionDirLastTD)) + "-wt." + wt +".r"
                    lPGenRCodeList.append([scriptName,"-d",dirName])

                    dirName = predictionDirAfterLastTD.replace('/ro/','/wf/') 
                    scriptName=lExperimentFolderName+"/predict" + algo + "-td." + os.path.basename(os.path.abspath(args.td)) + "-dt." + args.dt +"-pd."  + os.path.basename(os.path.abspath(predictionDirAfterLastTD)) + "-wt." + wt +".r"
                    lPGenRCodeList.append([scriptName,"-d",dirName])
                    
                    lTradingCommandList.append(["./ob/quality/tradeE6.py","-e",lExperimentFolderName,"-skipT",args.skipT,"-a",algo,"-entryCL","55;55;57;57;58;58;60;60;65;65","-exitCL","45;50;45;50;45;50;45;50;45;50","-orderQty","300",\
                                        '-dt',args.dt,"-targetClass",args.targetClass,"-td",args.td , "-pd",predictionDirLastTD,'-tickSize',args.tickSize,'-wt',wt])
                    lTradingCommandList.append(["./ob/quality/tradeE6.py","-e",lExperimentFolderName,"-skipT",args.skipT,"-a",algo,"-entryCL","55;55;57;57;58;58;60;60;65;65","-exitCL","45;50;45;50;45;50;45;50;45;50","-orderQty","300",\
                                        '-dt',args.dt,"-targetClass",args.targetClass,"-td",args.td , "-pd",predictionDirAfterLastTD,'-tickSize',args.tickSize,'-wt',wt])                
                utility.runCommandList(lRCodeGenCommandList,args)
                print dp.printGroupStatus()

                noOfModelsToBeScheduledToOneComputer = 60 / ( indexOfFeatures * int(args.dt) )
                totalModelsWhichCanBeScheduled = noOfModelsToBeScheduledToOneComputer * int(args.nComputers)
                for chunkNum in range(0,len(lMGenRCodeList),totalModelsWhichCanBeScheduled):
                    lSubModelList = lMGenRCodeList[chunkNum:chunkNum+totalModelsWhichCanBeScheduled]
                    utility.runCommandList(lSubModelList,args)
                    print dp.printGroupStatus()
                    
                utility.runCommandList(lPGenRCodeList,args)
                print dp.printGroupStatus()
                
                utility.runCommandList(lTradingCommandList,args)
                print dp.printGroupStatus()            
        indexOfFeatures = indexOfFeatures - 1

    utility.runCommand(["accumulate_results.py","-e",args.e,"-a",algo,"-t",args.t,"-td",args.td, "-dt" , str(args.dt) , '-nD' , str(args.nDays) , "-m" , "Following experiment results" , "-f" , "1"],args.run,args.sequence)