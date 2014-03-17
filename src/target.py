import os
import dataFile
import tGenArgs

vector = []

def checkIfTargetFileExists(pProgName):
   targetName = pProgName
   targetFile=tGenArgs.args.d+"/t/"+targetName+".target"
   print "Checking if target file exists " + targetFile + " \n"
   if (os.path.isfile(targetFile)):
      print "The target has already been generated. If you want to re-generate it then first delete the target file"
      os._exit(-1)

def writeToFile(pProgName):
   targetName = pProgName
   targetFile=open(tGenArgs.args.d+"/t/"+targetName+".target","w")
   for targetRow in vector:
      targetCount = 1
      for target in targetRow:
         targetFile.write("%s" % (target))
         if(targetCount < len (targetRow)):
            targetFile.write(",")
         targetCount = targetCount + 1
      targetFile.write('\n')   

def initVector():
   global vector
   vector =  [[0 for x in xrange(2)] for x in xrange(len(dataFile.matrix))]
