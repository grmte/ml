#!/usr/bin/python
from __future__ import division
import os


import argparse
parser = argparse.ArgumentParser(description='This program will generate a confusion matrix to measure the quality of the experiment. An e.g. command line is cMatrixGen.py -d ob/data/20140207/ -e e1')
parser.add_argument('-d', required=True,help='Directory of the data file')
parser.add_argument('-e', required=True,help='Directory of the experiment')
args = parser.parse_args()

from configobj import ConfigObj
eDesignConfigObj = ConfigObj(args.e+"/design.ini")
 
# The following will take care if args.e = "ob/e1/" or args.e = "ob/e1"
experimentName = os.path.basename(os.path.abspath(args.e))

predictedValuesFileName = args.d+"/"+experimentName+".predictions"
print "Starting to read the predicted values from "+ predictedValuesFileName
predictedValuesFile = open(predictedValuesFileName)

actualValuesFileName = args.d+"/"+eDesignConfigObj["target"]+".target"
print "Starting to read the actual values from "+ actualValuesFileName
actualValuesFile = open(actualValuesFileName)

# reading the actual values into a dictionary on timestamp
actualValuesDict=dict()
for line in actualValuesFile:
    line=line.rstrip('\n')
    splitLine = line.split(',',1)
    timeStamp = splitLine[0]
    value = int(splitLine[1])
    actualValuesDict[timeStamp] = value

import numpy
state = numpy.zeros((10,2,2),dtype=numpy.int)

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
    
    for i in xrange (1,10,1):
        thresold = float(i)/10

        if(pPredictedProb > thresold):
            predictedState = 1
        else:
            predictedState = 0

        state[i][actualState][predictedState] = state[i][actualState][predictedState] + 1            



predictedValueNotFoundInActualValue = 0
IsItHeader = 1
currentRowNumber = 0
for line in predictedValuesFile:
    if (IsItHeader == 1):
        IsItHeader = 0
        continue
    line=line.rstrip('\n')
    splitLine = line.split(',',2)
    timeStamp = splitLine [1]
    predictedProb = float(splitLine[2])
    try:
        actualValue = actualValuesDict[timeStamp]
        fillUpMatrix = True
    except:
        predictedValueNotFoundInActualValue = predictedValueNotFoundInActualValue +1

    if(fillUpMatrix):
        matrixUpdate(predictedProb,actualValue)

    currentRowNumber = currentRowNumber + 1
    if( currentRowNumber % 1000 == 0):
        print "Processing row number " + str(currentRowNumber)

 
print "predicted value not found in actual value = " + str(predictedValueNotFoundInActualValue)

print "The confusion matrix is"
print state

fileName = args.d+"/"+experimentName+".cmatrix"
outputFile = open(fileName,"w")
print "Starting to write the output file"

formatString = "%3s,%10s,%10s,%10s,%10s,%7s,%7s,%7s,%7s,%7s,%7s,%7s,%7s,%7s,%7s \n"
outputFile.write(formatString% ("%TS","FN A=1 P=0","TN A=0 P=0","FP A=0 P=1","TP A=1 P=1","MCC","TPR","TNR","PPV","NPV","FPR","FDR","FNR","ACC","F1"))

import cmath
for i in xrange (1,10,1):
    FN = state[i][1][0]
    TN = state[i][0][0]
    FP = state[i][0][1]
    TP = state[i][1][1] 
    N = TN + TP +FN + FP
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
    outputFile.write(formatString % (str(i*10),str(FN),str(TN),str(FP),str(TP),str(MCC),str(TPR),str(TNR),str(PPV),str(NPV),str(FPR),str(FDR),str(FNR),str(ACC),str(F1)))

outputFile.write("Ref: http://en.wikipedia.org/wiki/Matthews_correlation_coefficient")
