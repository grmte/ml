#!/usr/local/bin/pypy

"""
attribute generator
"""


import dataFile
import colNumberOfData
import attribute
import common

import os, sys, importlib, traceback

import argparse

def parseCommandLine():
    parser = argparse.ArgumentParser(description='This program will run aGen.py given a generator. An e.g. command line is aGen.py -d ob/data/ro/20140204/ -g ob/generators/fColCInCurrentRow -c BidP0')
    parser.add_argument('-d', required=True,help='Directory of data file')
    parser.add_argument('-iT',required=False,help='Instrument name')
    parser.add_argument('-sP',required=False,help='Strike price of instrument')
    parser.add_argument('-oT',required=False,help='Options Type')
    # This is a command and it does not have sub commands. Hence it does not need 
    # 1. A "sequence of commands" as a parameter.
    # 2. Whether the command is to be run in dry more or real mode.
    args = parser.parse_args()
    return args

args = parseCommandLine()

def main():
#   try:
      attribute.initializeInstDetails(args.iT,args.sP,args.oT) 
      dataFile.getDataIntoMatrix(args.d)
      attribute.checkIfNewDataFileExists(args.d)
      newFileName = dataFile.getNewDataFileName(args.d)
      header = "Instrument;AskQ0;AskP0;AskQ1;AskP1;AskQ2;AskP2;AskQ3;AskP3;AskQ4;AskP4;BidQ0;BidP0;BidQ1;BidP1;BidQ2;BidP2;BidQ3;BidP3;BidQ4;BidP4;TTQ;LTP;LTQ;LTT;ATP;TBQ;TSQ;CP;OP;HP;LP;TimeStamp;SerialNo;MsgCode;OrderType;Quantity1;Price1;Quantity2;Price2;ExchangeTS;BestBidQ;BestBidP;BestAskQ;BestAskP\n"
      print newFileName
      newFileObject = open(newFileName,"w")
      newFileObject.write(header)
      previousLine = ""
      currentRowCount = 0
      for dataRow in dataFile.matrix:
        
        lineWithoutBestPrices = ";".join(dataRow[:colNumberOfData.TTQ])
        if previousLine <> lineWithoutBestPrices:
            newFileObject.write(";".join(dataRow) + "\n")
            previousLine = lineWithoutBestPrices
        currentRowCount = currentRowCount + 1
        if(currentRowCount % 1000 == 0):
            print "Processed row number " + str(currentRowCount)
    
          
#   except:
#      traceback.print_exc()
#      e = sys.exc_info()[0]
#      print e
#      os._exit(-1)

if __name__ == "__main__":
   main()

