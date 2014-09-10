#!/usr/bin/python
from __future__ import division
from __future__ import print_function
import os, sys, argparse
from configobj import ConfigObj
import attribute
parser = argparse.ArgumentParser(description='This program will do trades to measure the quality of the experiment.\n\
 An e.g. command line is tradeE5.py -d ob/data/20140207/ -e ob/e/1 -a logitr -entryCL 0.90 -exitCL .55 -orderQty 500', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-e', required=True,help='Directory of the experiment or sub experiment e/10/s/3c/ABC')
parser.add_argument('-entryCL', required=True,help='Percentage of the confidence level used to enter the trades')
parser.add_argument('-exitCL', required=True,help='Percentage of the confidence level used to exit the trades')
parser.add_argument('-td', required=True,help='Directory of the training data file')
parser.add_argument('-dt',required=False,help="Number of days it was trained")  
parser.add_argument('-targetClass',required=False,help="For which model was used ; binomial(target takes only true and false) / multinomial (target values takes more than 2 values)")
parser.add_argument('-pd', required=True,help='Directory of the prediction data file')
parser.add_argument('-a', required=False,help='Algorithm name')
parser.add_argument('-wt',required=False,help="default/exp , weight type to be given to different days")
parser.add_argument('-orderQty',required=True,help="Order qty to be given")
parser.add_argument('-iT',required=False,help='Instrument name')
parser.add_argument('-sP',required=False,help='Strike price of instrument')
parser.add_argument('-oT',required=False,help='Options Type')
args = parser.parse_args()
import attribute
attribute.initializeInstDetails(args.iT,args.sP,args.oT)


if args.targetClass == None:
    args.targetClass = "binomial"
if args.wt == None:
    args.wt = "default"
if args.a == None:
    args.a = "glmnet"

featureFpList = []
featureNames = []
experimnetList = args.e.split(";")
predFpList = []
predNames = []
targetFpList = []
targetNames = []
tradeFpList = []
mainExperimentNameList = []
for experiment in  experimnetList:                            
    absPathOfExperimentName = os.path.abspath(experiment)
    
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

    mainExperimentNameList.append(mainExperimentName)    
    experimentName = os.path.basename(absPathOfExperimentName)
    sys.path.append("./src/")
    sys.path.append("./ob/generators/")
    
    config = ConfigObj(experiment+"/design.ini")
    featureTargetFilePath = args.pd.replace('ro', 'wf')
    
    
    for feature in config["features-buy"]:
        lName = config["features-buy"][feature].replace('(','').replace(')','')
        if lName not in featureNames:
            lFeatureFile = featureTargetFilePath + "/f/" + lName+ attribute.generateExtension() + ".feature"
            featureFP = open(lFeatureFile, "rb")
            featureFpList.append(featureFP)
            featureNames.append(lName)
        
    for feature in config["features-sell"]:
        lName = config["features-sell"][feature].replace('(','').replace(')','')
        if lName not in featureNames:
            lFeatureFile = featureTargetFilePath + "/f/" + lName + attribute.generateExtension() + ".feature"
            featureFP = open(lFeatureFile, "rb")
            featureFpList.append(featureFP)
            featureNames.append(lName)
            
    dirName = args.pd.replace('/ro/','/wf/')
    targetSet = config['target']
    for target in targetSet.keys():
        predictedValuesFileName = dirName+"/p/"+mainExperimentName+"/" + args.a + target + '-td.' + os.path.basename(os.path.abspath(args.td)) + \
                                     '-dt.' + str(args.dt) + '-targetClass.' + args.targetClass + '-f.' + experimentName +  "-wt." + args.wt + attribute.generateExtension()+ ".predictions"
        predFp = open(predictedValuesFileName, "rb")
        predFpList.append(predFp)
        predNames.append(mainExperimentName+"_"+target)
        print (predictedValuesFileName)                             
    
    for target in targetSet:
        lName = targetSet[target] +attribute.generateExtension() +".target"
        if  lName not in targetNames:
            ltargetFile = featureTargetFilePath + "/t/" + lName
            lTargetFP = open(ltargetFile, "rb")
            targetFpList.append(lTargetFP)
            targetNames.append(lName)
    
    dirName = args.pd.replace('/ro/','/rs/')
    fileNamesForTradeDirectory = dirName + "/t/" + mainExperimentName + "/" 
    
#    lInitialFileName = fileNamesForTradeDirectory + args.a + '-td.' + os.path.basename(os.path.abspath(args.td)) + \
#    '-dt.' + args.dt + '-targetClass.' + args.targetClass + '-f.' + experimentName + "-wt." + args.wt + attribute.generateExtension() + '-l.'+args.entryCL+"-"+args.exitCL + "-tq." + args.orderQty + "-te.7.trade"
#    lTradeFp = open(lInitialFileName, "rb")
#    tradeFpList.append(lTradeFp)

fileName = ''
try:   
   if(attribute.instType!=''):
     command = "ls -1  " +  args.pd + " | grep " +  attribute.instType + "-" + attribute.strikePrice + "-" +  attribute.optionsType
     print(command)
     import commands
     dataFile = commands.getoutput(command)
     print(dataFile)
     if dataFile != None:
        foundFile = True
        fileName = args.pd+"/"+ dataFile
except:
    list_of_files = os.listdir(args.pd) 
    for each_file in list_of_files:
        if each_file.startswith('data') and each_file.endswith('txt'):  #since its all type str you can simply use startswith
            foundFile = True
            fileName = args.pd+"/"+each_file
            break
print("data file being read ", fileName)
dataFp = open(fileName,"rb")    
            
        
dirName = args.pd.replace('/ro/','/rs/')
fileNamesForTradeDirectory = dirName + "/r/" 

lInitialFileName = fileNamesForTradeDirectory + args.a + '-td.' + os.path.basename(os.path.abspath(args.td)) + \
               '-dt.' + args.dt + '-f.' + "_".join(mainExperimentNameList) + \
               '-l.'+args.entryCL+"-"+args.exitCL + "-tq." + args.orderQty + ".csv"

print ("filename---", lInitialFileName)
outputfile = open(lInitialFileName, 'wb')
print ("outputfile---", lInitialFileName)
# featureFpList = []
# featureNames = []
# experimnetList = args.e.split(";")
# predFpList = []
# predNames = []
# targetFpList = []
# targetNames = []
# tradeFpList = []
startIndex = 0
while True:
    allFeatureData = ''
    line = dataFp.readline()
    if line == '' :
        exit(0)
    ls = line.strip().split(";")
    list_temp = []
    list_temp.append(ls[33])
    list_temp.extend(ls[0:11])
    #list_temp.extend([ls[41],ls[42]])
    list_temp.extend(ls[11:21])
    #list_temp.extend([ls[43],ls[44]])
    list_temp.extend(ls[21:23])
    list_temp.extend(ls[34:41])
    line = ";".join(list_temp)
    allFeatureData = allFeatureData + line + ";"
    
    index = 0
    for fFp in featureFpList:
        line = fFp.readline()
        if line == '' :
            exit(0)
        if startIndex != 0 :
            allFeatureData = allFeatureData + line.split(";")[1].strip() + ";"
        else:
            allFeatureData = allFeatureData + featureNames[index]+ ";"
        index = index + 1 

    index = 0    
    for tFp in targetFpList:
        line = tFp.readline()
        if startIndex != 0 :
            allFeatureData = allFeatureData + line.split(";")[1].strip() + ";"
        else:
            allFeatureData = allFeatureData + targetNames[index]+ ";"
        index = index + 1
    index = 0

    for predFp in predFpList:
        line = predFp.readline()
        if line == '' :
            exit(0)
        if startIndex != 0 :
            allFeatureData = allFeatureData + line.split(",")[2].strip() + ";"  
        else:
            allFeatureData = allFeatureData + predNames[index]  + ";"
        index = index + 1

    index = 0    
#    for tradeFp in tradeFpList:
#        line = tradeFp.readline()
#        if line == '' :
#            exit(0)
#        lineSplit = line.split(";")
#        if startIndex != 0 :
#            allFeatureData = allFeatureData + lineSplit[1] + ";" + lineSplit[2] + ";" + lineSplit[14] + ";" + lineSplit[11] + ";"
#        else:
#            allFeatureData = allFeatureData + lineSplit[1]+"_"+mainExperimentNameList[index]+ ";" + lineSplit[2]+"_"+mainExperimentNameList[index] + ";" \
#             + lineSplit[14]+"_"+mainExperimentNameList[index] + ";" + lineSplit[11]+"_"+mainExperimentNameList[index] + ";"
             
 #       index = index + 1 
        
    startIndex = startIndex + 1   
    lineToWrite = str(allFeatureData) + "\n"
    outputfile.write(lineToWrite)






