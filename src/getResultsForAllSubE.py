#!/usr/bin/python

import itertools, os,argparse, subprocess, multiprocessing
from configobj import ConfigObj
from datetime import datetime
import rCodeGen, utility

parser = argparse.ArgumentParser(description='This program will get results for all the subexperiments. \n\
An e.g. command line is \n\
getResultsForAllSubE.py -e ob/e/4/ -a glmnet -td ob/data/20140204 -pd ob/data/20140205 -g ob/generators/ -run real -runType serial',formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('-e', required=True,help='Directory of the experiment')
parser.add_argument('-a', required=True,help='Algorithm name.')
parser.add_argument('-td', required=True,help='Training directory')
parser.add_argument('-pd', required=True,help='Prediction directory')
parser.add_argument('-g', required=True,help='Generators directory')
parser.add_argument('-run', required=True,help='dry (only show dont execute) or real (show and execute)')
parser.add_argument('-runType', required=True,help='lp (Local parallel) / dp (Distributed parallel) / serial')
args = parser.parse_args()

config = ConfigObj(args.e+"/design.ini")
features = config["features"]
i = 1

algo = rCodeGen.getAlgoName(args)

utility.runProgram(["aGenForE.py","-e",args.e,"-d",args.td,"-g",args.g,"-run",args.run],args)
utility.runProgram(["aGenForE.py","-e",args.e,"-d",args.pd,"-g",args.g,"-run",args.run],args)
utility.runProgram(["genAllRScriptsForAllSubE.py","-e",args.e,"-a",algo,"-run",args.run],args)
utility.runProgram(["runAllRScriptsForAllSubE.py","-td",args.td,"-pd",args.pd,"-e",args.e,"-a",algo,"-runType",args.runType,"-run",args.run],args)

dirName=os.path.dirname(args.e)
            
designFiles = utility.list_files(dirName+"/s/")    
# lets make a list of all the experiments for which we need to run cMatrixGen and trading
experimentNames = list()
for designFile in designFiles:
    experimentName = os.path.dirname(designFile)
    experimentNames.append(experimentName)

def scriptWrapper(experimentName):
    utility.runProgram(["cMatrixGen.py","-d",args.pd,"-e",experimentName,"-a",algo],args)
    utility.runProgram(["./ob/quality/tradeE1.py","-d",args.pd,"-e",experimentName,"-a",algo,"-entryCL",".55","-exitCL",".45"],args)

if args.runType == 'lp':
    # to run it in local parallel mode
    pool = multiprocessing.Pool() # this will return the number of CPU's
    results = pool.map(scriptWrapper,experimentNames)
elif args.runType == 'dp':
    import dp
    for experimentName in experimentNames:
        dp.runProgram.delay(["cMatrixGen.py","-d",args.pd,"-e",experimentName,"-a",algo],args.run)
        dp.runProgram.delay(["./ob/quality/tradeE1.py","-d",args.pd,"-e",experimentName,"-a",algo,"-entryCL",".55","-exitCL",".45"],args.run)
else:
    results = map(scriptWrapper,experimentNames)

