#!/usr/bin/python
import argparse
import utility
from configobj import ConfigObj
 
parser = argparse.ArgumentParser(description='This program will run mGen.py and pGen.py. An e.g. command line is\n\
rGenForAllSubE.py -e ob/e/9.1/ -a glmnet -run dry -sequence serial -targetClass multinomial -pd ob/data/ro/20140205 -skipM yes -skipP yes -mpMearge yes', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-e', required=True,help='Directory of the experiment')
parser.add_argument('-a', required=True,help='Algorithm name')
parser.add_argument('-run', required=False,help='real or dummy run')
parser.add_argument('-sequence', required=False,help='ld / pd / serial')
parser.add_argument('-pd', required=True,help='Prediction directory')
parser.add_argument('-td',required=True,help='Training Directory')
parser.add_argument('-dt',required=False,help='No of day from start for which it is to be trained ')
parser.add_argument('-targetClass',required=True,help="binomial(target takes only true and false) / multinomial (target values takes more than 2 values)")
parser.add_argument('-skipM',required=False,help="yes or no , If you want to regenerate already generated algorithm model file then make this value No")
parser.add_argument('-skipP',required=False,help="yes or no , If you want to regenerate already generated algorithm prediction file then make this value No")
parser.add_argument('-mpMearge',required=True,help="yes or no , If you want to separate model and prediction files then make this no")
args = parser.parse_args()

if args.skipM == None:
    args.skipM = "yes"
if args.skipP == None:
    args.skipP = "yes"
if args.dt == None:
    args.dt = "1"
        
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
        if args.mpMearge == "yes":
            utility.runCommand(["mpRGenForAllSubE.py","-e",args.e,"-a",algo,"-targetClass",args.targetClass,"-pd",args.pd ,"-skipP",args.skipP ,"-skipM",args.skipM,\
                                "-td",args.td, "-dt" , args.dt , "-s",args.e+"/s/"+str(i)+"c"],args.run,args.sequence)
        else:
            utility.runCommand(["mRGenForAllSubE.py","-e",args.e,"-a",algo,"-targetClass",args.targetClass,"-pd",args.pd ,"-td" , args.td , "-dt", args.dt,"-skipM",args.skipM,"-s",args.e+"/s/"+str(i)+"c"],args.run,args.sequence)
            utility.runCommand(["pRGenForAllSubE.py","-e",args.e,"-a",algo,"-skipP",args.skipP ,"-targetClass",args.targetClass,"-pd",args.pd ,"-td" , args.td , "-dt", args.dt , "-s",args.e+"/s/"+str(i)+"c"],args.run,args.sequence)
        i +=1
