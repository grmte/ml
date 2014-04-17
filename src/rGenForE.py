#!/usr/bin/python
import argparse
import utility

parser = argparse.ArgumentParser(description='This program will run mGen.py and pGen.py. An e.g. command line is rGenAll.py -e e1/')
parser.add_argument('-e', required=True,help='Directory of the experiment')
parser.add_argument('-a', required=False,help='Algorithm name')
parser.add_argument('-run', required=False,help='dry or real')
args = parser.parse_args()


import subprocess

if args.a is not None:
    allAlgos = [args.a]
else:
    allAlgos = ['logitr','glmnet','randomForest']



for algo in allAlgos:
    utility.runCommand(["mRScriptGenForE.py","-e",args.e,"-a",algo],args)
    utility.runCommand(["pRScriptGenForE.py","-e",args.e,"-a",algo],args)
