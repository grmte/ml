#!/usr/bin/python
import argparse
import utility
from configobj import ConfigObj
 
parser = argparse.ArgumentParser(description='This program will run mGen.py and pGen.py. An e.g. command line is rGenAll.py -e e1/')
parser.add_argument('-e', required=True,help='Directory of the experiment')
parser.add_argument('-a', required=True,help='Algorithm name')
parser.add_argument('-run', required=False,help='real or dummy run')
args = parser.parse_args()




if args.a is not None:
    allAlgos = [args.a]
else:
    allAlgos = ['logitr','glmnet','randomForest']

config = ConfigObj(args.e+"/design.ini")
features = config["features"]
totalNumberOfFeatures = len(features)

i = 2
for algo in allAlgos:
    while i <= totalNumberOfFeatures:
        utility.runProgram(["mRScriptGenForSubE.py","-e",args.e,"-a",algo,"-s",args.e+"/s/"+str(i)+"c"],args)
        utility.runProgram(["pRScriptGenForSubE.py","-e",args.e,"-a",algo,"-s",args.e+"/s/"+str(i)+"c"],args)
        i +=1
