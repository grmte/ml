#!/usr/bin/python

import itertools, os,argparse, subprocess, multiprocessing
from configobj import ConfigObj
from datetime import datetime
import rCodeGen, utility
import attribute
import aGenForE

parser = argparse.ArgumentParser(description='This program will do trades to measure the quality of the experiment.\n\
 An e.g. command line is tradeE5.py -d ob/data/20140207/ -e ob/e/1 -a logitr -entryCL 0.90 -exitCL .55 -orderQty 500', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-e', required=True,help='Directory of the experiment or sub experiment e/10/s/3c/ABC')
parser.add_argument('-a', required=True,help='Algorithm name')
parser.add_argument('-entryCL', required=True,help='Percentage of the confidence level used to enter the trades')
parser.add_argument('-exitCL', required=True,help='Percentage of the confidence level used to exit the trades')
parser.add_argument('-orderQty',required=True,help='Order Quantity with which we trade')
parser.add_argument("-skipT",required=False,help="Skip creating trade files if already generated")
parser.add_argument('-td', required=True,help='Directory of the training data file')
parser.add_argument('-pd', required=True,help='Directory of the prediction data file')
parser.add_argument('-dt',required=False,help="Number of days it was trained")  
parser.add_argument('-targetClass',required=False,help="For which model was used ; binomial(target takes only true and false) / multinomial (target values takes more than 2 values)")
parser.add_argument('-tickSize',required=True,help="Nse Currency = 25000 , Future Options = 5")
parser.add_argument('-wt',required=False,help="default/exp , weight type to be given to different days")
parser.add_argument('-run', required=True,help='dry (only show dont execute) or real (show and execute)')
parser.add_argument('-sequence', required=True,help='lp (Local parallel) / dp (Distributed parallel) / serial')
parser.add_argument('-iT',required=False,help='Instrument name')
parser.add_argument('-sP',required=False,help='Strike price of instrument')
parser.add_argument('-oT',required=False,help='Options Type')
args = parser.parse_args()

attribute.initializeInstDetails(args.iT,args.sP,args.oT)
if args.skipT == None:
    args.skipT = "no"
if args.dt == None:
    args.dt = "1"
if args.targetClass == None:
    args.targetClass = "binomial"
if args.wt == None:
    args.wt = "default"
                    
                    
if(args.sequence == "dp"):
    import dp


dirName=os.path.dirname(args.e)
            
designFiles = utility.list_files(dirName+"/s/")    
# lets make a list of all the experiments for which we need to run cMatrixGen and trading
experimentNames = list()
for designFile in designFiles:
    experimentName = os.path.dirname(designFile)
    experimentNames.append(experimentName)

buyExperimentIndex = 0
sellExperimentIndex = 0
experimentNamesIndex = len(experimentNames)
buyExperimentList = []
sellExperimentList = []
for buyExperimentIndex in range(experimentNamesIndex):
    for sellExperimentIndex in range(experimentNamesIndex):
        if buyExperimentIndex == sellExperimentIndex:
            continue
        buyExperimentList.append(experimentNames[buyExperimentIndex])
        sellExperimentList.append(experimentNames[sellExperimentIndex])

buyListLength = len(buyExperimentList)
print "List of Sub Experiments " , buyListLength

def scriptWrapper(index):

     utility.runCommand(["./ob/quality/tradeE7BuySellMixMatch.py","-es",sellExperimentList[index],"-eb",buyExperimentList[index],"-skipT",args.skipT,"-a",args.a,"-entryCL",args.entryCL,"-exitCL",args.exitCL,"-orderQty",args.orderQty,'-dt',args.dt,"-targetClass",args.targetClass,"-td",args.td ,"-pd",args.pd,'-tickSize',args.tickSize,'-wt',args.wt,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP],args.run,args.sequence)
        

if(args.sequence == "dp"):
    import dp

    lTradingCommandList= []

    for index in range(buyListLength):
        lTradingCommandList.append(["./ob/quality/tradeE7BuySellMixMatch.py","-es",sellExperimentList[index],"-eb",buyExperimentList[index],"-skipT",args.skipT,"-a",args.a,"-entryCL",args.entryCL,"-exitCL",args.exitCL,"-orderQty",args.orderQty,'-dt',args.dt,"-targetClass",args.targetClass,"-td",args.td ,"-pd",args.pd,'-tickSize',args.tickSize,'-wt',args.wt,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP])

    utility.runCommandList(lTradingCommandList,args)
    print dp.printGroupStatus()
else:
    buyIndexList = range(buyListLength)
    if args.sequence == 'lp':
        # to run it in local parallel mode
        pool = multiprocessing.Pool() # this will return the number of CPU's
        results = pool.map(scriptWrapper,buyIndexList)
    else:
        results = map(scriptWrapper,buyIndexList)

