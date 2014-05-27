#!/usr/bin/python

import itertools, os,argparse, subprocess, multiprocessing
from configobj import ConfigObj
from datetime import datetime
import rCodeGen, utility
import attribute

parser = argparse.ArgumentParser(description='This program will get results for all the subexperiments. \n\
An e.g. command line is \n\
rsGenForAllSubE.py -e ob/e/4/ -a glmnet -td ob/data/ro/20140204 -pd ob/data/ro/20140205 -g ob/generators/ -run real -sequence serial -targetClass multinomial -skipM Yes -skipP Yes',formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('-e', required=True,help='Directory of the experiment')
parser.add_argument('-a', required=True,help='Algorithm name.')
parser.add_argument('-td', required=True,help='Training directory')
parser.add_argument('-pd', required=True,help='Prediction directory')
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
parser.add_argument('-wt',required=False,help="default/exp , weight type to be given to different days")
args = parser.parse_args()

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
if args.wt == None:
    args.wt = "default"
                    
if(args.sequence == "dp"):
    import dp

config = ConfigObj(args.e+"/design.ini")
features = config["features"]

algo = rCodeGen.getAlgoName(args)

def scriptWrapperForFeatureGeneration(trainingDirectory):
    utility.runCommand(["aGenForE.py","-e",args.e,"-d",trainingDirectory,"-g",args.g,"-run",args.run,"-sequence",args.sequence,'-tickSize',args.tickSize],args.run,args.sequence)
        
if(args.sequence == "dp"):
    import aGenForE
    experimentFolder = args.e
    dataFolder = args.td
    generatorsFolder = args.g
    commandList = []
    lListofTrainingDirectories = attribute.getListOfTrainingDirectoriesNames(args.dt,args.td) 
    for trainingDirectory in lListofTrainingDirectories:
        commandList.extend(aGenForE.getCommandList(experimentFolder,trainingDirectory,generatorsFolder,args.tickSize))
    commandList.extend(aGenForE.getCommandList(experimentFolder,args.pd,generatorsFolder,args.tickSize))
    # Seperate into 2 different list one for aGen and another for operateOnAttribute

    aGenList = []
    attribute.getGenerationCommands(commandList,aGenList)
    utility.runCommandList(aGenList,args)
    dp.printGroupStatus()

    operateOnAttributeList = []
    attribute.getOperationCommands(commandList,operateOnAttributeList)
    operateOnAttributeListAsPerPriority = attribute.getOperationCommandsInPriority(operateOnAttributeList)
    for i in operateOnAttributeListAsPerPriority:
        utility.runCommand(i,args.run,args.sequence)
        dp.printGroupStatus() 

else:
    lListOfTrainingDirectories = attribute.getListOfTrainingDirectoriesNames(args.dt,args.td) 
    lListOfTrainPredictDirectories = lListOfTrainingDirectories
    lListOfTrainPredictDirectories.append(args.pd)
    if args.sequence == 'lp':
            # to run it in local parallel mode
        pool = multiprocessing.Pool() # this will return the number of CPU's
        results = pool.map(scriptWrapperForFeatureGeneration,lListOfTrainPredictDirectories)
    else:
        results = map(scriptWrapperForFeatureGeneration,lListOfTrainPredictDirectories)

utility.runCommand(["rGenForAllSubE.py","-e",args.e,"-a",algo,"-run",args.run,"-sequence",args.sequence,"-targetClass",args.targetClass,"-td",args.td , \
                    "-pd",args.pd,"-skipM",args.skipM,"-skipP",args.skipP,"-mpMearge",args.mpMearge,'-dt',args.dt, '-wt' , args.wt],args.run,args.sequence)
if(args.sequence == "dp"):
    print dp.printGroupStatus()

if(args.sequence == "dp"):
    import runAllRScriptsForAllSubE

    if args.mpMearge.lower() == "yes":
        commandList = runAllRScriptsForAllSubE.getTrainPredictCommandList(args.e,args.a,args.td,args.pd,args.dt,args.wt)
        utility.runCommandList(commandList,args)
        print dp.printGroupStatus()
    else:                
        commandList = runAllRScriptsForAllSubE.getTrainCommandList(args.e,args.a,args.td,args.dt,args.wt)
        utility.runCommandList(commandList,args)
        print dp.printGroupStatus()
    
        commandList = runAllRScriptsForAllSubE.getPredictCommandList(args.e,args.a,args.pd,args.td,args.dt,args.wt)
        utility.runCommandList(commandList,args)
        print dp.printGroupStatus()

else:
    utility.runCommand(["runAllRScriptsForAllSubE.py","-td",args.td,"-pd",args.pd,"-e",args.e,"-a",algo, '-wt' , args.wt,\
                        "-dt",args.dt ,"-sequence",args.sequence,"-run",args.run,"-mpMearge",args.mpMearge],args.run,args.sequence)
    pass

dirName=os.path.dirname(args.e)
            
designFiles = utility.list_files(dirName+"/s/")    
# lets make a list of all the experiments for which we need to run cMatrixGen and trading
experimentNames = list()
for designFile in designFiles:
    experimentName = os.path.dirname(designFile)
    experimentNames.append(experimentName)

def scriptWrapper(experimentName):
    if args.targetClass == "multinomial" :
#        utility.runCommand(["cMatrixGen.py","-d",args.pd,"-e",experimentName,"-a",algo],args.run,args.sequence)
        utility.runCommand(["./ob/quality/tradeE5.py","-e",experimentName,"-skipT",args.skipT,"-a",algo,"-entryCL","55","-exitCL","45","-orderQty","500",\
                            '-dt',args.dt,"-targetClass",args.targetClass,"-td",args.td , "-pd",args.pd,'-tickSize',args.tickSize,'-wt',args.wt],args.run,args.sequence)
        utility.runCommand(["./ob/quality/tradeE5.py","-e",experimentName,"-skipT",args.skipT,"-a",algo,"-entryCL","90","-exitCL","50","-orderQty","500",\
                            '-dt',args.dt,"-targetClass",args.targetClass,"-td",args.td , "-pd",args.pd,'-tickSize',args.tickSize,'-wt',args.wt],args.run,args.sequence)
        utility.runCommand(["./ob/quality/tradeE5.py","-e",experimentName,"-skipT",args.skipT,"-a",algo,"-entryCL","60","-exitCL","40","-orderQty","500",\
                            '-dt',args.dt,"-targetClass",args.targetClass,"-td",args.td , "-pd",args.pd,'-tickSize',args.tickSize,'-wt',args.wt],args.run,args.sequence)
        utility.runCommand(["./ob/quality/tradeE5.py","-e",experimentName,"-skipT",args.skipT,"-a",algo,"-entryCL","50","-exitCL","25","-orderQty","500",\
                            '-dt',args.dt,"-targetClass",args.targetClass,"-td",args.td , "-pd",args.pd,'-tickSize',args.tickSize,'-wt',args.wt],args.run,args.sequence)
    else:
        utility.runCommand(["./ob/quality/tradeE6.py","-e",experimentName,"-skipT",args.skipT,"-a",algo,"-entryCL","90","-exitCL","50","-orderQty","500",\
                            '-dt',args.dt,"-targetClass",args.targetClass,"-td",args.td , "-pd",args.pd,'-tickSize',args.tickSize,'-wt',args.wt],args.run,args.sequence)
        utility.runCommand(["./ob/quality/tradeE6.py","-e",experimentName,"-skipT",args.skipT,"-a",algo,"-entryCL","75","-exitCL","50","-orderQty","500",\
                            '-dt',args.dt,"-targetClass",args.targetClass,"-td",args.td , "-pd",args.pd,'-tickSize',args.tickSize,'-wt',args.wt],args.run,args.sequence)
        utility.runCommand(["./ob/quality/tradeE6.py","-e",experimentName,"-skipT",args.skipT,"-a",algo,"-entryCL","60","-exitCL","50","-orderQty","500",\
                            '-dt',args.dt,"-targetClass",args.targetClass,"-td",args.td , "-pd",args.pd,'-tickSize',args.tickSize,'-wt',args.wt],args.run,args.sequence)
        
if args.sequence == 'lp':
    # to run it in local parallel mode
    pool = multiprocessing.Pool() # this will return the number of CPU's
    results = pool.map(scriptWrapper,experimentNames)
else:
    results = map(scriptWrapper,experimentNames)

if(args.sequence == "dp"):
    print dp.printGroupStatus()
