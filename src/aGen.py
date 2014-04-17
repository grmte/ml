#!/usr/local/bin/pypy

"""
attribute generator
"""



import os, sys, importlib, traceback

import dataFile,argparse
import attribute


def parseCommandLine():
    parser = argparse.ArgumentParser(description='This program will run aGen.py for all attributes required for an experiement. An e.g. command line is aGenAll.py -d ob/data/20140207/ -e e7.1')
    parser.add_argument('-d', required=True,help='Directory of data file')
    parser.add_argument('-g', required=True,help='Directory of geneartors')
    parser.add_argument('-c', required=False,help='Column name')
    parser.add_argument('-n', required=False,help='Number of rows / cols / seconds / Qty')
    parser.add_argument('-run', required=True,help='dry or real')
    parser.add_argument('-sequence', required=True,help='dp / lp / serial')
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
      dataFile.getDataIntoMatrix(args.d)
      attribute.initList()
      userModule.extractAttributeFromDataMatrix(args)
      attribute.writeToFile(os.path.basename(moduleName),args.n,args.c,args.d)
   except:
      traceback.print_exc()
      e = sys.exc_info()[0]
      print e
      os._exit(-1)

if __name__ == "__main__":
   main()
