#!/usr/bin/python
from configobj import ConfigObj

import argparse
parser = argparse.ArgumentParser(description='This program will run fGen.py for all features required for an experiement. An e.g. command line is fGenAll.py -d ob/data/20140207/ -e e7.1')
parser.add_argument('-d', required=True,help='Directory of data file')
parser.add_argument('-e', required=True,help='Directory of experiement')
parser.add_argument('-m', required=True,help='Directory of geneartors')
args = parser.parse_args()


config = ConfigObj(args.e+"/design.ini")
features = config["features"]

import subprocess

for feature in features:
    featureName = features[feature]
    print "\nGenerating for " + featureName

    paramList = []
    paramList = ["fGen.py","-d",args.d]

    if "Col" in featureName:
        startPos = featureName.find("Col") + 3
        endPos = featureName.find("In")
        colName = featureName[startPos:endPos]
        featureName = featureName.replace(colName,"C")
        paramList.append("-c")
        paramList.append(colName)

    if "Last" in featureName:
        startPos = featureName.find("Last") + 4
        endPos = featureName.find("Rows")
        N = featureName[startPos:endPos]
        featureName = featureName.replace(N,"N")
        paramList.append("-n")
        paramList.append(N)

    paramList.append("-m")
    paramList.append(args.m+featureName)

    print paramList
    subprocess.call(paramList)
    
