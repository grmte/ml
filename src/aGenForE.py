#!/usr/bin/python
from configobj import ConfigObj
import subprocess
import attribute
import argparse
import os

print "\nStarting to run Attribute generator for experiment"
parser = argparse.ArgumentParser(description='This program will run aGen.py for all attributes required for an experiement. An e.g. command line is aGenAll.py -d ob/data/20140207/ -e e7.1')
parser.add_argument('-d', required=True,help='Directory of data file')
parser.add_argument('-e', required=True,help='Directory of experiement')
parser.add_argument('-g', required=True,help='Directory of geneartors')
args = parser.parse_args()


config = ConfigObj(args.e+"/design.ini")
attributes = config["features"]
attributes["target"] = config["target"]


def genForAttribute(attributeName):
    if "DivideBy" in attributeName or "Add" in attributeName or "Subtract" in attributeName or "MultiplyBy" in attributeName:
        startPos = attributeName.find("[")
        endPos = attributeName.find("]") + 1
        firstFeatureName = attributeName[0:startPos]
        secondFeatureName = attributeName[endPos:]
        genForAttribute(firstFeatureName)
        genForAttribute(secondFeatureName)
        operatorName = attributeName[startPos:endPos]
        attributeFile = attribute.getFileNameFromAttributeName(attributeName)
        if (os.path.isfile(attributeFile)):
            print "The feature file already exists: "+attributeFile
        else:    
            if "DivideBy" in operatorName:
                attribute.list = attribute.operateOnAttributes(firstFeatureName,secondFeatureName,"DivideBy")
            elif "Add" in operatorName:
                attribute.list = attribute.operateOnAttributes(firstFeatureName,secondFeatureName,"Add")
            elif "Subtract" in operatorName:
                attribute.list = attribute.operateOnAttributes(firstFeatureName,secondFeatureName,"Subtract")
            elif "MultiplyBy" in operatorName:
                attribute.list = attribute.operateOnAttributes(firstFeatureName,secondFeatureName,"MultiplyBy")
            attribute.writeToFile(attributeName)
        return   

    returnCode = runCommandLine(attributeName)
    if(returnCode < 0):
        print "There has been an unrecoverable error with error code: " + str(returnCode)
        os._exit(-1)
    else:
        print "Return code is: " + str(returnCode)


def runCommandLine(pAttributesName):
    paramList = []
    paramList = ["aGen.py","-d",args.d]


    # Getting the moduleName from the attributeName
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
        if endPos == -1:
            endPos = pAttributesName.find("Secs")
            if endPos == -1:
                endPos = pAttributesName.find("Qty")
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

    paramList.append("-g")
    paramList.append(args.g+pAttributesName)

    print "\nExecuting the command: " + " ".join(paramList)
    return subprocess.check_call(paramList)

for f in attributes:
    attributeName = attributes[f]
    print "\nGenerating for " + attributeName
    genForAttribute(attributeName)
