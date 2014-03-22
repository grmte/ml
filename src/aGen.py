#!/usr/bin/python
import os
import sys
import importlib

import dataFile
import fGenArgs
import feature

sys.path.append(os.path.dirname(fGenArgs.args.m))
try:
   import colNumberOfData
except:
   print "There is some problem with the path. I cannot import colNumberOfData"
   os._exit(-1)

moduleName = os.path.basename(fGenArgs.args.m)
moduleName = os.path.splitext(moduleName)[0]
userModule = importlib.import_module(moduleName)

def main():
   feature.checkIfFeatureFileExists(os.path.basename(moduleName))
   dataFile.getDataIntoMatrix(fGenArgs.args.d)
   feature.initVector()
   userModule.extractFeatureFromDataMatrix()
   feature.writeToFile(os.path.basename(moduleName))

if __name__ == "__main__":
    main()
