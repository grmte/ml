#!/usr/bin/python
from configobj import ConfigObj
import subprocess
import feature
import argparse

parser = argparse.ArgumentParser(description='This program will run fGen.py for all features required for an experiement. An e.g. command line is fGenAll.py -d ob/data/20140207/ -e e7.1')
parser.add_argument('-d', required=True,help='Directory of data file')
parser.add_argument('-e', required=True,help='Directory of experiement')
parser.add_argument('-m', required=True,help='Directory of geneartors')
args = parser.parse_args()


config = ConfigObj(args.e+"/design.ini")
features = config["features"]

def runCommandLine(pFeatureName):
    paramList = []
    paramList = ["fGen.py","-d",args.d]
    if "Col" in pFeatureName:
        startPos = pFeatureName.find("Col") + 3
        endPos = pFeatureName.find("In")
        colName = pFeatureName[startPos:endPos]
        pFeatureName = pFeatureName.replace(colName,"C")
        paramList.append("-c")
        paramList.append(colName)

    if "Last" in pFeatureName:
        startPos = pFeatureName.find("Last") + 4
        endPos = pFeatureName.find("Rows")
        N = pFeatureName[startPos:endPos]
        pFeatureName = pFeatureName.replace(N,"N")
        paramList.append("-n")
        paramList.append(N)

    paramList.append("-m")
    paramList.append(args.m+pFeatureName)

    print paramList
    subprocess.call(paramList)

for f in features:
    featureName = features[f]
    print "\nGenerating for " + featureName

    if "DivideBy" in featureName:
        startPos = featureName.find("[")
        endPos = featureName.find("]") + 1
        firstFeatureName = featureName[0:startPos]
        secondFeatureName = featureName[endPos:]
        runCommandLine(firstFeatureName)
        runCommandLine(secondFeatureName)
        feature.vector = feature.divideFeatures(firstFeatureName,secondFeatureName)
        feature.writeToFile(featureName)
        continue

    runCommandLine(featureName)

    
