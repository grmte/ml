import os
import dataFile

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
   fileHasHeader = 0
   for dataRow in open(pFeatureFile):
      if(fileHasHeader == 1 and headerSkipped != 1):
         headerSkipped = 1 
         continue
      dataRow=dataRow.rstrip('\n')
      dataColumns=dataRow.split(',')
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
            value = float(firstMatrix[currentRowCount][1]) / float(secondMatrix[currentRowCount][1])
         elif(pOperand == "Add"):
            value = float(firstMatrix[currentRowCount][1]) + float(secondMatrix[currentRowCount][1])
         elif(pOperand == "Subtract"):
            value = float(firstMatrix[currentRowCount][1]) - float(secondMatrix[currentRowCount][1])
         elif(pOperand == "MultiplyBy"):
            value = float(firstMatrix[currentRowCount][1]) * float(secondMatrix[currentRowCount][1])
         featureMatrix.append([timeStamp,value,firstMatrix[currentRowCount][1],pOperand,secondMatrix[currentRowCount][1]])

      currentRowCount += 1   

   return featureMatrix   

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
   


def checkIfAttributeOutputFileExists(pGeneratorName,number,columnName,dataFolder):
   attributeFile = getOutputFileNameFromGeneratorName(pGeneratorName,number,columnName,dataFolder)
   print "Checking if attribute file exists " + attributeFile 
   if (os.path.isfile(attributeFile)):
      print "The attribute has already been generated. If you want to re-generate it then first delete the attribute file."
      os._exit(0)  # We do not take it as a error condition hence return 0 and not -1

def writeToFile(outputFileName):
   print "Writing to file the attribute: "+ outputFileName
   attributeFile = open(outputFileName,"w")
   for featureRow in aList:
      featureCount = 1
      for feature in featureRow:
         attributeFile.write("%s" % (feature))
         if(featureCount < len(featureRow)):
            attributeFile.write(",")
         featureCount = featureCount + 1   
      attributeFile.write('\n')

def initList():
   global aList
   aList =  [[0 for x in xrange(4)] for x in xrange(len(dataFile.matrix))]
