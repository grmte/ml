import os
import fGenArgs
import dataFile

vector = []

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

   featureFile=fGenArgs.args.d+"/"+pFeatureName+".feature"
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
