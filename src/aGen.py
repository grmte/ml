#!/usr/local/bin/pypy

"""
attribute generator
"""



import os, sys, importlib, traceback

import dataFile,argparse
import attribute


def parseCommandLine():
    parser = argparse.ArgumentParser(description='This program will run aGen.py given a generator. An e.g. command line is aGen.py -d ob/data/ro/20140204/ -g ob/generators/fColCInCurrentRow -c BidP0')
    parser.add_argument('-d', required=True,help='Directory of data file')
    parser.add_argument('-g', required=True,help='Directory of geneartors')
    parser.add_argument('-c', required=False,help='Column name')
    parser.add_argument('-cType', required=False,help='primary / synthetic')
    parser.add_argument('-n', required=False,help='Number of rows / cols / seconds / Qty')
    # This is a command and it does not have sub commands. Hence it does not need 
    # 1. A "sequence of commands" as a parameter.
    # 2. Whether the command is to be run in dry more or real mode.
    args = parser.parse_args()
    return args

args = parseCommandLine()
sys.path.append(os.path.dirname(args.g))
try:
   import colNumberOfData
   moduleName = os.path.basename(args.g)
   moduleName = os.path.splitext(moduleName)[0]
   userModule = importlib.import_module(moduleName)
except:
   traceback.print_exc()
   e = sys.exc_info()[0]
   print e
   os._exit(-1)
   
   
   


def main():
   try:
      attribute.checkIfAttributeOutputFileExists(os.path.basename(moduleName),args.n,args.c,args.d)
      if(args.cType == "synthetic"):
          dataFile.getDataIntoMatrix(args.d,args.c)
      else:
          dataFile.getDataIntoMatrix(args.d)
      
      attribute.initList()
      lHeaderColumnNamesList = userModule.extractAttributeFromDataMatrix(args)
      fileName = attribute.getOutputFileNameFromGeneratorName(os.path.basename(moduleName),args.n,args.c,args.d)
      attribute.writeToFile(fileName , lHeaderColumnNamesList)
   except:
      traceback.print_exc()
      e = sys.exc_info()[0]
      print e
      os._exit(-1)

if __name__ == "__main__":
   main()
