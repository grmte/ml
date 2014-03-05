import os
import dataFile
import tGenArgs

vector = []

def writeToFile(pProgName):
   targetName = pProgName
   targetFile=open(tGenArgs.args.d+"/"+targetName+".target","w")
   for targetRow in vector:
      for target in targetRow:
         targetFile.write("%s," % (target))
      targetFile.write('\n')   

def initVector():
   global vector
   vector =  [[0 for x in xrange(2)] for x in xrange(len(dataFile.matrix))]
