#!/usr/bin/python


import argparse
parser = argparse.ArgumentParser(description='This program will run train-algo.r and predict-algo.r. An e.g. command line ~/ml/ob>getResultsForE.py -e e3.6/ -td data/20140204/ -pd data/20140205/')
parser.add_argument('-e', required=True,help='Directory of the experiment')
parser.add_argument('-a', required=False,help='Algorithm name')
parser.add_argument('-td', required=True,help='Training directory')
parser.add_argument('-pd', required=True,help='Prediction directory')
parser.add_argument('-m', required=True,help='Generators directory')
args = parser.parse_args()


import subprocess

if args.a is not None:
    algo = args.a
else:
    algo = 'glmnet'

subprocess.call(["fGenForE.py","-e",args.e,"-d",args.td,"-m",args.m])
subprocess.call(["fGenForE.py","-e",args.e,"-d",args.pd,"-m",args.m])
subprocess.call(["rGenForE.py","-e",args.e,"-a",algo])
subprocess.call(["rRunForE.py","-td",args.td,"-pd",args.pd,"-e",args.e,"-a",algo])
subprocess.call(["cMatrixGen.py","-d",args.pd,"-e",args.e,"-a",algo])
