#!/usr//bin/python
import os
import sys
import importlib

import dataFile
import tGenArgs
import target

sys.path.append(os.path.dirname(tGenArgs.args.m))
try:
   import colNumberOfData
except:
   print "There is some problem with the path. I cannot import colNumberOfData"
   os._exit(-1)

moduleName = os.path.basename(tGenArgs.args.m)
moduleName = os.path.splitext(moduleName)[0]
userModule = importlib.import_module(moduleName)


def main():
   dataFile.getDataIntoMatrix(tGenArgs.args.d)
   target.initVector()
   userModule.extractTargetFromDataMatrix()
   target.writeToFile(os.path.basename(moduleName))

if __name__ == "__main__":
    main()
