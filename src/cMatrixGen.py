#!/usr/bin/python
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
    print pPredictedProb,pActualValue

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



predictedValueNotFoundInActualValue = 1
IsItHeader = 1
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


 
print "predicted value not found in actual value = " + str(predictedValueNotFoundInActualValue)
fileName = args.d+"/"+experimentName+".cmatrix"
print "Writing the confusion matrix to " + fileName
print state
numpy.savetxt(fileName,state,fmt="%s")
