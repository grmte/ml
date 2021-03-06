#!/usr/bin/python

import itertools, os,argparse, subprocess, multiprocessing
from configobj import ConfigObj
from datetime import datetime
import rCodeGen, utility
import attribute

parser = argparse.ArgumentParser(description='This program will get results for all the subexperiments. \n\
An e.g. command line is \n\
src/rsGenForAllSubE.py -e ob/e/nsefut/ICICIBANK/ -a glmnet -td ob/data/ro/nsefut/20140801/ -pd ob/data/ro/nsefut/20140922/ -g ob/generators/ -dt 20 -run dry -sequence serial -tickSize 5 -iT ICICIBANK -sP -1 -oT 0 -t 0.00015\n')
parser.add_argument('-e', required=True,help='Directory of the experiment')
parser.add_argument('-a', required=True,help='Algorithm name.')
parser.add_argument('-td', required=True,help='Training directory')
parser.add_argument('-pd', required=True,help='Prediction directory')
parser.add_argument('-g', required=True,help='Generators directory')
parser.add_argument('-dt',required=False,help='Number of days after start training day specified . Defaults to 1 ')
parser.add_argument('-run', required=True,help='dry (only show dont execute) or real (show and execute)')
parser.add_argument('-sequence', required=True,help='lp (Local parallel) / dp (Distributed parallel) / serial')
parser.add_argument('-targetClass',required=False,help="binomial(target takes only true and false) / multinomial (target values takes more than 2 values)")
parser.add_argument('-skipM',required=False,help="yes or no , If you want to regenerate already generated algorithm model file then make this value No.  Defaults to yes")
parser.add_argument('-skipP',required=False,help="yes or no , If you want to regenerate already generated algorithm prediction file then make this value No.  Defaults to yes")
parser.add_argument('-skipT',required=False,help="yes or no , If you want to regenerated trade files then make this value no.  Defaults to yes")
parser.add_argument('-mpMearge',required=False,help="yes or no , If you want to separate model and prediction files then make this no .  Defaults to yes") 
parser.add_argument('-tickSize',required=True,help="Nse Currency = 25000 , Future Options = 5")
parser.add_argument('-wt',required=False,help="default/exp , weight type to be given to different days")
parser.add_argument('-iT',required=False,help='Instrument name')
parser.add_argument('-sP',required=False,help='Strike price of instrument')
parser.add_argument('-oT',required=False,help='Options Type')
parser.add_argument('-nD',required=False,help='for mix match probability to run')
parser.add_argument('-cpu',required=False,help='number of trade engine to be scheduled')
parser.add_argument('-t',required=True,help="Transaction cost ")
args = parser.parse_args()

if args.nD == None:
    args.nD = "26"
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
if args.targetClass == None:
    args.targetClass = "binomial"
if args.cpu == None:
    args.cpu = 4

if(args.sequence == "dp"):
    import dp

config = ConfigObj(args.e+"/design.ini")

algo = rCodeGen.getAlgoName(args)

def scriptWrapperForFeatureGeneration(trainingDirectory):
    utility.runCommand(["aGenForE.py","-e",args.e,"-d",trainingDirectory,"-g",args.g,"-run",args.run,"-sequence",args.sequence,'-tickSize',args.tickSize,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP],args.run,args.sequence)
    pass
attribute.initializeInstDetails(args.iT,args.sP,args.oT) 
lListOfTrainingDirectories = attribute.getListOfTrainingDirectoriesNames(args.dt,args.td,args.iT) 
lListOfTrainPredictDirectories = lListOfTrainingDirectories
lListOfTrainPredictDirectories.append(args.pd)
if(args.sequence == "dp"):

    experimentFolder = args.e
    dataFolder = args.td
    generatorsFolder = args.g
    commandList = []
    for directories in lListOfTrainPredictDirectories:
        commandList.append(["aGenForE.py","-e",experimentFolder,"-d",directories,"-g",args.g,"-run",args.run,"-sequence",args.sequence,'-tickSize',args.tickSize,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP])
    utility.runCommandList( commandList ,args)
    print dp.printGroupStatus() 

else:
        results = map(scriptWrapperForFeatureGeneration,lListOfTrainPredictDirectories)

