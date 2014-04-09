#!/usr/bin/python


import argparse
parser = argparse.ArgumentParser(description='This program will run mGen.py and pGen.py. An e.g. command line is rGenAll.py -e e1/')
parser.add_argument('-e', required=True,help='Directory of the experiment')
parser.add_argument('-a', required=False,help='Algorithm name')
args = parser.parse_args()


import subprocess

if args.a is not None:
    allAlgos = [args.a]
else:
    allAlgos = ['logitr','glmnet','randomForest']



for algo in allAlgos:
    subprocess.call(["mRScriptGenForE.py","-e",args.e,"-a",algo])
    subprocess.call(["pRScriptGenForE.py","-e",args.e,"-a",algo])
