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

user_module = importlib.import_module(os.path.basename(tGenArgs.args.m))


def main():
   dataFile.getDataIntoMatrix(tGenArgs.args.d)
   target.initVector()
   user_module.extractTargetFromDataMatrix()
   target.writeToFile(os.path.basename(tGenArgs.args.m))

if __name__ == "__main__":
    main()
