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
parser.add_argument('-d', required=True,help='Directory Folder')
parser.add_argument('-run', required=True,help='dry (only show dont execute) or real (show and execute)')
parser.add_argument('-sequence', required=True,help='lp (Local parallel) / dp (Distributed parallel) / serial')
parser.add_argument('-tickSize',required=True,help="Nse Currency = 25000 , Future Options = 5")
parser.add_argument('-nDays',required=True,help="Number of days present in the data set")
parser.add_argument('-nComputers',required=False,help="Number of computers at which task has to be run present in the data set")
parser.add_argument('-t',required=False,help="TransactionCost")
parser.add_argument('-targetType',required=False,help="list of 1,2,3,4,5,6 etc")
parser.add_argument('-orderQty',required=True,help="qty for whcih it is to be traded")
parser.add_argument('-iT',required=False,help='Instrument name')
parser.add_argument('-sP',required=False,help='Strike price of instrument')
parser.add_argument('-oT',required=False,help='Options Type')
args = parser.parse_args()

if(args.sequence == "dp"):
    import dp
attribute.initializeInstDetails(args.iT,args.sP,args.oT)  
commandList = []
allDataDirectories = attribute.getListOfTrainingDirectoriesNames( int(args.nDays) , args.d )
for directories in allDataDirectories:
    commandList.append(['src/aGenForEWithTargetOnly.py','-d',directories,'-g','ob/generators/','-run',args.run,'-sequence',args.sequence,'-tickSize',args.tickSize,'-e',args.e  ,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP])
if(args.sequence != "dp"):
    utility.runCommandList(commandList,args)
else:
    for chunkNum in range(0,len(commandList),int(args.nComputers)):
        lSubGenList = commandList[chunkNum:chunkNum+int(args.nComputers)]
        utility.runCommandList(lSubGenList,args)
        print dp.printGroupStatus() 

commandList = []
for directories in allDataDirectories:
    commandList.append(['src/targetVariableRun.py','-orderQty',args.orderQty,'-d',directories,'-tickSize',args.tickSize,'-targetType',args.targetType,'-e',args.e,'-run',args.run,'-sequence',args.sequence,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP])

if(args.sequence != "dp"):
    utility.runCommandList(commandList,args)
else:
    for chunkNum in range(0,len(commandList),int(args.nComputers)):
        lSubGenList = commandList[chunkNum:chunkNum+int(args.nComputers)]
        utility.runCommandList(lSubGenList,args)
        print dp.printGroupStatus() 

utility.runCommand(["src/accumulate_results_for_target_testing.py","-e",args.e,"-t",args.t,"-d",args.d, '-nD' , str(args.nDays) , "-m" , "ResultOfNewTargetVariableWhereWeForBuyWeCheckGreaterThanAskAndSellLessThanBid"],args.run,args.sequence)
