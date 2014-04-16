import os
import dataFile

list = []

def readFeatureFileIntoMatrix(pFeatureFile):
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

def operateOnAttributes(pFirstAttributeName,pSecondAttributeName,pOperand,number,columnName,dataFolder):
   print "\nOperating on attributes. First attribute: "+pFirstAttributeName + " 2nd attribute: "+pSecondAttributeName + " Operation: "+ pOperand
   featureMatrix = [] 
   firstFileName = getFileNameFromAttributeName(pFirstAttributeName,number,columnName,dataFolder)
   secondFileName = getFileNameFromAttributeName(pSecondAttributeName,number,columnName,dataFolder)
   
   firstMatrix = readFeatureFileIntoMatrix(firstFileName)
   secondMatrix = readFeatureFileIntoMatrix(secondFileName)

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
   

def getFileNameFromAttributeName(pAttributesName,number,columnName,dataFolder):
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
   
def checkIfAttributeFileExists(pAttributesName,number,columnName,dataFolder):
   attributeFile = getFileNameFromAttributeName(pAttributesName,number,columnName,dataFolder)
   print "Checking if attribute file exists " + attributeFile 
   if (os.path.isfile(attributeFile)):
      print "The attribute has already been generated. If you want to re-generate it then first delete the attribute file."
      os._exit(0)  # We do not take it as a error condition hence return 0 and not -1

def writeToFile(pAttributesName,number,columnName,dataFolder):
   print "Writing to file the attribute: "+pAttributesName
   attributeFile = open(getFileNameFromAttributeName(pAttributesName,number,columnName,dataFolder),"w")
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
