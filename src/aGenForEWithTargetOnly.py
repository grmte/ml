#!/usr/bin/python
import EvaluationOfExpression
import argparse
import attribute, utility
from configobj import ConfigObj
print "\nStarting to run Attribute generator for experiment"
import pdb
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

def genAttribute(attributeName,dataFolder,generatorsFolder,pTickSize,pConfig):
    commandLine = []
    postfixStackEvaulation = []
    postfixStack = EvaluationOfExpression.convertingInfixToPostfix(attributeName)
    for token in postfixStack:
        if token.type != "OPERATOR":
            postfixStackEvaulation.append(token.name)
        else:
            secondAttributeName = postfixStackEvaulation.pop()
            firstAttributeName = postfixStackEvaulation.pop()
            if firstAttributeName=='E':
                pass
            else:
                try:
                    float(firstAttributeName)
                except:
                    if  "[DivideBy]" not in firstAttributeName and "[Add]" not in firstAttributeName and "[Subtract]" not in firstAttributeName and "[Exp]" not in firstAttributeName \
                    and "[Pow]" not in firstAttributeName and "[Log]" not in firstAttributeName:
                        commandLine.append(getCommandLineForSingleAttribute(firstAttributeName,dataFolder,generatorsFolder,pTickSize,pConfig))
            if secondAttributeName=='E':
                pass
            else:
                try:
                    float(secondAttributeName)
                except:
                    if  "[DivideBy]" not in secondAttributeName and "[Add]" not in secondAttributeName and "[Subtract]" not in secondAttributeName and "[Exp]" not in secondAttributeName \
                    and "[Pow]" not in secondAttributeName and "[Log]" not in firstAttributeName:
                        commandLine.append(getCommandLineForSingleAttribute(secondAttributeName,dataFolder,generatorsFolder,pTickSize,pConfig)) 
                
            operatorName = token.name
            if "[DivideBy]" in operatorName:
                commandLine.append(attribute.getCommandLineToOperateOnAttributes(firstAttributeName,secondAttributeName,"DivideBy",dataFolder))
            elif "[Add]" in operatorName:
                commandLine.append(attribute.getCommandLineToOperateOnAttributes(firstAttributeName,secondAttributeName,"Add",dataFolder))
            elif "[Subtract]" in operatorName:
                commandLine.append(attribute.getCommandLineToOperateOnAttributes(firstAttributeName,secondAttributeName,"Subtract",dataFolder))
            elif "[MultiplyBy]" in operatorName:
                commandLine.append(attribute.getCommandLineToOperateOnAttributes(firstAttributeName,secondAttributeName,"MultiplyBy",dataFolder))
            elif "[Exp]" in operatorName:
                commandLine.append(attribute.getCommandLineToOperateOnAttributes(firstAttributeName,secondAttributeName,"Exp",dataFolder))
            elif "[Pow]" in operatorName:
                commandLine.append(attribute.getCommandLineToOperateOnAttributes(firstAttributeName,secondAttributeName,"Pow",dataFolder))
            elif "[Log]" in operatorName:
                commandLine.append(attribute.getCommandLineToOperateOnAttributes(firstAttributeName,secondAttributeName,"Log",dataFolder))
            postfixStackEvaulation.append(firstAttributeName + operatorName + secondAttributeName)
    while len(postfixStackEvaulation)!=0:
            firstAttributeName = postfixStackEvaulation.pop()
            if  "[DivideBy]" not in firstAttributeName and "[Add]" not in firstAttributeName and "[Subtract]" not in firstAttributeName and "[Exp]" not in firstAttributeName \
                and "[Pow]" not in firstAttributeName and "[Log]" not in firstAttributeName : 
                commandLine.append(getCommandLineForSingleAttribute(firstAttributeName,dataFolder,generatorsFolder,pTickSize,pConfig))        
    return commandLine                     

def getCommandLineForSingleAttribute(pUserFriendlyAttributeName,dataFolder,generatorsFolder,pTickSize,pConfig):
    """
    Support the user friendly attribute name is fColBidP0InCurrentRow this will return fColCInCurrentRow -c BidP0 
    """
    paramList = ["aGen.py","-d",dataFolder,"-tickSize",pTickSize]

    # Getting the moduleName from the attributeName
    if "Col" in pUserFriendlyAttributeName:
        startPos = pUserFriendlyAttributeName.find("Col") + 3
        # There are 2 types of columns. real or synthetic. The following if block finds what type of column do we have.
        if "_" == pUserFriendlyAttributeName[startPos]:
            endPos = pUserFriendlyAttributeName.find("_",startPos+1)
            colNameWithBracketsToBeReplaced = pUserFriendlyAttributeName[startPos:endPos+1]
            colNameWithBracketsToBeReplaced = colNameWithBracketsToBeReplaced.replace('(','')
            colNameWithBracketsToBeReplaced = colNameWithBracketsToBeReplaced.replace(')','')
            fileNameToBeSendAsFeatureCParam = colNameWithBracketsToBeReplaced
            try:
                if colNameWithBracketsToBeReplaced[1:-1] in pConfig["intermediate-features"]:
                    tempVariable = pConfig["intermediate-features"][colNameWithBracketsToBeReplaced[1:-1]]
                    tempVariable = tempVariable.replace('(','')
                    tempVariable = tempVariable.replace(')','')
                    fileNameToBeSendAsFeatureCParam = "_" + tempVariable + "_"
                paramList.append("-i")
                paramList.append(colNameWithBracketsToBeReplaced)
            except:
                pass
            pUserFriendlyAttributeName = pUserFriendlyAttributeName.replace(colNameWithBracketsToBeReplaced,"C",1)
            paramList.append("-c")
            paramList.append(fileNameToBeSendAsFeatureCParam)
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

    if "Order" in pUserFriendlyAttributeName:
            startPos = pUserFriendlyAttributeName.find("Order") + 5
            endPos = pUserFriendlyAttributeName.find("In",startPos + 1)
            colName = pUserFriendlyAttributeName[startPos:endPos]
            pUserFriendlyAttributeName = pUserFriendlyAttributeName.replace(colName,"O")
            paramList.append("-o")
            paramList.append(colName)

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
    config = ConfigObj(experimentFolder+"/design.ini")
    target = config['target']
    for f in target:
        attributeName = target[f]
        print "\nGenerating for " + attributeName
        command = genAttribute(attributeName,dataFolder,generatorsFolder,pTickSize,config)
        commandList.extend(command)
#         featureConfig = config["features-" + f]
#         for featureAttribute in featureConfig:
#             attributeName = featureConfig[featureAttribute]
#             print "\nGenerating for " + attributeName
#             command = genAttribute(attributeName,dataFolder,generatorsFolder,pTickSize,config)
#             commandList.extend(command)            
    return commandList    

def main():
    args = parseCommandLine()
    experimentFolder = args.e
    dataFolder = args.d
    generatorsFolder = args.g
    
    args.sequence = "lp"
#     insideFeatureCommandList = getCommandListForInsideFeatures( experimentFolder,dataFolder,generatorsFolder,args.tickSize )
#     utility.runCommandList(insideFeatureCommandList,args)
#     
#     intermediateFeatureCommandList = getCommandListForIntermediateFeatures(experimentFolder,dataFolder,generatorsFolder,args.tickSize)
#     utility.runCommandList(intermediateFeatureCommandList,args)
#     
    commandList = getCommandList(experimentFolder,dataFolder,generatorsFolder,args.tickSize)
    return utility.runCommandList(commandList,args)


if __name__ == "__main__":
    main()