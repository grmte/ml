#!/usr/bin/python
import argparse
import utility

parser = argparse.ArgumentParser(description='This program will run mGen.py and pGen.py. An e.g. command line is \n\
rGenForE.py -e ob/e/9.1/ -a glmnet -sequence serial -targetClass multinomial -skipM Yes -pd ob/data/ro/20140205 -skipP Yes', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-e', required=True,help='Directory of the experiment')
parser.add_argument('-a', required=False,help='Algorithm name')
parser.add_argument('-run', required=False,help='dry or real')
parser.add_argument('-sequence', required=False,help='lp / dp / serial')
parser.add_argument('-targetClass',required=True,help="binomial(target takes only true and false) / multinomial (target values takes more than 2 values)")
parser.add_argument('-skipM',required=False,help="yes or no , If you want to regenerate already generated algorithm model file then make this value No")
parser.add_argument('-skipP',required=False,help="yes or no , If you want to regenerate already generated algorithm prediction file then make this value No")
parser.add_argument('-pd', required=True,help='Prediction directory')
args = parser.parse_args()

if args.skipM == None:
    args.skipM = "yes"
if args.skipP == None:
    args.skipP = "yes"
    
import subprocess

if args.a is not None:
    allAlgos = [args.a]
else:
    allAlgos = ['logitr','glmnet','randomForest']



for algo in allAlgos:
    utility.runCommand(["mRGenForE.py","-e",args.e,"-a",algo,"-targetClass",args.targetClass,"-skipM",args.skipM],args.run,args.sequence)
    utility.runCommand(["pRGenForE.py","-e",args.e,"-a",algo,"-skipP",args.skipP,"-d",args.pd  ],args.run,args.sequence)
