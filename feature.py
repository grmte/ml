import os
import commonArgs
import dataFile

vector = []


def writeToFile(pProgName):
   featureName = pProgName
   featureFile=open(commonArgs.args.d+"/"+featureName+".feature","w")
   for featureRow in vector:
      for feature in featureRow:
         featureFile.write("%s," % (feature))
      featureFile.write('\n')

def initVector():
   global vector
   vector =  [[0 for x in xrange(2)] for x in xrange(len(dataFile.matrix))]
