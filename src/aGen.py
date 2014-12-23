#!/usr/local/bin/pypy

"""
attribute generator
"""



import os, sys, importlib, traceback

import dataFile,argparse
import attribute


def parseCommandLine():
    parser = argparse.ArgumentParser(description='This program will run aGen.py given a generator. An e.g. command line is:-\n src/aGen.py -d ob/data/ro/nsefut/20141017/ -g ob/generators/fMovingAverageOfColCInLastNSecs -c BidP0 -n 600 -iT DLF -sP -1 -oT 0')
    parser.add_argument('-d', required=True,help='Directory of data file')
    parser.add_argument('-g', required=True,help='Directory of geneartors')
    parser.add_argument('-c', required=False,help='Column name')
    parser.add_argument('-o', required=False,help='Order type N/X/T')
    parser.add_argument('-cType', required=False,help='primary / synthetic')
    parser.add_argument('-n', required=False,help='Number of rows / cols / seconds / Qty')
    parser.add_argument('-i',required=False,help="Imaginary Name of column")
    parser.add_argument('-tickSize',required=False,help='For NseCurrency data give 25000 and for future options data give 5')
    parser.add_argument('-iT',required=False,help='Instrument name')
    parser.add_argument('-sP',required=False,help='Strike price of instrument')
    parser.add_argument('-oT',required=False,help='Options Type')
    parser.add_argument('-m',required=False,help='Diff Pip')
    parser.add_argument('-rev',required=False,help="Yes/No, whether to take only relevant data row of all data rows")
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
      attribute.initializeInstDetails(args.iT,args.sP,args.oT,args.rev) 
      if args.i is not None: 
          attribute.checkIfAttributeOutputFileExists(os.path.basename(moduleName),args.n,args.i,args.o,args.m,args.d)
      else:
          attribute.checkIfAttributeOutputFileExists(os.path.basename(moduleName),args.n,args.c,args.o,args.m,args.d)
      if args.rev!= None and args.rev.lower()=="yes":
          dataFile.getSelectedDataIntoMatrix(args.d)
      else:
          if(args.cType == "synthetic"):
              dataFile.getDataIntoMatrix(args.d,args.c)
          else:
              dataFile.getDataIntoMatrix(args.d)
      
      attribute.initList()
      lHeaderColumnNamesList = userModule.extractAttributeFromDataMatrix(args)
      if args.i is not None:
          fileName = attribute.getOutputFileNameFromGeneratorName(os.path.basename(moduleName),args.n,args.i,args.o,args.m,args.d )
      else:
          fileName = attribute.getOutputFileNameFromGeneratorName(os.path.basename(moduleName),args.n,args.c,args.o,args.m,args.d )
      print fileName
      attribute.writeToFile(fileName , lHeaderColumnNamesList)
      attribute.callRProgramToConvertToBinary(fileName) 
   except:
      traceback.print_exc()
      e = sys.exc_info()[0]
      print e
      os._exit(-1)

if __name__ == "__main__":
   main()