utility.runCommand(["rGenForAllSubE.py","-e",args.e,"-a",algo,"-run",args.run,"-sequence",args.sequence,"-targetClass",args.targetClass,"-td",args.td , \
                    "-pd",args.pd,"-skipM",args.skipM,"-skipP",args.skipP,"-mpMearge",args.mpMearge,'-dt',args.dt, '-wt' , args.wt,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP],args.run,args.sequence)
if(args.sequence == "dp"):
    print dp.printGroupStatus()

if(args.sequence == "dp"):
    import runAllRScriptsForAllSubE
    attribute.initializeInstDetails(args.iT,args.sP,args.oT)
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
                        "-dt",args.dt ,"-sequence","serial","-run",args.run,"-mpMearge",args.mpMearge,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP],args.run,args.sequence)
    pass

dirName=os.path.dirname(args.e)
            
designFiles = utility.list_files(dirName+"/s/")    
# lets make a list of all the experiments for which we need to run cMatrixGen and trading
experimentNames = list()
for designFile in designFiles:
    experimentName = os.path.dirname(designFile)
    experimentNames.append(experimentName)

entrylist = ""
exitlist = ""
for i in range(55,70,1):
    for j in range(max(50,i-6),i+1,1):
        exitlist = exitlist + str(j) + ";"
        entrylist = entrylist + str(i) + ";"
exitlist = exitlist[:-1]
entrylist = entrylist[:-1]
def scriptWrapper(experimentName):
    if args.targetClass == "multinomial" :
#        utility.runCommand(["cMatrixGen.py","-d",args.pd,"-e",experimentName,"-a",algo],args.run,args.sequence)
        utility.runCommand(["./ob/quality/tradeE5.py","-e",experimentName,"-skipT",args.skipT,"-a",algo,"-entryCL","55;90;60;50","-exitCL","45;50;40;25","-orderQty","500",\
                            '-dt',args.dt,"-targetClass",args.targetClass,"-td",args.td , "-pd",args.pd,'-tickSize',args.tickSize,'-wt',args.wt,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP],args.run,args.sequence)
    else:
        utility.runCommand(["./ob/quality/tradeE7Optimized.py","-e",experimentName,"-skipT",args.skipT,"-a",algo,"-entryCL",entrylist,"-exitCL",exitlist,"-orderQty","300",                            '-dt',args.dt,"-targetClass",args.targetClass,"-td",args.td , "-pd",args.pd,'-tickSize',args.tickSize,'-wt',args.wt,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP],args.run,args.sequence)
        pass
        
if args.sequence == 'lp':
    # to run it in local parallel mode
    pool = multiprocessing.Pool() # this will return the number of CPU's
    results = pool.map(scriptWrapper,experimentNames)
else:
    results = map(scriptWrapper,experimentNames)

utility.runCommand(["accumulate_results.py","-e",args.e,"-a",algo,"-t",args.t,"-td","ob/data/ro/nsecur/20140602", "-dt" , str(args.dt) , '-nD' , str(args.nD) , "-m" ,"Nsecur With AmBmCmDandE\n" , "-f" , "1","-iT",args.iT,"-oT",args.oT,"-sP",args.sP],args.run,args.sequence)
if(args.sequence == "dp"):
    print dp.printGroupStatus()

#utility.runCommand(["src/rsTradeBuySellMixMatch.py","-e",args.e,"-skipT",args.skipT,"-a",algo,"-entryCL",entrylist,"-exitCL",exitlist,"-orderQty","300",'-dt',args.dt,"-targetClass",args.targetClass,"-td",args.td , "-pd",args.pd,'-tickSize',args.tickSize,'-wt',args.wt,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP,"-run",args.run,"-sequence",args.sequence],args.run,args.sequence)


#utility.runCommand(["accumulate_results.py","-e",args.e,"-a",algo,"-t",args.t,"-td",args.td, "-dt" , str(args.dt) , '-nD' , str(args.nD) , "-m" ,"NsecurWithABCDEAllSubCombinationforCompletionOf"+args.pd+"\n", "-f" , "1","-iT",args.iT,"-oT",args.oT,"-sP",args.sP],args.run,args.sequence)
