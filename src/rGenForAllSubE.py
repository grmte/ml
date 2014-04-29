#!/usr/bin/python
import argparse
import utility
from configobj import ConfigObj
 
parser = argparse.ArgumentParser(description='This program will run mGen.py and pGen.py. An e.g. command line is rGenAll.py -e e1/')
parser.add_argument('-e', required=True,help='Directory of the experiment')
parser.add_argument('-a', required=True,help='Algorithm name')
parser.add_argument('-run', required=False,help='real or dummy run')
parser.add_argument('-sequence', required=False,help='ld / pd / serial')
parser.add_argument('-targetClass',required=True,help="binomial(target takes only true and false) / multinomial (target values takes more than 2 values)")
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
        utility.runCommand(["mRGenForAllSubE.py","-e",args.e,"-a",algo,"-targetClass",args.targetClass,"-s",args.e+"/s/"+str(i)+"c"],args.run,args.sequence)
        utility.runCommand(["pRGenForAllSubE.py","-e",args.e,"-a",algo,"-s",args.e+"/s/"+str(i)+"c"],args.run,args.sequence)
        i +=1
