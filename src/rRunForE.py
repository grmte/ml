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

scriptName=args.e+"/train-"+algo+".r"
print "Running "+ scriptName +" to generate the model"
returnState = subprocess.check_call([scriptName,"-d",args.td])
if(returnState < 0):
    print "Unrecoverable error code: " + str(returnState)
    os._exit(-1)
    
scriptName=args.e+"/predict-"+algo+".r"
print "Running "+ scriptName +" to generate the predictions"
returnState = subprocess.check_call([scriptName,"-d",args.pd])
if(returnState < 0):
    print "Unrecoverable error code: " + str(returnState)
    os._exit(-1)


