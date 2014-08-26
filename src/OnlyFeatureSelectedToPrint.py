#!/usr/bin/python
from __future__ import division
from __future__ import print_function
import os, sys, argparse
from configobj import ConfigObj
import attribute
parser = argparse.ArgumentParser(description='This program will do trades to measure the quality of the experiment.\n\
 An e.g. command line is tradeE5.py -d ob/data/20140207/ -e ob/e/1 -a logitr -entryCL 0.90 -exitCL .55 -orderQty 500', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-e', required=True,help='Directory of the experiment or sub experiment e/10/s/3c/ABC')
parser.add_argument('-entryCL', required=False,help='Percentage of the confidence level used to enter the trades')
parser.add_argument('-exitCL', required=False,help='Percentage of the confidence level used to exit the trades')
parser.add_argument('-td', required=False,help='Directory of the training data file')
parser.add_argument('-dt',required=False,help="Number of days it was trained")  
parser.add_argument('-targetClass',required=False,help="For which model was used ; binomial(target takes only true and false) / multinomial (target values takes more than 2 values)")
parser.add_argument('-pd', required=True,help='Directory of the prediction data file')
parser.add_argument('-a', required=True,help='Algorithm name')
parser.add_argument("-skipT",required=False,help="Skip creating trade files if already generated")
parser.add_argument('-wt',required=False,help="default/exp , weight type to be given to different days")
parser.add_argument('-orderQty',required=False,help="Order qty to be given")

args = parser.parse_args()
if args.skipT == None:
    args.skipT = "no"
                    
absPathOfExperimentName = os.path.abspath(args.e)

if 'nsecur' in absPathOfExperimentName:
    pathAfterE = absPathOfExperimentName[absPathOfExperimentName.index("/nsecur/")+8:]
elif 'nsefut' in absPathOfExperimentName:
    pathAfterE = absPathOfExperimentName[absPathOfExperimentName.index("/nsefut/")+8:]
elif 'nseopt' in absPathOfExperimentName:
    pathAfterE = absPathOfExperimentName[absPathOfExperimentName.index("/nseopt/")+8:]
    
if "/" in pathAfterE:
    mainExperimentName = pathAfterE[:pathAfterE.index("/")]
else:
    mainExperimentName = pathAfterE
    
experimentName = os.path.basename(absPathOfExperimentName)
sys.path.append("./src/")
sys.path.append("./ob/generators/")
import codecs, glob

config = ConfigObj(args.e+"/design.ini")
featureTargetFilePath = args.pd.replace('ro', 'wf')

features = config["features-buy"]
featureFiles = []
featureFpList = []
featureFp = 1

intermediate_feature_dict , config = attribute.getIntermediateAttributesForExperiment(args.e)
# normal_feature_list , config = attribute.getAttributesOfExperiment(args.e)
normal_feature_list = {
                         "A" : "fStrengthOfColAskInOrderNInLast60Secs" , 
                         "B":"fStrengthOfColBidInOrderNInLast60Secs",
                        "C" : "fStrengthOfColAskInOrderXInLast60Secs", 
                        "D":"fStrengthOfColBidInOrderXInLast60Secs",
                        "E" : "fVarianceOfCol_fStrengthOfColAskInOrderNInLast60Secs_InLast60Secs",
                        "F": "fVarianceOfCol_fStrengthOfColBidInOrderNInLast60Secs_InLast60Secs",
                        "G":"fVarianceOfCol_fStrengthOfColAskInOrderXInLast60Secs_InLast60Secs",
                        "H" : "fVarianceOfCol_fStrengthOfColBidInOrderXInLast60Secs_InLast60Secs",
                        "E":"fCol_NewStrengthVariable60_InCurrentRow",
                        "F":"fCol_CancelStrengthVariable60_InCurrentRow",
                       }

for feature in normal_feature_list:
    lFeatureFile = featureTargetFilePath + "/f/" + normal_feature_list[feature] + ".feature"
    featureFP = "featureFp" + str(featureFp)
    featureFP = open(lFeatureFile, "rb")
    featureFpList.append(featureFP)
    featureFiles.append(lFeatureFile)
    featureFp = featureFp + 1

targetSet = config['target']

# dirName = args.pd.replace('/ro/','/wf/')
# predFpList = []
# for target in targetSet.keys():
#     predictedValuesFileName = dirName+"/p/"+mainExperimentName+"/" + args.a + target + '-td.' + os.path.basename(os.path.abspath(args.td)) + \
#                                  '-dt.' + args.dt + '-targetClass.' + args.targetClass + '-f.' + experimentName +  "-wt." + args.wt + ".predictions"
#     predFp = open(predictedValuesFileName, "rb")
#     predFpList.append(predFp)
#     
#     print (predictedValuesFileName)                             

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

pdFiles = args.pd + "*.txt" 
files = glob.glob(pdFiles)  
predictionFpList = []

for file1 in files:
    tdFp =  open(file1, 'rb') 
    predictionFpList.append(tdFp)
        
dirName = args.pd.replace('/ro/','/rs/')
fileNamesForTradeDirectory = dirName + "/t/" + mainExperimentName + "/" 

# totalEntryCL = args.entryCL.split(";")
# totalExitCL = args.exitCL.split(";")
# tradeFpList = []
# for indexOfCL in range(0,len(totalEntryCL)):
#     lInitialFileName = fileNamesForTradeDirectory + args.a + '-td.' + os.path.basename(os.path.abspath(args.td)) + \
#                    '-dt.' + args.dt + '-targetClass.' + args.targetClass + '-f.' + experimentName + "-wt." + args.wt + \
#                    '-l.'+totalEntryCL[indexOfCL]+"-"+totalExitCL[indexOfCL] + "-tq." + args.orderQty + ".trade"
#     lTradeFp = open(lInitialFileName, "rb")
#     tradeFpList.append(lTradeFp)
#     
dirName = args.pd.replace('/ro/','/rs/')
fileNamesForTradeDirectory = dirName + "/r/" 
lInitialFileName = fileNamesForTradeDirectory + args.a + \
               '-f.' + experimentName +".csv"
print ("filename---", lInitialFileName)
outputfile = codecs.open(lInitialFileName, 'wb') 

startIndex = 0
while True:
    allFeatureData = ''
    for trFp in predictionFpList:
        line = trFp.readline()
        if line == '' :
            exit(0)
        allFeatureData = allFeatureData + line.strip() + ";"
#     for predFp in predFpList:
#         line = predFp.readline()
#         if line == '' :
#             exit(0)
#         if startIndex != 0 :
#             allFeatureData = allFeatureData + line.split(",")[2].strip() + ";"  
#         else:
#             allFeatureData = allFeatureData + os.path.basename(os.path.abspath(predFp.name.split('.predictions')[0]))  + ";"
    for fFp in featureFpList:
        line = fFp.readline()
        if line == '' :
            exit(0)
        if startIndex != 0 :
            allFeatureData = allFeatureData + line.split(";")[1].strip() + ";"
        else:
            allFeatureData = allFeatureData + os.path.basename(os.path.abspath(fFp.name.split(".feature")[0])) + ";"

    for tFp in targetFpList:
        line = tFp.readline()
        allFeatureData = allFeatureData + line.split(";")[1].strip() + ";"
#     for tradeFp in tradeFpList:
#         line = tradeFp.readline()
#         if line == '' :
#             exit(0)
#         lineSplit = line.split(";")
#         allFeatureData = allFeatureData + lineSplit[1] + ";" + lineSplit[2] + ";" + lineSplit[10] + ";" + lineSplit[13] + ";" + lineSplit[11] + ";" + lineSplit[14] + ";"
    startIndex = startIndex + 1   
    lineToWrite = str(allFeatureData) + "\n"
    outputfile.write(lineToWrite)






