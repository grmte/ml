#!/usr/bin/python
import argparse,os,multiprocessing
from datetime import timedelta
from datetime import datetime
import utility
import attribute

parser = argparse.ArgumentParser(description='This program will do the 5 steps necessary to get the results for an experiment. \n \
The 5 steps are: \n \
1. Attribute generation  \n \
2. R code generation  \n \
3. R code running.  \n \
4. CMatrix generation  \n \
5. Doing the trading.   \n \
An e.g. command line >rsGenForE.py -e ob/e/8/ -td ob/data/ro/20140204/ -pd ob/data/ro/20140205/ -g ob/generators/ -run dry -sequence serial -targetClass multinomial -skipM Yes -skipP Yes', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-e', required=True,help='Directory of the experiment')
parser.add_argument('-a', required=False,help='Algorithm name. This is optional and defaults to glmnet.')
parser.add_argument('-pType', required=True,help='Same day prediction or next day prediction')
parser.add_argument('-pd', required=True,help='Prediction directory')
parser.add_argument('-dt',required=False,help='Number of days after start training day specified . Defaults to 1 ')
parser.add_argument('-g', required=True,help='Generators directory')
parser.add_argument('-run', required=True,help='dry or real')
parser.add_argument('-sequence', required=True,help='dp/lp/serial')
parser.add_argument('-targetClass',required=True,help="binomial(target takes only true and false) / multinomial (target values takes more than 2 values)")
parser.add_argument('-skipM',required=False,help="yes or no , If you want to regenerate already generated algorithm model file then make this value No . Defaults to yes")
parser.add_argument('-skipP',required=False,help="yes or no , If you want to regenerate already generated algorithm prediction file then make this value No. Defaults to yes")
parser.add_argument('-tickSize',required=True,help="Nse Currency = 25000 , Future Options = 5")
parser.add_argument('-wt',required=False,help="default/exp , weight type to be given to different days")
args = parser.parse_args()

if args.skipM == None:
    args.skipM = "yes"
if args.skipP == None:
    args.skipP = "yes"
if args.dt == None:
    args.dt = "1"
if args.wt == None:
    args.wt = "default"

if args.a is not None:
    algo = args.a
else:
    algo = 'glmnet'

if args.targetClass == None:
    args.targetClass = "binomial"
    print "Since no class of target variable is specified so taking binomial class of target variable"

def scriptWrapperForFeatureGeneration(trainingDirectory):
    utility.runCommand(["aGenForE.py","-e",args.e,"-d",trainingDirectory,"-g",args.g,"-run",args.run,"-sequence",args.sequence,'-tickSize',args.tickSize],args.run,args.sequence)

trainingDirectory = attribute.getTrainDirFromPredictDir( args.dt , args.pd , args.pType )        
lListOfTrainingDirectories = attribute.getListOfTrainingDirectoriesNames(args.dt,trainingDirectory) 
lListOfTrainPredictDirectories = lListOfTrainingDirectories
lListOfTrainPredictDirectories.append(args.pd)
results = map(scriptWrapperForFeatureGeneration,lListOfTrainPredictDirectories)

utility.runCommand(["rGenForE.py","-e",args.e,"-a",algo,"-sequence",args.sequence,"-targetClass",args.targetClass,"-skipM",args.skipM,\
                    '-dt',args.dt,'-pd',args.pd,"-td",trainingDirectory,"-skipP",args.skipP, '-wt' , args.wt],args.run,args.sequence)
utility.runCommand(["runAllRScriptsForE.py","-td",trainingDirectory,"-pd",args.pd,"-dt",args.dt,"-e",args.e,"-a",algo,"-run",args.run,\
                     '-wt' , args.wt,"-sequence",args.sequence],args.run,args.sequence)
utility.runCommand(["./ob/quality/tradeE6.py","-e",args.e,"-a",algo,"-entryCL","90;75;60;55;55;65;65","-exitCL","50;50;50;45;50;50;45","-orderQty","50",\
                                        '-dt',args.dt,"-targetClass",args.targetClass,"-td",trainingDirectory , "-pd",args.pd,'-tickSize',args.tickSize,'-wt',args.wt],args.run,args.sequence)

if args.pType.lower()== "next":
    nD = int(args.dt) + 1
    utility.runCommand(["accumulate_results.py","-e",args.e,"-dt",args.dt,"-nD",str(nD),"-td",trainingDirectory,"-pd",args.pd, "-a",algo,"-m","PythonSimResultsForModelToBeUsedNextDayAndTodaysSimRunResults" ,"-f","1","-t","0.000015"],args.run,args.sequence)
