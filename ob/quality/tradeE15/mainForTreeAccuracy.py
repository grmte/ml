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
parser.add_argument("-skipT",required=False,help="Skip creating trade files if already generated")
parser.add_argument('-td', required=False,help='Directory of the training data file')
parser.add_argument('-pd', required=True,help='Directory of the prediction data file')
parser.add_argument('-dt',required=True,help="Number of days it was trained")  
parser.add_argument('-targetClass',required=False,help="For which model was used ; binomial(target takes only true and false) / multinomial (target values takes more than 2 values)")
parser.add_argument('-wt',required=False,help="default/exp , weight type to be given to different days")
parser.add_argument('-iT',required=False,help='Instrument name')
parser.add_argument('-sP',required=False,help='Strike price of instrument')
parser.add_argument('-oT',required=False,help='Options Type')
parser.add_argument('-t',required=False,help='Transaction Cost')
parser.add_argument('-double',required=False,help='Double training of in model')
parser.add_argument('-treeType',required=False,help="Tree read for trade engine")
parser.add_argument('-nodes',required=False,help='Nodes specified')
parser.add_argument('-nPD',required=False,help='Number of prediction days for which tree is to be made')
args = parser.parse_args()

sys.path.append("./src/")
sys.path.append("./ob/generators/")
sys.path.append("./ob/quality/tradeE15/")
import dataFile, colNumberOfData, common
import dd , reading_tree , treeAccuracyOnPredictionDay
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
if args.nPD == None:
    args.nPD = "0"

         
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

tStart = datetime.now()

if len(args.nodes) == 0:
    for target in ['buy','sell']:
        lTreeFileName = "/home/vikas/ml/ob/e/nsecur/ABAll_AmBRAmBAll/s/2c/AmBRAmB//glmnet" + target + "-td.20140821-tTD30-dt.10.tree1"#args.e+"/"+args.a+ target+'-td.' + os.path.basename(os.path.abspath(args.td)) + '-dt.' + args.dt + attribute.generateExtension() +".tree" + args.treeType
        dd.gGlobalTree[target],lVariable = reading_tree.reading_tree(lTreeFileName,args.treeType)
        dd.gTreeVariablesPresent = dd.gTreeVariablesPresent + lVariable
        dd.gFinalCondition[target]["0"] = ''
        dd.gFinalCondition[target]["0"] = reading_tree.traverse_tree(1,args.treeType,0.0,dd.gGlobalTree[target],dd.gFinalCondition[target]["0"])
        print("Calling tree traversal ")#,dd.gFinalCondition[target]["0"])
else:
    for target in ['buy','sell']:
        lTreeFileName = args.e+"/"+args.a+ target+'-td.' + os.path.basename(os.path.abspath(args.td)) + '-dt.' + args.dt + attribute.generateExtension() +".tree" + args.treeType
        dd.gGlobalTree[target],lVariable = reading_tree.reading_tree(lTreeFileName,args.treeType)
        dd.gTreeVariablesPresent = dd.gTreeVariablesPresent + lVariable
        nodes = args.nodes.split(";")
        dd.gFinalCondition[target]['nodes'] = reading_tree.traverse_nodes(args.treeType,nodes,dd.gGlobalTree[target])
    
config = ConfigObj(args.e+"/design1.ini")
lListOfPredictionDirectory = attribute.getListOfTrainingDirectoriesNames(int(args.nPD),args.pd,args.iT)
lBuyOutputFileObject = args.e+"/Buy-OutOfSampleTree-"+'-pd.' + os.path.basename(os.path.abspath(args.pd)) + '-nPD.' + args.nPD + attribute.generateExtension() +".tree" + args.treeType
lSellOutputFileObject = args.e+"/Sell-OutOfSampleTree-"+'-pd.' + os.path.basename(os.path.abspath(args.pd)) + '-nPD.' + args.nPD + attribute.generateExtension() +".tree" + args.treeType
dd.gOutputGlobalTree['buy'] = [ 0 for i in xrange(4078)] 
dd.gOutputGlobalTree['sell'] = [ 0 for i in xrange(4078)] 
for precitionDirectory in lListOfPredictionDirectory:
    dirName = precitionDirectory.replace('/ro/','/rs/')
    checkAllFilesAreExistOrNot = 'false'
    
    lWFDirName = precitionDirectory.replace('/ro/','/wf/')
    trainingDirectoryName = attribute.getTrainDirFromPredictDir(10,precitionDirectory,"next")

    dd.gFileObjectsOfVariablesPresent = []
    for variable in dd.gTreeVariablesPresent:
        if config['predictions-buy'].get(variable,"f").lower()=="buyprob":
            predictedBuyValuesFileName = lWFDirName+"/p/"+mainExperimentName+"/"+args.a + 'buy' + '-td.' + os.path.basename(os.path.abspath( trainingDirectoryName  )) + '-dt.' + \
                                    args.dt + '-targetClass.' + args.targetClass + '-f.' + experimentName + "-wt." + args.wt+ attribute.generateExtension() + ".predictions"
            dd.gFileObjectsOfVariablesPresent.append(open(predictedBuyValuesFileName,'r'))
        elif config['predictions-sell'].get(variable,"f").lower()=="sellprob":
            predictedSellValuesFileName = lWFDirName+"/p/"+mainExperimentName+"/"+args.a + 'sell' + '-td.' + os.path.basename(os.path.abspath( trainingDirectoryName  )) + '-dt.' +\
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
        
           
        dataFileName = dataFile.getFileNameFromCommandLineParam(precitionDirectory)
        dataFileObject = {}
        dataFileObject['buy'] =  open(lWFDirName+"/t/"+config['target']['buy'] + ".target","r")
        dataFileObject['sell'] =  open(lWFDirName+"/t/"+config['target']['sell'] + ".target","r")
        print("Buy Target file Used :- " ,dataFileObject['buy'] )
        print("Sell Target file Used :- " ,dataFileObject['sell'] )
        lObjectList = treeAccuracyOnPredictionDay.getDataFileAndPredictionsIntoObjectList(dataFileObject,dd.gFileObjectsOfVariablesPresent,dd.gGlobalTree,config)
            
        tEnd = datetime.now()
        print("Time taken to read data and prediction file is " + str(tEnd - tStart))
            
reading_tree.print_ouput_tree(dd.gOutputGlobalTree['buy'], lBuyOutputFileObject)
reading_tree.print_ouput_tree(dd.gOutputGlobalTree['sell'], lSellOutputFileObject)
tEnd = datetime.now()
print("Time taken to for complete run " + str(tEnd - tStart))

