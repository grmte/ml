import os
import dataFile
from datetime import timedelta
from datetime import datetime

aList = []


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
   paramList = []                        
   paramList = ["operateOnAttributes.py","-d",dataFolder]  
   paramList.append("-a1")
   paramList.append(pFirstAttributeName)  
   paramList.append("-a2")
   paramList.append(pSecondAttributeName)  
   paramList.append("-operand")
   paramList.append(pOperand)  
   return paramList

def getFileNameFromOperationCommand(a1,a2,operand,d):
   # assuming that all operations happen on f to operate on t this function needs to change.
   d = d.replace('/ro/','/wf/')   
   return d+"/f/"+a1+"["+operand+"]"+a2+".feature"

def operateOnAttributes(pFirstAttributeName,pSecondAttributeName,pOperand,dataFolder):
   print "\nOperating on attributes. First attribute: "+pFirstAttributeName + " 2nd attribute: "+pSecondAttributeName + " Operation: "+ pOperand
   featureMatrix = [] 
   firstFileName = getOutputFileNameFromAttributeName(pFirstAttributeName,dataFolder)
   secondFileName = getOutputFileNameFromAttributeName(pSecondAttributeName,dataFolder)
   
   firstMatrix = readAttributeFileIntoMatrix(firstFileName)
   secondMatrix = readAttributeFileIntoMatrix(secondFileName)

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
         featureMatrix.append([timeStamp,value,firstMatrix[currentRowCount][1],pOperand,secondMatrix[currentRowCount][1]])

      currentRowCount += 1   
   lListOfHeaderColNames = ["TimeStamp","Value","Operand1","Operator","Operand2"]
   return featureMatrix , lListOfHeaderColNames   

def getAttributeTypeFromAttributeName(pAttributeName):
   if(pAttributeName[0]=='f'):
      return "feature"
   else:
      return "target"
   

def getOutputFileNameFromAttributeName(pAttributesName,dataFolder):
   # we need to replace /ro with /wf   
   dirName = dataFolder.replace('/ro/','/wf/')   
   if (getAttributeTypeFromAttributeName(pAttributesName) == "feature"):   
      attributeFile=dirName+"/f/"+pAttributesName+".feature"
   else:   
      attributeFile=dirName+"/t/"+pAttributesName+".target"
      
   return attributeFile
   

def getOutputFileNameFromGeneratorName(pGeneratorName,number,columnName,dataFolder):
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

   if "ColC" in pGeneratorName:
      pGeneratorName = pGeneratorName.replace("ColC","Col"+columnName)   

   # we need to replace /ro with /wf   
   dirName = dataFolder.replace('/ro/','/wf/')   
   if (getAttributeTypeFromAttributeName(pGeneratorName) == "feature"):   
      attributeFile=dirName+"/f/"+pGeneratorName+".feature"
   else:   
      attributeFile=dirName+"/t/"+pGeneratorName+".target"
      
   return attributeFile
   
def getListOfTrainingDirectoriesNames(pNumOfTrainingDays,pStartTrainingDirectory):
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
        lTrainingDirectoryList.append(l_training_date_full_path_name)
        countOfDaysTaken += 1
        if countOfDaysTaken == int(pNumOfTrainingDays):
           break
    return lTrainingDirectoryList

def checkIfAttributeOutputFileExists(pGeneratorName,number,columnName,dataFolder):
   attributeFile = getOutputFileNameFromGeneratorName(pGeneratorName,number,columnName,dataFolder)
   print "Checking if attribute file exists " + attributeFile 
   if (os.path.isfile(attributeFile)):
      print "The attribute has already been generated. If you want to re-generate it then first delete the attribute file."
      os._exit(0)  # We do not take it as a error condition hence return 0 and not -1

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
