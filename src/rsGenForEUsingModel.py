#!/usr/bin/python                                                                                                                                                                                                                           
import argparse, glob
import utility
import multiprocessing  # read https://medium.com/building-things-on-the-internet/40e9b2b36148                                                                                                                                              
from functools import partial
import os
import attribute

parser = argparse.ArgumentParser(description='This program will run mGenForE.py and pGenForE.py. An e.g. command line is \n\                                                                                                               rGenForE.py -e ob/e/9.1/ -a glmnet -sequence serial -targetClass multinomial -skipM Yes -pd ob/data/ro/20140205 -skipP Yes', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-e', required=True,help='Directory of the experiment')
parser.add_argument('-a', required=False,help='Algorithm name')
parser.add_argument('-run', required=False,help='dry or real')
parser.add_argument('-sequence', required=False,help='lp / dp / serial')
parser.add_argument('-targetClass',required=True,help="binomial(target takes only true and false) / multinomial (target values takes more than 2 values)")
parser.add_argument('-skipT',required=False,help="yes or no , If you want to regenerated trade files then make this value no.  Defaults to yes")
parser.add_argument('-skipM',required=False,help="yes or no , If you want to regenerate already generated algorithm model file then make this value No")
parser.add_argument('-skipP',required=False,help="yes or no , If you want to regenerate already generated algorithm prediction file then make this value No")
parser.add_argument('-td',required=True,help='Training Directory')
parser.add_argument('-nDays',required=True,help="Number of days present in the data set")
parser.add_argument('-dt',required=False,help='No of day from start for which it is to be trained ')
parser.add_argument('-wt',required=False,help="default/exp , weight type to be given to different days")
parser.add_argument('-tickSize',required=True,help="Nse Currency = 25000 , Future Options = 5")
parser.add_argument('-t',required=True,help="TransactionCost")
parser.add_argument('-iT',required=False,help='Instrument name')
parser.add_argument('-sP',required=False,help='Strike price of instrument')
parser.add_argument('-oT',required=False,help='Options Type')
parser.add_argument("-orderQty",required=True,help="Order qty ")
parser.add_argument("-nComputers",required=False,help="nComputers")
args = parser.parse_args()

if args.skipM == None:
    args.skipM = "yes"
if args.skipP == None:
    args.skipP = "yes"
if args.dt == None:
    args.dt = "1"
if args.wt == None:
    args.wt = "default"
if(args.nComputers == None):
    args.nComputers = 1
if(args.sequence == "dp"):
    import dp
if args.a is not None:
    allAlgos = [args.a]
else:
    allAlgos = ['logitr','glmnet','randomForest']
attribute.initializeInstDetails(args.iT,args.sP,args.oT)
allDataDirectories = attribute.getListOfTrainingDirectoriesNames( int(args.nDays) , args.td ,args.iT)
entrylist = ""
exitlist = ""
for i in range(50,70,1):
    for j in range(45,i,1):
        exitlist = exitlist + str(j) + ";"
        entrylist = entrylist + str(i) + ";"
exitlist = exitlist[:-1]
entrylist = entrylist[:-1]
lRCodeGenCommandList = []
lPGenRCodeList = []
lTradingCommandList = []
lExperimentFolderName = args.e
for algo in allAlgos:
    for i in range(len(allDataDirectories)):
        predictionDirAfterLastTD = allDataDirectories[i]
        lRCodeGenCommandList.append((["pRGenForE.py","-e",args.e,"-a",algo,"-skipP",args.skipP,"-td",args.td , "-pd" , predictionDirAfterLastTD , "-dt" , args.dt ,\
                         "-targetClass" , args.targetClass , '-wt' , args.wt ,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP]))
        scriptName=lExperimentFolderName+"/predict" + algo + "-td." + os.path.basename(os.path.abspath(args.td)) + "-dt." + args.dt +"-pd."  +\
                    os.path.basename(os.path.abspath(predictionDirAfterLastTD)) + "-wt." + args.wt  + attribute.generateExtension() +".r"
        dirName = predictionDirAfterLastTD.replace('/ro/','/wf/')
        lPGenRCodeList.append([scriptName,"-d",dirName])
        lTradingCommandList.append(["./ob/quality/tradeE7Optimized.py","-e",lExperimentFolderName,"-skipT",args.skipT,"-a",algo,"-entryCL",entrylist,"-exitCL",\
                exitlist,"-orderQty",args.orderQty,'-dt',args.dt,"-targetClass",args.targetClass,"-td",args.td , "-pd",predictionDirAfterLastTD,\
                '-tickSize',args.tickSize,'-wt',args.wt,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP])
if args.sequence == "dp":
    totalModelsWhichCanBeScheduled = int(args.nComputers)
    for chunkNum in range(0,len(lRCodeGenCommandList),totalModelsWhichCanBeScheduled):
        l_sub_RCodeGenList = lRCodeGenCommandList[chunkNum:chunkNum+totalModelsWhichCanBeScheduled]
        utility.runCommandList(l_sub_RCodeGenList,args)
        print dp.printGroupStatus()
    for chunkNum in range(0,len(lPGenRCodeList),totalModelsWhichCanBeScheduled):
        l_sub_pGenRCodeGenList = lPGenRCodeList[chunkNum:chunkNum+totalModelsWhichCanBeScheduled]
        utility.runCommandList(l_sub_pGenRCodeGenList,args)
        print dp.printGroupStatus()
    for chunkNum in range(0,len(lTradingCommandList),totalModelsWhichCanBeScheduled):
        l_sub_TradingCommandList = lTradingCommandList[chunkNum:chunkNum+totalModelsWhichCanBeScheduled]
        utility.runCommandList(l_sub_TradingCommandList,args)
        print dp.printGroupStatus()
else:
    for chunkNum in lRCodeGenCommandList:
        utility.runCommand(chunkNum,args.run,args.sequence)
    for chunkNum in lPGenRCodeList:
        utility.runCommand(chunkNum,args.run,args.sequence)
    for chunkNum in lTradingCommandList:
        utility.runCommand(chunkNum,args.run,args.sequence)


#utility.runCommandList(lRCodeGenCommandList,args)
#print dp.printGroupStatus()
#utility.runCommandList(lPGenRCodeList,args)
#print dp.printGroupStatus()
#utility.runCommandList(lTradingCommandList,args)
#print dp.printGroupStatus()
args.dt = 1
utility.runCommand(["accumulate_results.py","-e",args.e,"-a",algo,"-t",args.t,"-td",args.td, "-dt" , str(args.dt) , '-nD' , str(args.nDays) , "-m" ,"ICICI_BANK_experiments" , "-f" , "1","-iT",args.iT,"-oT",args.oT,"-sP",args.sP],args.run,args.sequence)
