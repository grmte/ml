#!/usr/bin/python
import argparse,os,multiprocessing
import writeOutputToRemotePC
from datetime import timedelta
from datetime import datetime
import utility
import attribute,commands

parser = argparse.ArgumentParser(description='This program will do the 5 steps necessary to get the results for an experiment. \n \
The 5 steps are: \n \
1. Attribute generation  \n \
2. R code generation  \n \
3. R code running.  \n \
4. CMatrix generation  \n \
5. Doing the trading.   \n \
An example of command line :-\
src/rsGenForLiveDailyModelCalculation.py -e ob/e/nsecur/live_experiment/ -pType same -dt 10 -pd ob/data/ro/nsecur/20140620/ \
-targetClass binomial -wt default -run real -sequence lp -g ob/generators/ -tickSize 25000 -instrGroups "1;2;3;4;5" -nF 5 -orderQty 500 -entryCL "57;57;58;58;60;60;65;65" -exitCL \
"45;50;45;50;45;50;45;50"', formatter_class=argparse.RawTextHelpFormatter)
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
parser.add_argument('-instrGroups',required=True,help="instruments groups used in live file")
parser.add_argument('-nF',required=True,help="number of features")
parser.add_argument('-entryCL',required=True,help="Trade open position entry point separated by semicolon")
parser.add_argument('-exitCL',required=True,help="Trade close position point separated by semicolon")
parser.add_argument('-orderQty',required=True,help="Qty with which you want to trade")
args = parser.parse_args()


current_number_of_features_used = int(args.nF)
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
utility.runCommand(["./ob/quality/tradeE7.py","-e",args.e,"-a",algo,"-entryCL",args.entryCL,"-exitCL",args.exitCL,"-orderQty",args.orderQty,\
                                        '-dt',args.dt,"-targetClass",args.targetClass,"-td",trainingDirectory , "-pd",args.pd,'-tickSize',args.tickSize,'-wt',args.wt],args.run,args.sequence)

instrGroupList = args.instrGroups.split(";")
if args.pType.lower()== "same":
    modelValueFileName = args.e+'/'+algo+ '-td.' + os.path.basename(os.path.abspath(trainingDirectory)) + '-dt.' + args.dt + '-targetClass.' + \
                     args.targetClass + "-wt." + args.wt +'.coef'    
    modelFp = open(modelValueFileName,"r")
    lines = modelFp.readlines()
    modelIniFile = args.e + '/' + "model-parameters.ini"
    modelIniFP = open(modelIniFile,"w")
    writeOutputToRemotePC.clear_file_from_remote_PC('/home/', "model-parameters.ini", ('1.ps.eo.spalgo.com', 'root', 'omshriganeshaya'))
    for n in instrGroupList:
        startString = "[ml-instr-group" + n + "]"
        modelIniFP.write("%s\n" %startString)
        try:
            writeOutputToRemotePC.main(startString, '/home/', "model-parameters.ini", ('1.ps.eo.spalgo.com', 'root', 'omshriganeshaya'))
        except:
            pass
        for l in lines:
            line_to_print = l.strip()
            if "vector-of-alphas-" in l:
                splitted_line = l.split(",")
                length_of_vector = len(splitted_line)
                for i in range(length_of_vector,current_number_of_features_used+1):
                    line_to_print = line_to_print + "0,"
            modelIniFP.write("    %s\n" %line_to_print)
            try:
                line_to_print = "    " + line_to_print
                writeOutputToRemotePC.main(line_to_print, '/home/', "model-parameters.ini", ('1.ps.eo.spalgo.com', 'root', 'omshriganeshaya'))
            except:
                pass
    
if args.pType.lower()== "next":
    nD = int(args.dt) + 1
    utility.runCommand(["accumulate_results.py","-e",args.e,"-dt",args.dt,"-nD",str(nD),"-td",trainingDirectory,"-pd",args.pd, "-a",algo,"-m",\
                        "PythonSimResultsForModelToBeUsedNextDayAndTodaysSimRunResults" ,"-f","1","-t","0.000015"],args.run,args.sequence)
    

