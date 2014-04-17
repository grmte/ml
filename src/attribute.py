import os
import dataFile

list = []

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
   paramList = ["operateOnAttribute.py","-d",dataFolder]  
   paramList.append("-a1")
   paramList.append(pFirstAttributeName)  
   paramList.append("-a2")
   paramList.append(pSecondAttributeName)  
   paramList.append("-operand")
   paramList.append(pOperand)  
   return paramList

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
   

def getOutputFileNameFromGeneratorName(pAttributesName,number,columnName,dataFolder):
   if "NRows" in pAttributesName:
      N = number
      pAttributesName = pAttributesName.replace("NRows",str(N)+"Rows")   

   if "NSecs" in pAttributesName:
      N = number
      pAttributesName = pAttributesName.replace("NSecs",str(N)+"Secs")   

   if "NQty" in pAttributesName:
      N = number
      pAttributesName = pAttributesName.replace("NQty",str(N)+"Qty")   

   if "ColC" in pAttributesName:
      pAttributesName = pAttributesName.replace("ColC","Col"+columnName)   

   # we need to replace /ro with /wf   
   dirName = dataFolder.replace('/ro/','/wf/')   
   if (getAttributeTypeFromAttributeName(pAttributesName) == "feature"):   
      attributeFile=dirName+"/f/"+pAttributesName+".feature"
   else:   
      attributeFile=dirName+"/t/"+pAttributesName+".target"
      
   return attributeFile
   


def checkIfAttributeOutputFileExists(pAttributesName,number,columnName,dataFolder):
   attributeFile = getOutputFileNameFromAttributeName(pAttributesName,dataFolder)
   print "Checking if attribute file exists " + attributeFile 
   if (os.path.isfile(attributeFile)):
      print "The attribute has already been generated. If you want to re-generate it then first delete the attribute file."
      os._exit(0)  # We do not take it as a error condition hence return 0 and not -1

def writeToFile(pAttributesName,number,columnName,dataFolder):
   print "Writing to file the attribute: "+pAttributesName
   attributeFile = open(getOutputFileNameFromAttributeName(pAttributesName,dataFolder),"w")
   for featureRow in list:
      featureCount = 1
      for feature in featureRow:
         attributeFile.write("%s" % (feature))
         if(featureCount < len(featureRow)):
            attributeFile.write(",")
         featureCount = featureCount + 1   
      attributeFile.write('\n')

def initList():
   global list
   list =  [[0 for x in xrange(4)] for x in xrange(len(dataFile.matrix))]
