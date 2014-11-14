#!/usr/bin/python
from __future__ import division
import os
import sys

import argparse
parser = argparse.ArgumentParser(description='This program will generate a confusion matrix to measure the quality of the experiment. An e.g. command line is cMatrixGen.py -d ob/data/20140207/ -e e1 -a logitr')
parser.add_argument('-e', required=True,help='Directory of the experiment')
parser.add_argument('-a', required=True,help='Algorithm name')
parser.add_argument('-pd', required=True,help='Prediction directory')
parser.add_argument('-dt',required=False,help="Number of days for which it has to be run")
parser.add_argument('-targetClass',required=True,help="binomial/multinomial")
parser.add_argument('-td',required=True,help="training directory")
parser.add_argument('-wt',required=True,help="default/exp , weight type to be given to different days")
# This is a command and it does not have sub commands. Hence it does not need a "sequence of commands" as a parameter.
args = parser.parse_args()

if args.dt == None:
    args.dt = 1
if args.wt == None:
    args.wt = "default"
    
from configobj import ConfigObj
eDesignConfigObj = ConfigObj(args.e+"/design.ini")
 
# The following will take care if args.e = "ob/e1/" or args.e = "ob/e1"
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

print "\nStarting to generate the confusion matrix"

dirName = args.pd.replace('/ro/','/wf/')
def matrixUpdate(pPredictedProb,pActualValue):
    #print pPredictedProb,pActualValue

    if(pActualValue == 1):
        actualState = 1
    else:
        actualState = 0

    """ code to do for 1 prob    
    if(pPredictedProb > .5):
        predictedState = 1
    else:
        predictedState = 0

    state[actualState][predictedState] = state[actualState][predictedState] + 1
    """
    
    for i in [ 5.0 , 5.5 , 6.5 , 7.0  ]:
        thresold = float(i)/10

        if(pPredictedProb > thresold):
            predictedState = 1
        else:
            predictedState = 0

        state[i][actualState][predictedState] = state[i][actualState][predictedState] + 1            

targetSet = eDesignConfigObj["target"]
for target in targetSet.keys():
    predictedValuesFileName = dirName+"/p/"+mainExperimentName+"/" + args.a + target + '-td.' + os.path.basename(os.path.abspath(args.td)) + \
                                 '-dt.' + str(args.dt) + '-targetClass.' + args.targetClass + '-f.' + experimentName +  "-wt." + args.wt + ".predictions"
    print "Reading predicted values from: "+ predictedValuesFileName
    predictedValuesFile = open(predictedValuesFileName)
    
    actualValuesFileName = dirName+"/t/"+eDesignConfigObj["target"][target]+".target"
    print "Reading actual values from: "+ actualValuesFileName
    actualValuesFile = open(actualValuesFileName)
    # reading the actual values into a dictionary on timestamp
    actualValuesDict=dict()
    totalNumberOfRows = 0
    ItHasHeader = 1
    for line in actualValuesFile:
        if (ItHasHeader == 1):
            ItHasHeader = 0
            continue
        line=line.rstrip('\n')
        splitLine = line.split(';',2)
        timeStamp = splitLine[0]
        value = int(splitLine[1])
        actualValuesDict[timeStamp] = value
        totalNumberOfRows += 1
    
    import numpy
    state = numpy.zeros((10,2,2),dtype=numpy.int)
    
    
    predictedValueNotFoundInActualValue = 0
    IsItHeader = 1
    currentRowNumber = 0
    
    print "Entering for loop to process rows: ",
    divisorToPrint10Times = int(totalNumberOfRows / 10) 
    for line in predictedValuesFile:
        if (IsItHeader == 1):
            IsItHeader = 0
            continue
        line=line.rstrip('\n')
        splitLine = line.split(',',2)
        timeStamp = splitLine [1]
        try:   #TODO: remove this and then run the code to identify errors.
            predictedProb = float(splitLine[2]) # This is to avoid this error    predictedProb = float(splitLine[2])   ValueError: could not convert string to float: 
        except:
            predictedProb = 0
        try:
            actualValue = actualValuesDict[timeStamp]
            fillUpMatrix = True
        except:
            predictedValueNotFoundInActualValue = predictedValueNotFoundInActualValue +1
    
        if(fillUpMatrix):
            matrixUpdate(predictedProb,actualValue)
    
        currentRowNumber = currentRowNumber + 1
        if( currentRowNumber % divisorToPrint10Times == 0):
            print str(currentRowNumber), 
            sys.stdout.flush()
     
    print "\nPredicted event not found in actual event = " + str(predictedValueNotFoundInActualValue)
    
    cMatrixDirName = args.pd.replace('/ro/','/rs/')
    cMatrixDataDirectoryName = cMatrixDirName+"/c/"
    if not os.path.exists(cMatrixDataDirectoryName):
        os.mkdir(cMatrixDataDirectoryName)
    cMatrixDataDirectoryName = cMatrixDataDirectoryName+mainExperimentName+"/"
    if not os.path.exists(cMatrixDataDirectoryName):
        os.mkdir(cMatrixDataDirectoryName)    
    fileName = cMatrixDataDirectoryName+"/" + args.a + target + '-td.' + os.path.basename(os.path.abspath(args.td)) + \
                                 '-dt.' + str(args.dt) + '-targetClass.' + args.targetClass + '-f.' + experimentName +  "-wt." + args.wt +".cmatrix"
    outputFile = open(fileName,"w")
    print "Starting to write: "+fileName
    
    formatString = "%3s,%10s,%10s,%10s,%10s,%10s,%7s,%7s,%7s,%7s,%7s,%7s,%7s,%7s,%7s,%7s \n"
    outputFile.write(formatString% ("%TS","FN A=1 P=0","TN A=0 P=0","FP A=0 P=1","TP A=1 P=1","N","Accuracy","TPR","TNR","PPV","NPV","FPR","FDR","FNR","ACC","F1"))
    
    import cmath
    for i in [ 5.5 , 6.0 , 6.5 , 7.0 ,7.5  ]:
        FN = state[i][1][0]
        TN = state[i][0][0]
        FP = state[i][0][1]
        TP = state[i][1][1] 
        N = TN + TP +FN + FP
        
        Accuracy = (TP+TN) / N
        
        S = ( TP + FN ) / N
        P =  TP + FN 
        PForMCC = (TP + FP )/ N
        numerator = (TP / N ) - (S * PForMCC)
        denominatorSquared = PForMCC * S * (1-S) * (1-PForMCC)
        denominator = cmath.sqrt(denominatorSquared)
        MCC = numerator / denominator
        MCC = round(MCC,3)
        TPR = round(TP / P , 3)
        TNR = round (TN / N , 3)
        PPV = round (TP / (TP + FP) , 3)
        NPV = round (TN / (TN+FN), 3)
        FPR = round (FP / N , 3) 
        FDR = round (1 - PPV, 3)
        FNR = round (FN / (FN+TP),3)
        ACC = round ((TP + TN) / (P+N),3)
        F1 = round(2 * TP / (2 * TP + FP + FN) , 3)
        dollar = TP * .5 - (FP * 1.5)
        outputFile.write(formatString % (str(i*10),str(FN),str(TN),str(FP),str(TP),str(N),str(Accuracy),str(TPR),str(TNR),str(PPV),str(NPV),str(FPR),str(FDR),str(FNR),str(ACC),str(F1)))
    
    outputFile.write("Ref: http://en.wikipedia.org/wiki/Matthews_correlation_coefficient \n")
    outputFile.write("========== Section: Experiment design ================ \n")
    outputFile.write(open(args.e+"/design.ini").read())
