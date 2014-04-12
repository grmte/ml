#!/usr/bin/python
import argparse
import utility

parser = argparse.ArgumentParser(description='This program will run train-algo.r and predict-algo.r. An e.g. command line ~/ml/ob>rRunForE.py -e e3.6/ -td data/20140204/ -pd data/20140205/')
parser.add_argument('-e', required=True,help='Directory of the experiment')
parser.add_argument('-a', required=False,help='Algorithm name')
parser.add_argument('-td', required=True,help='Training directory')
parser.add_argument('-pd', required=True,help='Prediction directory')
parser.add_argument('-run', required=True,help='dry or real')
args = parser.parse_args()


import subprocess

if args.a is not None:
    algo = args.a
else:
    algo = 'glmnet'


dirName = args.td.replace('/ro/','/wf/')
scriptName=args.e+"/train-"+algo+".r"
utility.runProgram([scriptName,"-d",dirName],args)

dirName = args.pd.replace('/ro/','/wf/')    
scriptName=args.e+"/predict-"+algo+".r"
utility.runProgram([scriptName,"-d",dirName],args)



