#!/usr/bin/python
from configobj import ConfigObj
import subprocess, argparse, os
import attribute, utility

print "\nStarting to run Attribute generator for experiment"


def parseCommandLine():
    parser = argparse.ArgumentParser(description='This program will run aGen.py for all attributes required for an experiement. An e.g. command line is aGenForE.py -d ob/data/20140207/ -e e7.1')
    parser.add_argument('-d', required=True,help='Directory of data file')
    parser.add_argument('-e', required=True,help='Directory of experiement')
    parser.add_argument('-g', required=True,help='Directory of geneartors')
    parser.add_argument('-run', required=True,help='dry or real')
    parser.add_argument('-sequence', required=True,help='ld (local distributed) or pd(parallel distributed)')
    args = parser.parse_args()
    return args

def getAttributesOfExprement(experimentFolder):
    config = ConfigObj(experimentFolder+"/design.ini")
    attributes = config["features"]
    attributes["target"] = config["target"]
    return attributes

def genAttribute(attributeName,dataFolder,generatorsFolder):
    commandLine = []
    if "DivideBy" in attributeName or "Add" in attributeName or "Subtract" in attributeName or "MultiplyBy" in attributeName:
        startPos = attributeName.find("[")
        endPos = attributeName.find("]") + 1
        firstAttributeName = attributeName[0:startPos]
        secondAttributeName = attributeName[endPos:]
        commandLine.append(genAttribute(firstAttributeName,dataFolder,generatorsFolder)) # recursive call
        commandLine.append(genAttribute(secondAttributeName,dataFolder,generatorsFolder)) # recursive call
        operatorName = attributeName[startPos:endPos]
        attributeFile = attribute.getOutputFileNameFromAttributeName(attributeName,dataFolder)
        if "DivideBy" in operatorName:
            commandLine.append(attribute.getCommandLineToOperateOnAttributes(firstAttributeName,secondAttributeName,"DivideBy",dataFolder))
        elif "Add" in operatorName:
            commandLine.append(attribute.getCommandLineToOperateOnAttributes(firstAttributeName,secondAttributeName,"Add",dataFolder))
        elif "Subtract" in operatorName:
            commandLine.append(attribute.getCommandLineToOperateOnAttributes(firstAttributeName,secondAttributeName,"Subtract",dataFolder))
        elif "MultiplyBy" in operatorName:
            commandLine.append(attribute.getCommandLineToOperateOnAttributes(firstAttributeName,secondAttributeName,"MultiplyBy",dataFolder))
            
        return commandLine   

    return getCommandLineForSingleAttribute(attributeName,dataFolder,generatorsFolder)

def getCommandLineForSingleAttribute(pUserFriendlyAttributeName,dataFolder,generatorsFolder):
    """
    Support the user friendly attribute name is fColBidP0InCurrentRow this will return fColCInCurrentRow -c BidP0 
    """
    paramList = []
    paramList = ["aGen.py","-d",dataFolder]


    # Getting the moduleName from the attributeName
    if "Col" in pUserFriendlyAttributeName:
        startPos = pUserFriendlyAttributeName.find("Col") + 3
        endPos = pUserFriendlyAttributeName.find("In")
        colName = pUserFriendlyAttributeName[startPos:endPos]
        pUserFriendlyAttributeName = pUserFriendlyAttributeName.replace(colName,"C")
        paramList.append("-c")
        paramList.append(colName)

    if "Last" in pUserFriendlyAttributeName:
        startPos = pUserFriendlyAttributeName.find("Last") + 4
        endPos = pUserFriendlyAttributeName.find("Rows")
        if endPos == -1:
            endPos = pUserFriendlyAttributeName.find("Secs")
            if endPos == -1:
                endPos = pUserFriendlyAttributeName.find("Qty")
        N = pUserFriendlyAttributeName[startPos:endPos]
        pUserFriendlyAttributeName = pUserFriendlyAttributeName.replace(N,"N")
        paramList.append("-n")
        paramList.append(N)

    if "Future" in pUserFriendlyAttributeName:
        startPos = pUserFriendlyAttributeName.find("Future") + 6
        endPos = pUserFriendlyAttributeName.find("Rows")
        N = pUserFriendlyAttributeName[startPos:endPos]
        pUserFriendlyAttributeName = pUserFriendlyAttributeName.replace(N,"N")
        paramList.append("-n")
        paramList.append(N)

    paramList.append("-g")
    paramList.append(generatorsFolder+pUserFriendlyAttributeName)

    commandLine =[]
    commandLine.append(paramList)
    return commandLine


def getCommandList(experimentFolder,dataFolder,generatorsFolder):
    commandList = list()
    attributes = getAttributesOfExprement(experimentFolder)
    for f in attributes:
        attributeName = attributes[f]
        print "\nGenerating for " + attributeName
        command = genAttribute(attributeName,dataFolder,generatorsFolder)
        commandList.extend(command)
    return commandList    

def main():
    args = parseCommandLine()
    experimentFolder = args.e
    dataFolder = args.d
    generatorsFolder = args.g
    commandList = getCommandList(experimentFolder,dataFolder,generatorsFolder)
    return utility.runCommandList(commandList,args)


if __name__ == "__main__":
    main()
