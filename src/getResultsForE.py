#!/usr/bin/python
import argparse,os
from datetime import datetime
import utility

parser = argparse.ArgumentParser(description='This program will do the 5 steps necessary to get the results for an experiment. \n \
The 5 steps are: \n \
1. Attribute generation  \n \
2. R code generation  \n \
3. R code running.  \n \
4. CMatrix generation  \n \
5. Doing the trading.   \n \
An e.g. command line >getResultsForE.py -e ob/e3.71/ -td ob/data/20140204/ -pd ob/data/20140205/ -m ob/generators/ ', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-e', required=True,help='Directory of the experiment')
parser.add_argument('-a', required=False,help='Algorithm name. This is optional and defaults to glmnet.')
parser.add_argument('-td', required=True,help='Training directory')
parser.add_argument('-pd', required=True,help='Prediction directory')
parser.add_argument('-g', required=True,help='Generators directory')
args = parser.parse_args()


import subprocess

if args.a is not None:
    algo = args.a
else:
    algo = 'glmnet'

# only run the set of programs if the trading results file does not exist

fName = args.pd + "r/" + os.path.basename(os.path.abspath(args.e)) + algo +".55-.45.trade"
if os.path.isfile(fName):
    print "The results file already exists delete it if you want to run the experiment again"
else:
    utility.runProgram(["aGenForE.py","-e",args.e,"-d",args.td,"-g",args.g])        
    utility.runProgram(["aGenForE.py","-e",args.e,"-d",args.pd,"-g",args.g])        
    utility.runProgram(["genAllRScriptsForE.py","-e",args.e,"-a",algo])
    utility.runProgram(["runAllRScriptsForE.py","-td",args.td,"-pd",args.pd,"-e",args.e,"-a",algo])
    utility.runProgram(["cMatrixGen.py","-d",args.pd,"-e",args.e,"-a",algo])
    utility.runProgram(["./ob/quality/tradeE1.py","-d",args.pd,"-e",args.e,"-a",algo,"-entryCL",".55","-exitCL",".45"])
