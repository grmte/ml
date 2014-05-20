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
    parser.add_argument('-tickSize',required=True,help='For NseCurrency data give 25000 and for future options give 5')
    args = parser.parse_args()
    return args

def getAttributesOfExprement(experimentFolder):
    config = ConfigObj(experimentFolder+"/design.ini")
    attributes = config["features"]
    attributes.update(config["target"])
    return attributes

def genAttribute(attributeName,dataFolder,generatorsFolder,pTickSize):
    commandLine = []
    if "DivideBy" in attributeName or "Add" in attributeName or "Subtract" in attributeName or "MultiplyBy" in attributeName:
        startPos = attributeName.find("[")
        endPos = attributeName.find("]") + 1
        firstAttributeName = attributeName[0:startPos]
        secondAttributeName = attributeName[endPos:]
        commandLine.append(genAttribute(firstAttributeName,dataFolder,generatorsFolder,pTickSize)) # recursive call
        commandLine.append(genAttribute(secondAttributeName,dataFolder,generatorsFolder,pTickSize)) # recursive call
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

    return getCommandLineForSingleAttribute(attributeName,dataFolder,generatorsFolder,pTickSize)

def getCommandLineForSingleAttribute(pUserFriendlyAttributeName,dataFolder,generatorsFolder,pTickSize):
    """
    Support the user friendly attribute name is fColBidP0InCurrentRow this will return fColCInCurrentRow -c BidP0 
    """
    paramList = []
    paramList = ["aGen.py","-d",dataFolder,"-tickSize",pTickSize]

    # Getting the moduleName from the attributeName
    if "Col" in pUserFriendlyAttributeName:
        startPos = pUserFriendlyAttributeName.find("Col") + 3
        # There are 2 types of columns. real or synthetic. The following if block finds what type of column do we have.
        if "_" == pUserFriendlyAttributeName[startPos]:
            endPos = pUserFriendlyAttributeName.find("_",startPos+1)
            colNameWithBracketsToBeReplaced = pUserFriendlyAttributeName[startPos:endPos+1]
            pUserFriendlyAttributeName = pUserFriendlyAttributeName.replace(colNameWithBracketsToBeReplaced,"C",1)
            paramList.append("-c")
            paramList.append(colNameWithBracketsToBeReplaced)
            paramList.append("-cType")
            paramList.append("synthetic") 
        else:
            endPos = pUserFriendlyAttributeName.find("In")
            colName = pUserFriendlyAttributeName[startPos:endPos]
            pUserFriendlyAttributeName = pUserFriendlyAttributeName.replace(colName,"C")
            paramList.append("-c")
            paramList.append(colName)
            paramList.append("-cType")
            paramList.append("primary") 

    if "Last" in pUserFriendlyAttributeName:
        startPos = pUserFriendlyAttributeName.rfind("Last") + 4
        endPos = pUserFriendlyAttributeName.rfind("Rows")
        if endPos == -1:
            endPos = pUserFriendlyAttributeName.rfind("Secs")
            if endPos == -1:
                endPos = pUserFriendlyAttributeName.rfind("Qty")
        N = pUserFriendlyAttributeName[startPos:endPos]
        reversedAttributeName = pUserFriendlyAttributeName[::-1]
        pUserFriendlyAttributeName = reversedAttributeName.replace(N[::-1],"N",1)[::-1]
        paramList.append("-n")
        paramList.append(N)

    if "Future" in pUserFriendlyAttributeName:
        startPos = pUserFriendlyAttributeName.find("Future") + 6
        endPos = pUserFriendlyAttributeName.find("Rows")
        if endPos == -1:
            endPos = pUserFriendlyAttributeName.rfind("Trades")
            if endPos == -1:
                endPos = pUserFriendlyAttributeName.rfind("Qty")
        N = pUserFriendlyAttributeName[startPos:endPos]
        pUserFriendlyAttributeName = pUserFriendlyAttributeName.replace(N,"N")
        paramList.append("-n")
        paramList.append(N)

    paramList.append("-g")
    paramList.append(generatorsFolder+pUserFriendlyAttributeName)

    commandLine =[]
    commandLine.append(paramList)
    return commandLine


def getCommandList(experimentFolder,dataFolder,generatorsFolder,pTickSize):
    commandList = list()
    attributes = getAttributesOfExprement(experimentFolder)
    for f in attributes:
        attributeName = attributes[f]
        print "\nGenerating for " + attributeName
#        if "obwave" in attributeName or "obaverge" in attributeName:
#            continue
        command = genAttribute(attributeName,dataFolder,generatorsFolder,pTickSize)
        commandList.extend(command)
    return commandList    

def main():
    args = parseCommandLine()
    experimentFolder = args.e
    dataFolder = args.d
    generatorsFolder = args.g
    commandList = getCommandList(experimentFolder,dataFolder,generatorsFolder,args.tickSize)
    return utility.runCommandList(commandList,args)


if __name__ == "__main__":
    main()
