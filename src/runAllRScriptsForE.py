#!/usr/bin/python
import argparse
import utility
import os
import attribute

parser = argparse.ArgumentParser(description='This program will run train-algo.r and predict-algo.r. An e.g. command line ~/ml/ob>rRunForE.py -e e3.6/ -td data/20140204/ -pd data/20140205/')
parser.add_argument('-e', required=True,help='Directory of the experiment')
parser.add_argument('-a', required=False,help='Algorithm name')
parser.add_argument('-td', required=True,help='Training directory')
parser.add_argument('-pd', required=True,help='Prediction directory')
parser.add_argument('-run', required=True,help='dry or real')
parser.add_argument('-sequence', required=True,help='lp / dp / serial')
parser.add_argument('-dt',required=False,help='No of day from start for which it is to be trained ')
args = parser.parse_args()


if args.a is not None:
    algo = args.a
else:
    algo = 'glmnet'

if args.dt == None:
    args.dt = "1"

dirName = args.td.replace('/ro/','/wf/')
scriptName=args.e+"/train" + algo + "-td." + os.path.basename(os.path.abspath(args.td)) + "-dt." + os.path.basename(os.path.abspath(args.dt)) + ".r"
trainingDataList = attribute.getListOfTrainingDirectoriesNames(args.dt,dirName)
trainingDataListString = "\"" + ";".join(trainingDataList) + "\""
utility.runCommand([scriptName,"-d",trainingDataListString],args.run,args.sequence)

dirName = args.pd.replace('/ro/','/wf/')    
scriptName=args.e+"/predict" + algo + "-td." + os.path.basename(os.path.abspath(args.td)) + "-dt." + args.dt + "-pd"  + os.path.basename(os.path.abspath(args.pd)) + ".r"
utility.runCommand([scriptName,"-d",dirName],args.run,args.sequence)



