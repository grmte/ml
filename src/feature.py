import os
import fGenArgs
import dataFile

vector = []


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
