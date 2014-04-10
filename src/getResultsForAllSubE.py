#!/usr/bin/python

import itertools, os,argparse, subprocess
from configobj import ConfigObj
from datetime import datetime
import rCodeGen
import utility

parser = argparse.ArgumentParser(description='This program will run generate all the subexperiments. An e.g. command line is genAllSubE.py -e e1/')
parser.add_argument('-e', required=True,help='Directory of the experiment')
parser.add_argument('-a', required=True,help='Algorithm name.')
parser.add_argument('-td', required=True,help='Training directory')
parser.add_argument('-pd', required=True,help='Prediction directory')
parser.add_argument('-g', required=True,help='Generators directory')
parser.add_argument('-run', required=True,help='Dry or Real')
args = parser.parse_args()

config = ConfigObj(args.e+"/design.ini")
features = config["features"]
i = 1

algo = rCodeGen.getAlgoName(args)

utility.runProgram(["aGenForE.py","-e",args.e,"-d",args.td,"-g",args.g],args)
utility.runProgram(["aGenForE.py","-e",args.e,"-d",args.pd,"-g",args.g],args)
utility.runProgram(["genAllRScriptsForAllSubE.py","-e",args.e,"-a",algo],args)
utility.runProgram(["runAllRScriptsForAllSubE.py","-td",args.td,"-pd",args.pd,"-e",args.e,"-a",algo],args)

dirName=os.path.dirname(args.e)
            
designFiles = utility.list_files(dirName+"/s/")    

for designFile in designFiles:
    experimentName = os.path.dirname(designFile)
    utility.runProgram(["cMatrixGen.py","-d",args.pd,"-e",experimentName,"-a",algo],args)
    utility.runProgram(["./ob/quality/tradeE1.py","-d",args.pd,"-e",experimentName,"-a",algo,"-entryCL",".55","-exitCL",".45"],args)

