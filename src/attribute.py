import os
import aGenArgs
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

def operateOnAttributes(pFirstAttributeName,pSecondAttributeName,pOperand):
   print "\nOperating on attributes. First attribute: "+pFirstAttributeName + " 2nd attribute: "+pSecondAttributeName + " Operation: "+ pOperand
   featureMatrix = [] 
   firstFileName = getFileNameFromAttributeName(pFirstAttributeName)
   secondFileName = getFileNameFromAttributeName(pSecondAttributeName)
   
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
   

def getFileNameFromAttributeName(pAttributesName):
   if "NRows" in pAttributesName:
      if aGenArgs.args.n == None:
         N = 5
      else:
         N = aGenArgs.args.n
      pAttributesName = pAttributesName.replace("NRows",str(N)+"Rows")   

   if "NSecs" in pAttributesName:
      if aGenArgs.args.n == None:
         N = 5
      else:
         N = aGenArgs.args.n
      pAttributesName = pAttributesName.replace("NSecs",str(N)+"Secs")   

   if "NQty" in pAttributesName:
      if aGenArgs.args.n == None:
         N = 5
      else:
         N = aGenArgs.args.n
      pAttributesName = pAttributesName.replace("NQty",str(N)+"Qty")   

   if "ColC" in pAttributesName:
      if aGenArgs.args.c == None:
         print "Column name has not been specified"
         os._exit(1)
      pAttributesName = pAttributesName.replace("ColC","Col"+str(aGenArgs.args.c))   

   if (getAttributeTypeFromAttributeName(pAttributesName) == "feature"):   
      attributeFile=aGenArgs.args.d+"/f/"+pAttributesName+".feature"
   else:   
      attributeFile=aGenArgs.args.d+"/t/"+pAttributesName+".target"
      
   return attributeFile
   
def checkIfAttributeFileExists(pAttributesName):
   attributeFile = getFileNameFromAttributeName(pAttributesName)
   print "Checking if attribute file exists " + attributeFile 
   if (os.path.isfile(attributeFile)):
      print "The attribute has already been generated. If you want to re-generate it then first delete the attribute file."
      os._exit(0)  # We do not take it as a error condition hence return 0 and not -1

def writeToFile(pAttributesName):
   print "Writing to file the attribute: "+pAttributesName
   attributeFile = open(getFileNameFromAttributeName(pAttributesName),"w")
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
