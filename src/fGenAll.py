#!/usr/bin/python
from configobj import ConfigObj

import argparse
parser = argparse.ArgumentParser(description='This program will run fGen.py for all features required for an experiement. An e.g. command line is fGenAll.py -d ob/data/20140207/ -e e7.1')
parser.add_argument('-d', required=True,help='Directory of data file')
parser.add_argument('-e', required=True,help='Directory of experiement')
args = parser.parse_args()


config = ConfigObj(args.e+"/design.ini")
features = config["features"]

import subprocess

for feature in features:
    featureName = features[feature]
    print "\nGenerating for " + featureName

    if "ColC" in featureName:
        featureName = featureName.replace("ColC","Col"+str(fGenArgs.args.c))

    if "LastNRows" in featureName:
      if fGenArgs.args.n == None:
         N = 5
      else:
         N = fGenArgs.args.n
      featureName = featureName.replace("LastNRows","Last"+str(N)+"Rows")   

    subprocess.call(["fGen.py","-d",args.d,"-m",featureName])
    
