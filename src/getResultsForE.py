#!/usr/bin/python
import argparse,os
from datetime import datetime

parser = argparse.ArgumentParser(description='This program will run train-algo.r and predict-algo.r. An e.g. command line ~/ml/>getResultsForE.py -e ob/e3.71/ -td ob/data/20140204/ -pd ob/data/20140205/ -m ob/generators/ ')
parser.add_argument('-e', required=True,help='Directory of the experiment')
parser.add_argument('-a', required=False,help='Algorithm name. This is optional and defaults to glmnet.')
parser.add_argument('-td', required=True,help='Training directory')
parser.add_argument('-pd', required=True,help='Prediction directory')
parser.add_argument('-m', required=True,help='Generators directory')
args = parser.parse_args()


import subprocess

if args.a is not None:
    algo = args.a
else:
    algo = 'glmnet'

def runProgram(pProgDefinationList):
    tStart = datetime.now()
    returnState = subprocess.check_call(pProgDefinationList)
    tEnd = datetime.now()
    if(returnState < 0):
        print "Unrecoverable error code: " + str(returnState)
        os._exit(-1)
    else:
        print "Time taken to run the program is " + str(tEnd - tStart)

runProgram(["aGenForE.py","-e",args.e,"-d",args.td,"-m",args.m])        
runProgram(["aGenForE.py","-e",args.e,"-d",args.pd,"-m",args.m])
runProgram(["rGenForE.py","-e",args.e,"-a",algo])
runProgram(["rRunForE.py","-td",args.td,"-pd",args.pd,"-e",args.e,"-a",algo])
runProgram(["cMatrixGen.py","-d",args.pd,"-e",args.e,"-a",algo])
runProgram(["./ob/quality/trade.py","-d",args.pd,"-e",args.e,"-a",algo,"-entryCL",".55","-exitCL",".45"])
