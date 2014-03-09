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
for line in actualValuesFile:
    splitLine = line.split(' ',1)
    timeStamp = splitLine[0]
    value = splitLine[1]
    actualValueDict[timeStamp] = value

confusionMatrix ['.9']['true']['positive'] = list()
confusionMatrix ['.9']['true']['negative'] = list()
confusionMatrix ['.9']['false']['positive'] = list()
confusionMatrix ['.9']['false']['negative'] = list()

for line in predictedValuesFile:
    splitLine = line.split(' ',3)
    predictedProb = splitLine[1]
    timeStamp = splitLine [2]
    actualValue = actualValueDict[timeStamp]
    print line
    print predictedProb
    print actualValue

    if(predictedProb > .9):
        predictedValueThresold['.9'] = ""
