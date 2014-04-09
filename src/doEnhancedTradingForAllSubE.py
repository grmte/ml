#!/usr/bin/python

import itertools, os,argparse, subprocess
from configobj import ConfigObj
from datetime import datetime

parser = argparse.ArgumentParser(description='This program will run generate all the subexperiments. An e.g. command line is genAllSubE.py -e e1/')
parser.add_argument('-e', required=True,help='Directory of the experiment')
parser.add_argument('-a', required=True,help='Algorithm name. This is optional and defaults to glmnet.')
parser.add_argument('-d', required=True,help='Prediction directory')
parser.add_argument('-run', required=True,help='Dry or Real')
args = parser.parse_args()

config = ConfigObj(args.e+"/design.ini")
features = config["features"]
i = 1

def runProgram(pProgDefinationList):
    message = "\n Going to run "+' '.join(pProgDefinationList)
    print message
    if(args.run == "Dry"):
        return
    tStart = datetime.now()
    returnState = subprocess.check_call(pProgDefinationList)
    tEnd = datetime.now()
    if(returnState < 0):
        print "Unrecoverable error code: " + str(returnState)
        os._exit(-1)
    else:
        print "Time taken to run the program is " + str(tEnd - tStart)

while i <= len(features):
    i += 1
    # lets make a directory if it does not already exist
    try:
        os.stat(args.e+"/s/"+str(i)+"c")
    except:
        os.mkdir(args.e+"/s/"+str(i)+"c")       

    featureSets = list(itertools.combinations(features, i))
    for featureSet in featureSets:
        try:
            os.stat(args.e+"/s/"+str(i)+"c/"+''.join(featureSet))
        except:
            os.mkdir(args.e+"/s/"+str(i)+"c/"+''.join(featureSet))       
        experimentName = args.e+"/s/"+str(i)+"c/"+''.join(featureSet)+'/'
        runProgram(["./ob/quality/tradeE2.py","-e",experimentName,"-d",args.d,"-a",args.a,"-entryCL",".55","-exitCL",".45"])


