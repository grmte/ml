#!/usr/bin/python

import itertools, os,argparse, subprocess, multiprocessing
from configobj import ConfigObj
from datetime import datetime
import rCodeGen, utility


parser = argparse.ArgumentParser(description='This program will get results for all the subexperiments. \n\
An e.g. command line is \n\
rsGenForAllSubE.py -e ob/e/4/ -a glmnet -td ob/data/ro/20140204 -pd ob/data/ro/20140205 -g ob/generators/ -run real -sequence serial',formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('-e', required=True,help='Directory of the experiment')
parser.add_argument('-a', required=True,help='Algorithm name.')
parser.add_argument('-td', required=True,help='Training directory')
parser.add_argument('-pd', required=True,help='Prediction directory')
parser.add_argument('-g', required=True,help='Generators directory')
parser.add_argument('-run', required=True,help='dry (only show dont execute) or real (show and execute)')
parser.add_argument('-sequence', required=True,help='lp (Local parallel) / dp (Distributed parallel) / serial')
args = parser.parse_args()

if(args.sequence == "dp"):
    import dp

config = ConfigObj(args.e+"/design.ini")
features = config["features"]

algo = rCodeGen.getAlgoName(args)

if(args.sequence == "dp"):
    import aGenForE
    experimentFolder = args.e
    dataFolder = args.td
    generatorsFolder = args.g
    commandList = aGenForE.getCommandList(experimentFolder,dataFolder,generatorsFolder)
    commandList.extend(aGenForE.getCommandList(experimentFolder,args.pd,generatorsFolder))
    # Seperate into 2 different list one for aGen and another for operateOnAttribute
    import attribute

    aGenList = []
    attribute.getGenerationCommands(commandList,aGenList)
    #utility.runCommandList(aGenList,args)
    #dp.printGroupStatus()

    operateOnAttributeList = []
    attribute.getOperationCommands(commandList,operateOnAttributeList)
    operateOnAttributeListAsPerPriority = attribute.getOperationCommandsInPriority(operateOnAttributeList)
    for i in operateOnAttributeListAsPerPriority:
        utility.runCommand(i,args.run,args.sequence)
        dp.printGroupStatus() 


else:
    utility.runCommand(["aGenForE.py","-e",args.e,"-d",args.td,"-g",args.g,"-run",args.run,"-sequence",args.sequence],args.run,args.sequence)
    utility.runCommand(["aGenForE.py","-e",args.e,"-d",args.pd,"-g",args.g,"-run",args.run,"-sequence",args.sequence],args.run,args.sequence)


utility.runCommand(["rGenForAllSubE.py","-e",args.e,"-a",algo,"-run",args.run,"-sequence",args.sequence],args.run,args.sequence)
if(args.sequence == "dp"):
    print dp.printGroupStatus()

if(args.sequence == "dp"):
    import runAllRScriptsForAllSubE
    commandList = runAllRScriptsForAllSubE.getTrainCommandList(args.e,args.a,args.td)
    utility.runCommandList(commandList,args)
    print dp.printGroupStatus()

    commandList = runAllRScriptsForAllSubE.getPredictCommandList(args.e,args.a,args.pd)
    utility.runCommandList(commandList,args)
    print dp.printGroupStatus()

else:
    utility.runCommand(["runAllRScriptsForAllSubE.py","-td",args.td,"-pd",args.pd,"-e",args.e,"-a",algo,"-sequence",args.sequence,"-run",args.run],args.run,args.sequence)


dirName=os.path.dirname(args.e)
            
designFiles = utility.list_files(dirName+"/s/")    
# lets make a list of all the experiments for which we need to run cMatrixGen and trading
experimentNames = list()
for designFile in designFiles:
    experimentName = os.path.dirname(designFile)
    experimentNames.append(experimentName)

def scriptWrapper(experimentName):
    utility.runCommand(["cMatrixGen.py","-d",args.pd,"-e",experimentName,"-a",algo,"-sequence",args.sequence],args.run,args.sequence)
    utility.runCommand(["./ob/quality/tradeE1.py","-d",args.pd,"-e",experimentName,"-a",algo,"-entryCL",".55","-exitCL",".45","-sequence",args.sequence],args.run,args.sequence)

if args.sequence == 'lp':
    # to run it in local parallel mode
    pool = multiprocessing.Pool() # this will return the number of CPU's
    results = pool.map(scriptWrapper,experimentNames)
else:
    results = map(scriptWrapper,experimentNames)

if(args.sequence == "dp"):
    print dp.printGroupStatus()
