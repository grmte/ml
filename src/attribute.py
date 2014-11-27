import os
import dataFile
from datetime import timedelta
from datetime import datetime
from configobj import ConfigObj
import math
import commands
aList = []
instType = None
optionsType = None
strikePrice = None
rev = None
def getTargetVariableKeys(pConfig):
    return pConfig["target"]

def generateExtension():

    global instType
    global optionsType
    global strikePrice   
    
    try:
        len(instType)
        return "-iT." + instType + '-oT.' +  optionsType + '-sP.' +  strikePrice
    except:
        return ""
    
def getFeatureVariableKeys(pConfig , pTargetKey):
    featureKeyName = "features-" + pTargetKey
    attributes = pConfig[featureKeyName] 
    return attributes
    
def getIntermediateAttributesForExperiment(experimentFolder):
    config = ConfigObj(experimentFolder)
    attributes = {}
    if "intermediate-features" in config:
        attributes = config["intermediate-features"]
    return attributes , config

def getOperationCommandsInPriority(operateOnAttributeList):
    return sorted(operateOnAttributeList, key = lambda x: len(x[6]))

def getGenerationCommands(pCombinedList,pGenList):
    for i in pCombinedList:
        if(isinstance(i[0],list)):
            getGenerationCommands(i,pGenList)
        else:
            if "aGen.py" in i:
                pGenList.append(i)

def getOperationCommands(pCombinedList,pOperationList):
    for i in pCombinedList:
        if(isinstance(i[0],list)):
            getOperationCommands(i,pOperationList)
        else:
            if "operateOnAttributes.py" in i:
                pOperationList.append(i)

def readAttributeFileIntoMatrix(pFeatureFile):
   
    print "Reading " +pFeatureFile
    matrix = []
    fileHasHeader = 1
    for dataRow in open(pFeatureFile):
        if(fileHasHeader == 1):
            fileHasHeader = 0 
            continue
        dataRow=dataRow.rstrip('\n')
        dataColumns=dataRow.split(';')
        matrix.append(dataColumns)
    
    return matrix   

def getCommandLineToOperateOnAttributes(pFirstAttributeName,pSecondAttributeName,pOperand,dataFolder):
    global instType
    global optionsType
    global strikePrice
    paramList = ["operateOnAttributes.py","-d",dataFolder]  
    paramList.append("-a1")
    paramList.append(pFirstAttributeName)  
    paramList.append("-a2")
    paramList.append(pSecondAttributeName)  
    paramList.append("-operand")
    paramList.append(pOperand)  
    paramList.extend(["-iT",instType,"-sP",strikePrice,"-oT",optionsType])
    return paramList

def getFileNameFromOperationCommand(a1,a2,operand,d):

   extension = generateExtension()
   # assuming that all operations happen on f to operate on t this function needs to change.
   d = d.replace('/ro/','/wf/')   
   return d+"/f/"+a1+"["+operand+"]"+a2+extension+".feature"

def operateOnAttributes(pFirstAttributeName,pSecondAttributeName,pOperand,dataFolder):
   print "\nOperating on attributes. First attribute: "+pFirstAttributeName + " 2nd attribute: "+pSecondAttributeName + " Operation: "+ pOperand
   featureMatrix = [] 
   firstIsConstant = False
   secondIsConstant = False
   if pFirstAttributeName == 'E': 
      firstIsConstant = True
   else:
       try:
           float(pFirstAttributeName)
           firstIsConstant = True
       except: 
           firstFileName = getOutputFileNameFromAttributeName(pFirstAttributeName,dataFolder)
           firstMatrix = readAttributeFileIntoMatrix(firstFileName)
   if pSecondAttributeName == 'E':
      secondIsConstant = True
   else: 
       try:
           float(pSecondAttributeName)
           secondIsConstant = True
       except:
           secondFileName = getOutputFileNameFromAttributeName(pSecondAttributeName,dataFolder)
           secondMatrix = readAttributeFileIntoMatrix(secondFileName)
   
   if firstIsConstant == True:
       firstMatrix =[ [i[0],pFirstAttributeName] for i in secondMatrix]
   elif  secondIsConstant == True:
       secondMatrix = [ [i[0],pSecondAttributeName] for i in firstMatrix]
   count =0  
   currentRowCount = 0
   for dataRow in firstMatrix:
      if(firstMatrix[currentRowCount][0] != secondMatrix[currentRowCount][0]):
         print "The time stamps do not match"
      else:
         timeStamp = firstMatrix[currentRowCount][0]
         if(pOperand == "DivideBy"):
            try:
               value = float(firstMatrix[currentRowCount][1]) / float(secondMatrix[currentRowCount][1])
            except:
               value = float(1)
               print 'Float Division Error , taking value to be 1 therefore'
         elif(pOperand == "Add"):
            value = float(firstMatrix[currentRowCount][1]) + float(secondMatrix[currentRowCount][1])
         elif(pOperand == "Subtract"):
            value = float(firstMatrix[currentRowCount][1]) - float(secondMatrix[currentRowCount][1])
         elif(pOperand == "MultiplyBy"):
            value = float(firstMatrix[currentRowCount][1]) * float(secondMatrix[currentRowCount][1])
         elif(pOperand == "Exp"):
            try: 
                value = math.exp( float(firstMatrix[currentRowCount][1])  * float(secondMatrix[currentRowCount][1]))
            except:
                value = math.exp(709)
         elif(pOperand == "Pow"):
            value = math.pow(float(firstMatrix[currentRowCount][1]),float(secondMatrix[currentRowCount][1]))
         elif(pOperand == "Log"):
            if secondMatrix[currentRowCount][1]=='E':
               try: 
                   value = math.log(float(firstMatrix[currentRowCount][1]))
               except:
                   if float(firstMatrix[currentRowCount][1])==0:
                       value = 0 
                   else:
                       value = math.log(float(firstMatrix[currentRowCount][1]))
               
            else:   
               try: 
                   value = math.log(float(firstMatrix[currentRowCount][1]),float(secondMatrix[currentRowCount][1]))
               except:
                   if float(firstMatrix[currentRowCount][1])==0:
                       value = 0 
                   else:
                       value = math.log(float(firstMatrix[currentRowCount][1]),float(secondMatrix[currentRowCount][1]))
         featureMatrix.append([timeStamp,value,firstMatrix[currentRowCount][1],pOperand,secondMatrix[currentRowCount][1]])

      currentRowCount += 1   
   lListOfHeaderColNames = ["TimeStamp","Value","Operand1","Operator","Operand2"]
   return featureMatrix , lListOfHeaderColNames   

