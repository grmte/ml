#!/usr/bin/python

from __future__ import division
from __future__ import print_function
import os, sys, argparse
from configobj import ConfigObj
from itertools import islice
from datetime import datetime

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
parser.add_argument('-dt',required=True,help="Number of days it was trained")  
parser.add_argument('-targetClass',required=False,help="For which model was used ; binomial(target takes only true and false) / multinomial (target values takes more than 2 values)")
parser.add_argument('-tickSize',required=True,help="Nse Currency = 25000 , Future Options = 5")
parser.add_argument('-wt',required=False,help="default/exp , weight type to be given to different days")
parser.add_argument('-iT',required=False,help='Instrument name')
parser.add_argument('-sP',required=False,help='Strike price of instrument')
parser.add_argument('-oT',required=False,help='Options Type')
parser.add_argument('-t',required=False,help='Transaction Cost')
parser.add_argument('-double',required=False,help='Double training of in model')
parser.add_argument('-treeType',required=False,help="Tree read for trade engine")
parser.add_argument('-nodes',required=False,help='Nodes specified')
args = parser.parse_args()

sys.path.append("./src/")
sys.path.append("./ob/generators/")
sys.path.append("./ob/quality/tradeE15/")
import dataFile, colNumberOfData, common
import dd , reading_tree , trade
import attribute
attribute.initializeInstDetails(args.iT,args.sP,args.oT)
if args.skipT == None:
    args.skipT = "no"
# if args.pT == None:
#     args.pT = "no"
if args.targetClass == None:
    args.targetClass = "binomial"
if args.wt == None:
    args.wt = "default"
if args.nodes == None:
    args.nodes = ""               
absPathOfExperimentName = os.path.abspath(args.e)

if 'nsecur' in absPathOfExperimentName:
    pathAfterE = absPathOfExperimentName[absPathOfExperimentName.index("/nsecur/")+8:]
    if args.t ==None:
        dd.gTransactionCost = 0.000015
        dd.currencyDivisor = 10000
elif 'nsefut' in absPathOfExperimentName:
    pathAfterE = absPathOfExperimentName[absPathOfExperimentName.index("/nsefut/")+8:]
    if args.t == None:
        dd.gTransactionCost = 0.00015
        dd.currencyDivisor = 100
elif 'nseopt' in absPathOfExperimentName:
    pathAfterE = absPathOfExperimentName[absPathOfExperimentName.index("/nseopt/")+8:]
    dd.gTransactionCost = args.t
    dd.currencyDivisor = 0
    print("Please specify the transaction cost and currency divisor for options and remove os.exit(-1) and rerun it")
    os._exit(-1)
if "/" in pathAfterE:
    mainExperimentName = pathAfterE[:pathAfterE.index("/")]
else:
    mainExperimentName = pathAfterE
    
experimentName = os.path.basename(absPathOfExperimentName)
dd.gTickSize = int(args.tickSize)
dd.gMaxQty = int(args.orderQty)

tStart = datetime.now()
dirName = args.pd.replace('/ro/','/rs/')
checkAllFilesAreExistOrNot = 'false'

lWFDirName = args.pd.replace('/ro/','/wf/')

lEntryClList = args.entryCL.split(";")
lExitClList = args.exitCL.split(";")
if len(lEntryClList)!= len(lExitClList):
    print("Len of entry and exit list does match. Entry List length = " , len(lEntryClList) , " and ExitCL List length = " , len(lExitClList))
    os._exit(-1)
lengthOfList = len(lEntryClList)
if len(args.nodes) == 0:
    for target in ['buy','sell']:
        lTreeFileName = args.e+"/"+args.a+ target+'-td.' + os.path.basename(os.path.abspath(args.td)) + '-dt.' + args.dt + attribute.generateExtension() +".tree" + args.treeType
        dd.gGlobalTree[target],lVariable = reading_tree.reading_tree(lTreeFileName,args.treeType)
        dd.gTreeVariablesPresent = dd.gTreeVariablesPresent + lVariable
        for entry,exit in zip(lEntryClList,lExitClList):
            if entry not in dd.gFinalCondition[target]:
                dd.gFinalCondition[target][entry] = reading_tree.traverse_tree(1,args.treeType,float(entry),dd.gGlobalTree[target],dd.gGlobalTree[target])
            if exit not in dd.gFinalCondition[target]:
                dd.gFinalCondition[target][exit] = reading_tree.traverse_tree(1,args.treeType,float(entry),dd.gGlobalTree[target],dd.gGlobalTree[target])
else:
    for target in ['buy','sell']:
        lTreeFileName = args.e+"/"+args.a+ target+'-td.' + os.path.basename(os.path.abspath(args.td)) + '-dt.' + args.dt + attribute.generateExtension() +".tree" + args.treeType
        dd.gGlobalTree[target],lVariable = reading_tree.reading_tree(lTreeFileName,args.treeType)
        dd.gTreeVariablesPresent = dd.gTreeVariablesPresent + lVariable
        nodes = args.nodes.split(";")
        dd.gFinalCondition[target]['nodes'] = reading_tree.traverse_nodes(args.treeType,nodes,dd.gGlobalTree[target])
    
config = ConfigObj(args.e+"/design1.ini")
    
