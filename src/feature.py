import os
import fGenArgs
import dataFile

vector = []

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

def operateOnFeatures(pFirstFeatureName,pSecondFeatureName,pOperand):
   featureMatrix = [] 
   firstFileName = getFileNameFromFeatureName(pFirstFeatureName)
   secondFileName = getFileNameFromFeatureName(pSecondFeatureName)
   
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
         featureMatrix.append([timeStamp,value])

      currentRowCount += 1   

   return featureMatrix   

def getFileNameFromFeatureName(pFeatureName):
   if "LastNRows" in pFeatureName:
      if fGenArgs.args.n == None:
         N = 5
      else:
         N = fGenArgs.args.n
   
      pFeatureName = pFeatureName.replace("LastNRows","Last"+str(N)+"Rows")   

   if "ColC" in pFeatureName:
      if fGenArgs.args.c == None:
         print "Column name has not been specified"
         os._exit(1)

      pFeatureName = pFeatureName.replace("ColC","Col"+str(fGenArgs.args.c))   

   featureFile=fGenArgs.args.d+"/f/"+pFeatureName+".feature"
   return featureFile
   
def checkIfFeatureFileExists(pFeatureName):
   featureFile = getFileNameFromFeatureName(pFeatureName)
   print "Checking if feature file exists " + featureFile 
   if (os.path.isfile(featureFile)):
      print "The feature has already been generated. If you want to re-generate it then first delete the feature file \n"
      os._exit(-1)

def writeToFile(pFeatureName):
   featureFile = open(getFileNameFromFeatureName(pFeatureName),"w")
   for featureRow in vector:
      featureCount = 1
      for feature in featureRow:
         featureFile.write("%s" % (feature))
         if(featureCount < len(featureRow)):
            featureFile.write(",")
         featureCount = featureCount + 1   
      featureFile.write('\n')

def initVector():
   global vector
   vector =  [[0 for x in xrange(2)] for x in xrange(len(dataFile.matrix))]