def getAttributeTypeFromAttributeName(pAttributeName):
    if(pAttributeName[0]=='t'):
        return "target"
    else:
        return "feature"
   

def getOutputFileNameFromAttributeName(pAttributesName,dataFolder):
    extension = generateExtension()
    # we need to replace /ro with /wf   
    dirName = dataFolder.replace('/ro/','/wf/')   
    if (getAttributeTypeFromAttributeName(pAttributesName) == "feature"):   
        attributeFile=dirName+"/f/"+pAttributesName+extension+".feature"
    else:   
        attributeFile=dirName+"/t/"+pAttributesName+extension+".target"
       
    return attributeFile
   

def getOutputFileNameFromGeneratorName(pGeneratorName,number,columnName,orderType,diffPip,dataFolder):

    if "NRows" in pGeneratorName:
        N = number
        pGeneratorName = pGeneratorName.replace("NRows",str(N)+"Rows")   
    if "NTrades" in pGeneratorName:
        N = number
        pGeneratorName = pGeneratorName.replace("NTrades",str(N)+"Trades") 
    if "NSecs" in pGeneratorName:
        N = number
        pGeneratorName = pGeneratorName.replace("NSecs",str(N)+"Secs")   
    
    if "NQty" in pGeneratorName:
        N = number
        pGeneratorName = pGeneratorName.replace("NQty",str(N)+"Qty")   

    if "NLevels" in pGeneratorName:
        N = number
        pGeneratorName = pGeneratorName.replace("NLevels",str(N)+"Levels")   
                

    if "ColC" in pGeneratorName:
        pGeneratorName = pGeneratorName.replace("ColC","Col"+columnName)   
       
    if "OrderO" in pGeneratorName:
        pGeneratorName = pGeneratorName.replace("OrderO","Order"+orderType)  
    if "DiffM" in pGeneratorName:
        pGeneratorName = pGeneratorName.replace("DiffM","Diff"+diffPip)   
            
    pGeneratorName = pGeneratorName + generateExtension() 
    # we need to replace /ro with /wf   
    dirName = dataFolder.replace('/ro/','/wf/')   
    if (getAttributeTypeFromAttributeName(pGeneratorName) == "feature"):   
        attributeFile=dirName+"/f/"+pGeneratorName+".feature"
    else:   
        attributeFile=dirName+"/t/"+pGeneratorName+".target"
       
    return attributeFile

def getTrainDirFromPredictDir( pNumOfTrainingDays , pPredictDir , pLastDayOrNextDayAfterLast ):
    lPredicionBaseFolderName = os.path.basename(os.path.abspath(pPredictDir))   
    lPredictionDateObject = datetime.strptime(lPredicionBaseFolderName, '%Y%m%d')
    pNumOfTrainingDays = int(pNumOfTrainingDays)
    index = 0
    countOfDaysTaken = 0
    l_training_date_full_path_name = ""
    if pLastDayOrNextDayAfterLast.lower() == "next":
        pNumOfTrainingDays = pNumOfTrainingDays + 1
    while(1):
        l_training_date = lPredictionDateObject - timedelta(days = index)
        index = index + 1 
        if( l_training_date.weekday() == 5 or l_training_date.weekday() == 6): # Day is monday
            continue
        l_training_date_in_string = l_training_date.strftime('%Y%m%d')
        l_training_date_full_path_name = pPredictDir.replace(lPredicionBaseFolderName,l_training_date_in_string) 
        if (os.path.exists(l_training_date_full_path_name)):
            countOfDaysTaken += 1
        if countOfDaysTaken == int(pNumOfTrainingDays):
            break            
    return l_training_date_full_path_name

