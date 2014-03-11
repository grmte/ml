import os
import fGenArgs
import dataFile

vector = []

def checkIfFeatureFileExists(pProgName):
   featureName = pProgName
   featureFile=fGenArgs.args.d+"/"+featureName+".feature"
   print "Checking if feature file exists " + featureFile 
   if (os.path.isfile(featureFile)):
      print "The feature has already been generated. If you want to re-generate it then first delete the feature file \n"
      os._exit(-1)

def writeToFile(pProgName):
   featureName = pProgName
   featureFile=open(fGenArgs.args.d+"/"+featureName+".feature","w")
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
