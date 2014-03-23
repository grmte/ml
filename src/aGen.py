#!/usr/bin/python
import os
import sys
import importlib

import dataFile
import aGenArgs
import attribute

sys.path.append(os.path.dirname(aGenArgs.args.m))
try:
   import colNumberOfData
   moduleName = os.path.basename(aGenArgs.args.m)
   moduleName = os.path.splitext(moduleName)[0]
   userModule = importlib.import_module(moduleName)
except:
   print "There is some problem with the path. I cannot import required files"
   sys.exit(-1)


def main():
   try:
      attribute.checkIfAttributeFileExists(os.path.basename(moduleName))
      dataFile.getDataIntoMatrix(aGenArgs.args.d)
      attribute.initList()
      userModule.extractAttributeFromDataMatrix()
      attribute.writeToFile(os.path.basename(moduleName))
   except:
      os._exit(-1)

if __name__ == "__main__":
   main()