def getListOfTrainingDirectoriesNames(pNumOfTrainingDays,pStartTrainingDirectory,pInstType="data"):
    global instType
    if pInstType == None:
        pInstType = "data"
    lTrainingDirectoryList = []
    l_training_day_folder_base_date = os.path.basename(os.path.abspath(pStartTrainingDirectory))
    l_start_training_date = datetime.strptime(l_training_day_folder_base_date, '%Y%m%d')
    index = 0
    countOfDaysTaken = 0
    while(1):
        l_training_date = l_start_training_date + timedelta(days = index)
        index = index + 1 
        if( l_training_date.weekday() == 5 or l_training_date.weekday() == 6): # Day is monday
            continue
        l_training_date_in_string = l_training_date.strftime('%Y%m%d')
        l_training_date_full_path_name = pStartTrainingDirectory.replace(l_training_day_folder_base_date,l_training_date_in_string)
#        print l_training_date_full_path_name , l_training_date_full_path_name+"/*ICICI*"
        if (os.path.exists(l_training_date_full_path_name)):
            lRoDir = l_training_date_full_path_name.replace('/wf/','/ro/')
            lRoDir = lRoDir.replace('/rs/','/ro/')
            listOfFiles = commands.getoutput('ls -1 '+ lRoDir).split("\n")
            for file in listOfFiles:
                print file
                if pInstType.strip() in file:
                    lTrainingDirectoryList.append(l_training_date_full_path_name)
                    countOfDaysTaken += 1
                    break
                    
        if countOfDaysTaken == int(pNumOfTrainingDays):
            break
    print lTrainingDirectoryList
    return lTrainingDirectoryList

def callRProgramToConvertToBinary(pFileName):
    lastPointInFileName = pFileName.rfind(".") 
    lFileWithoutExtension= pFileName[:lastPointInFileName]
    lVariableName = (lFileWithoutExtension.split("/")[-1])
    lVariableName = lVariableName.replace("[","")
    lVariableName = lVariableName.replace("]","")
    lVariableName = lVariableName.split("-")[0]
    lNameAfterDecimal = pFileName.split(".")[-1] 
    lFileNameToStore = pFileName.replace(lNameAfterDecimal,"bin")
    
    lCommandToConvertToBinary = "./src/rScriptSaveFeatureFileInBinaryFormat.r " + pFileName + " " + lVariableName + " " + lFileNameToStore
    
    os.system(lCommandToConvertToBinary)

def checkIfAttributeOutputFileExists(pGeneratorName,number,columnName,orderType,diffPip,dataFolder):
    attributeFile = getOutputFileNameFromGeneratorName(pGeneratorName,number,columnName,orderType,diffPip,dataFolder)
    print "Checking if attribute file exists " + attributeFile 
    if (os.path.isfile(attributeFile)):
        print "The attribute has already been generated. If you want to re-generate it then first delete the attribute file."
        lNameAfterDecimal = attributeFile.split(".")[-1] 
        attributeBinaryFileName = attributeFile.replace(lNameAfterDecimal,"bin")
        if (os.path.isfile(attributeBinaryFileName)):
            print   attributeBinaryFileName
            os._exit(0)  # We do not take it as a error condition hence return 0 and not -1
        else:
            callRProgramToConvertToBinary(attributeFile) 
            os._exit(0) 
        
def writeToFile(outputFileName,pListOfHeaderColNames):
    global aList
    print "Writing to file the attribute: "+ outputFileName
    attributeFile = open(outputFileName,"w")
    lHeaderString = ";".join(pListOfHeaderColNames) + "\n"
    attributeFile.write(lHeaderString)
    for featureRow in aList:
        featureCount = 1
        for feature in featureRow:
            attributeFile.write("%s" % (feature))
            if(featureCount < len(featureRow)):
                attributeFile.write(";")
            featureCount = featureCount + 1   
        attributeFile.write('\n')

def initList():
    global aList
    aList =  [[0 for x in xrange(4)] for x in xrange(len(dataFile.matrix))]

def initializeInstDetails(pInstType,pStrikePrice,pOptionType,pRev=None):
    global instType
    global optionsType
    global strikePrice
    global rev
    instType = pInstType
    optionsType = pOptionType
    strikePrice = pStrikePrice
    rev = pRev
    
         
