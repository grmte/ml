#!/usr/bin/python
from __future__ import division
from __future__ import print_function
import os, sys, argparse
from configobj import ConfigObj

parser = argparse.ArgumentParser(description='This program will do trades to measure the quality of the experiment.\n\
 An e.g. command line is tradeE5.py -d ob/data/20140207/ -e ob/e/1 -a logitr -entryCL 0.90 -exitCL .55 -orderQty 500', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-e', required=True,help='Directory of the experiment or sub experiment e/10/s/3c/ABC')
parser.add_argument('-entryCL', required=True,help='Percentage of the confidence level used to enter the trades')
parser.add_argument('-exitCL', required=True,help='Percentage of the confidence level used to exit the trades')
parser.add_argument('-td', required=True,help='Directory of the training data file')
parser.add_argument('-dt',required=False,help="Number of days it was trained")  
parser.add_argument('-targetClass',required=False,help="For which model was used ; binomial(target takes only true and false) / multinomial (target values takes more than 2 values)")
parser.add_argument('-pd', required=True,help='Directory of the prediction data file')
parser.add_argument('-a', required=True,help='Algorithm name')
parser.add_argument('-ft', required=True,help='Algorithm name')
parser.add_argument("-skipT",required=False,help="Skip creating trade files if already generated")
parser.add_argument('-wt',required=False,help="default/exp , weight type to be given to different days")


args = parser.parse_args()
if args.skipT == None:
    args.skipT = "no"
                    
absPathOfExperimentName = os.path.abspath(args.e)
experimentName = os.path.basename(absPathOfExperimentName)
sys.path.append("./src/")
sys.path.append("./ob/generators/")
import dataFile, colNumberOfData, common
from configobj import ConfigObj
import attribute
import codecs, glob

config = ConfigObj(args.e+"/design.ini")
featureTargetFilePath = args.ft

features = config["features"]
featureFiles = []
featureFpList = []
featureFp = 1
for feature in features:
    lFeatureFile = featureTargetFilePath + "/f/" + features[feature] + ".feature"
    featureFP = "featureFp" + str(featureFp)
    featureFP = open(lFeatureFile, "rb")
    featureFpList.append(featureFP)
    featureFiles.append(lFeatureFile)
    featureFp = featureFp + 1


dirName = args.pd.replace('/ro/','/wf/')
targetSet = config['target']
predFpList = []
for target in targetSet.keys():
    predictedValuesFileName = dirName+"/p/"+experimentName+"/" + args.a + target + '-td.' + os.path.basename(os.path.abspath(args.td)) + \
                                 '-dt.' + args.dt + '-targetClass.' + args.targetClass + '-f.' + experimentName +  "-wt." + args.wt + ".predictions"
    predFp = open(predictedValuesFileName, "rb")
    predFpList.append(predFp)
    
    print (predictedValuesFileName)                             

targetFiles = []
targetFpList = []
trrgetFp = 1
for target in targetSet:
    ltargetFile = featureTargetFilePath + "/t/" + targetSet[target] +".target"
    lTargetFP = "target" + str(trrgetFp)
    lTargetFP = open(ltargetFile, "rb")
    targetFpList.append(lTargetFP)
    targetFiles.append(ltargetFile)
    trrgetFp = trrgetFp + 1

outputfile = codecs.open("combined.txt", 'wb') 

tdFiles = args.td + "*.txt" 
files = glob.glob(tdFiles)  
trainingFiles = []
trainingFpList = []

for file in files:
    tdFp =  open(file, 'rb') 
    trainingFpList.append(tdFp)
        
dirName = args.pd.replace('/ro/','/rs/')
fileNamesForTradeDirectory = dirName + "t/" + experimentName + "/" 

totalEntryCL = args.entryCL.split(";")
totalExitCL = args.exitCL.split(";")
tradeFpList = []
for indexOfCL in range(0,len(totalEntryCL)):
    lInitialFileName = fileNamesForTradeDirectory + args.a + '-td.' + os.path.basename(os.path.abspath(args.td)) + \
                   '-dt.' + args.dt + '-targetClass.' + args.targetClass + '-f.' + experimentName + "-wt." + args.wt + \
                   '-l.'+totalEntryCL[indexOfCL]+"-"+totalExitCL[indexOfCL] + "-te6" + ".trade"
    lTradeFp = open(lInitialFileName, "rb")
    tradeFpList.append(lTradeFp)
    
line = tradeFpList[0].readline()
for predFp in predFpList:
    line = predFp.readline()
    if line == '' :
        exit(0)

while True:
    allFeatureData = ''
    for trFp in trainingFpList:
        line = trFp.readline()
        if line == '' :
            exit(0)
        allFeatureData = allFeatureData + line + ";"
    for predFp in predFpList:
        line = predFp.readline()
        if line == '' :
            exit(0)
        allFeatureData = allFeatureData + line.split(",")[1] + ";"    
    for fFp in featureFpList:
        line = fFp.readline()
        if line == '' :
            exit(0)
        allFeatureData = allFeatureData + line.split(";")[1] + ";"

    for tFp in targetFpList:
        line = tFp.readline()
        allFeatureData = allFeatureData + line.split(";")[1] + ";"
    for tradeFp in tradeFpList:
        line = tradeFp.readline()
        if line == '' :
            exit(0)
        lineSplit = line.split(";")
        allFeatureData = allFeatureData + lineSplit[1] + ";" + lineSplit[2] + ";" + lineSplit[10] + ";" + lineSplit[13] + ";" + lineSplit[11] + ";" + lineSplit[14] + ";"
        
    lineToWrite = str(allFeatureData) + "\n"
    outputfile.write(lineToWrite)






