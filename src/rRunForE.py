#!/usr/bin/python


import argparse
parser = argparse.ArgumentParser(description='This program will run train-algo.r and predict-algo.r. An e.g. command line ~/ml/ob>rRunForE.py -e e3.6/ -td data/20140204/ -pd data/20140205/')
parser.add_argument('-e', required=True,help='Directory of the experiment')
parser.add_argument('-a', required=False,help='Algorithm name')
parser.add_argument('-td', required=True,help='Training directory')
parser.add_argument('-pd', required=True,help='Prediction directory')
args = parser.parse_args()


import subprocess

if args.a is not None:
    algo = args.a
else:
    algo = 'glmnet'

print "Running train-algo.r to generate the model"
scriptName=args.e+"/train-"+algo+".r"
subprocess.call([scriptName,"-d",args.td])
    
scriptName=args.e+"/predict-"+algo+".r"
print "Running predict-algo.r to generate the predictions"
subprocess.call([scriptName,"-d",args.pd])
