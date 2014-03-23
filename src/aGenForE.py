#!/usr/bin/python
from configobj import ConfigObj
import subprocess
import attribute
import argparse
import os

parser = argparse.ArgumentParser(description='This program will run aGen.py for all attributes required for an experiement. An e.g. command line is aGenAll.py -d ob/data/20140207/ -e e7.1')
parser.add_argument('-d', required=True,help='Directory of data file')
parser.add_argument('-e', required=True,help='Directory of experiement')
parser.add_argument('-m', required=True,help='Directory of geneartors')
args = parser.parse_args()


config = ConfigObj(args.e+"/design.ini")
attributes = config["features"]
attributes["target"] = config["target"]

def runCommandLine(pAttributesName):
    paramList = []
    paramList = ["aGen.py","-d",args.d]
    if "Col" in pAttributesName:
        startPos = pAttributesName.find("Col") + 3
        endPos = pAttributesName.find("In")
        colName = pAttributesName[startPos:endPos]
        pAttributesName = pAttributesName.replace(colName,"C")
        paramList.append("-c")
        paramList.append(colName)

    if "Last" in pAttributesName:
        startPos = pAttributesName.find("Last") + 4
        endPos = pAttributesName.find("Rows")
        N = pAttributesName[startPos:endPos]
        pAttributesName = pAttributesName.replace(N,"N")
        paramList.append("-n")
        paramList.append(N)

    if "Future" in pAttributesName:
        startPos = pAttributesName.find("Future") + 6
        endPos = pAttributesName.find("Rows")
        N = pAttributesName[startPos:endPos]
        pAttributesName = pAttributesName.replace(N,"N")
        paramList.append("-n")
        paramList.append(N)

    paramList.append("-m")
    paramList.append(args.m+pAttributesName)

    print paramList
    return subprocess.check_call(paramList)

for f in attributes:
    attributeName = attributes[f]
    print "\nGenerating for " + attributeName

    if "DivideBy" in attributeName or "Add" in attributeName or "Subtract" in attributeName:
        startPos = attributeName.find("[")
        endPos = attributeName.find("]") + 1
        firstFeatureName = attributeName[0:startPos]
        secondFeatureName = attributeName[endPos:]
        runCommandLine(firstFeatureName)
        runCommandLine(secondFeatureName)
        attributeFile = attribute.getFileNameFromAttributeName(attributeName)
        if (os.path.isfile(attributeFile)):
            print "The feature file already exists"
        else:    
            if "DivideBy" in attributeName:
                attribute.list = attribute.operateOnAttributes(firstFeatureName,secondFeatureName,"DivideBy")
            elif "Add" in attributeName:
                attribute.list = attribute.operateOnAttributes(firstFeatureName,secondFeatureName,"Add")
            elif "Subtract" in attributeName:
                attribute.list = attribute.operateOnAttributes(firstFeatureName,secondFeatureName,"Subtract")
            attribute.writeToFile(attributeName)
        continue

    returnCode = runCommandLine(attributeName)
    if(returnCode < 0):
        print "There has been an unrecoverable error with error code: " + str(returnCode)
        os._exit(-1)
    else:
        print "Return code is: " + str(returnCode)
