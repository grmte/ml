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
    parser.add_argument('-a1', required=True,help='Attribute 1')
    parser.add_argument('-a2', required=False,help='Attribute 2')
    parser.add_argument('-operand', required=False,help='Operand')
    """ 
    this does not need a command sequence since this does not generate sub commands
    this does not need a dry or real since this is the final execution command
    """
    args = parser.parse_args()
    return args

args = parseCommandLine()

def main():
   try:
      outputFileName = attribute.getFileNameFromOperationCommand(args.a1,args.a2,args.operand,args.d)
      if (os.path.isfile(outputFileName)):
          print "The attribute has already been generated. If you want to re-generate it then first delete the attribute file."
          os._exit(0)  # We do not take it as a error condition hence return 0 and not -1
      attribute.aList,lListOfHeaderColNames = attribute.operateOnAttributes(args.a1,args.a2,args.operand,args.d)
      attribute.writeToFile(outputFileName,lListOfHeaderColNames)
   except:
      traceback.print_exc()
      e = sys.exc_info()[0]
      print e
      os._exit(-1)

if __name__ == "__main__":
   main()