for variable in dd.gTreeVariablesPresent:
    if variable.lower()=="buyprob":
        predictedBuyValuesFileName = lWFDirName+"/p/"+mainExperimentName+"/"+args.a + 'buy' + '-td.' + os.path.basename(os.path.abspath(args.td)) + '-dt.' + \
                                args.dt + '-targetClass.' + args.targetClass + '-f.' + experimentName + "-wt." + args.wt+ attribute.generateExtension() + ".predictions"
        dd.gFileObjectsOfVariablesPresent.append(open(predictedBuyValuesFileName,'r'))
    elif variable.lower()=="sellprob":
        predictedSellValuesFileName = lWFDirName+"/p/"+mainExperimentName+"/"+args.a + 'sell' + '-td.' + os.path.basename(os.path.abspath(args.td)) + '-dt.' +\
                                    args.dt + '-targetClass.' + args.targetClass + '-f.' + experimentName + "-wt." + args.wt+ attribute.generateExtension() + ".predictions"
        dd.gFileObjectsOfVariablesPresent.append(open(predictedSellValuesFileName,'r'))
    elif variable in config['features-buy']:
        lFaetureFileName = lWFDirName+"/f/"+config['features-buy'][variable]+".feature"
        dd.gFileObjectsOfVariablesPresent.append(open(lFaetureFileName,'r'))
    elif variable in config['features-sell']:
        lFaetureFileName = lWFDirName+"/f/"+config['features-sell'][variable]+".feature"
        dd.gFileObjectsOfVariablesPresent.append(open(lFaetureFileName,'r'))       
    else:
        print("Cannot match any key for variable name " ,variable," found in the tree in design1.ini" )    
    
lMinOfExitCl = 9999.000
fileNameList = []
finalEntryClList = []
finalExitClList = []
lengthOfFinalList = 0
for indexOfCL in range(lengthOfList):
    if args.double:
        lInitialFileName = args.a + '-td.' + os.path.basename(os.path.abspath(args.td)) + \
                       '-dt.' + args.dt + '-targetClass.' + args.targetClass + '-f.' + experimentName + "-wt." + args.wt+ attribute.generateExtension() + \
                       '-l.'+lEntryClList[indexOfCL]+"-"+lExitClList[indexOfCL] + "-tq." + args.orderQty + "-te.7double" 
    else:
        lInitialFileName = args.a + '-td.' + os.path.basename(os.path.abspath(args.td)) + \
                       '-dt.' + args.dt + '-targetClass.' + args.targetClass + '-f.' + experimentName + "-wt." + args.wt+ attribute.generateExtension() + \
                       '-l.'+lEntryClList[indexOfCL]+"-"+lExitClList[indexOfCL] + "-tq." + args.orderQty + "-te.7" 
    fileName = dirName + "/r/" + mainExperimentName + "/" + lInitialFileName+".result"
    if os.path.isfile(fileName) and args.skipT.lower() == "yes":
        print("Trade results file " + fileName + "Already exist. Not regenerating it. If you want to rerun it by making -skipT = no ")
    else: 
        checkAllFilesAreExistOrNot = 'true'
        print("Trade results file " + fileName + " Does not exist.")
        fileNameList.append(fileName)
        lEntryCL = float("." + lEntryClList[indexOfCL])
        lExitCL = float("." + lExitClList[indexOfCL])
        if lExitCL < lMinOfExitCl :
            lMinOfExitCl = lExitCL
        finalEntryClList.append(lEntryCL)
        finalExitClList.append(lExitCL)
        lengthOfFinalList = lengthOfFinalList + 1

print("Number of File to be run for ",lengthOfFinalList)
if checkAllFilesAreExistOrNot == 'true':
    
#    if os.path.isfile(predictedBuyValuesFileName) and os.path.isfile(predictedSellValuesFileName):
        print ("\nRunning the simulated trading program")
        dd.g_quantity_adjustment_list_for_sell = {}
        dd.g_quantity_adjustment_list_for_buy = {}

        dataFileName = dataFile.getFileNameFromCommandLineParam(args.pd)
        
        dataFileObject =  open(dataFileName,"r")
        
        print("Data file Used :- " ,dataFileName)
        #print("Buy Predict file Used :- ",predictedBuyValuesFileName)
        #print("Sell Predict file used :- ", predictedSellValuesFileName)
        lObjectList = trade.getDataFileAndPredictionsIntoObjectList(dataFileObject,dd.gFileObjectsOfVariablesPresent,lMinOfExitCl)
        
        print("Length of list formed " , len(lObjectList) , " Min of predictions taken :- ", lMinOfExitCl)
        tEnd = datetime.now()
        print("Time taken to read data and prediction file is " + str(tEnd - tStart))
        
        for lIndexOfFiles in range(lengthOfFinalList):
            trade.doTrade(fileNameList[lIndexOfFiles], finalEntryClList[lIndexOfFiles], finalExitClList[lIndexOfFiles], lObjectList)
#                 if args.pT.lower() == "yes":
#                     print("Need to print logs")
        
        tEnd = datetime.now()
        print("Time taken to for complete run " + str(tEnd - tStart))
        '''
    else:
        print (predictedBuyValuesFileName,predictedSellValuesFileName)
        print ("Features or prediction file are not yet generated")
        '''

