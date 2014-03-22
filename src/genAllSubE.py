#!/usr/bin/python

import itertools
import argparse
from configobj import ConfigObj

parser = argparse.ArgumentParser(description='This program will run generate all the subexperiments. An e.g. command line is genAllSubE.py -e e1/')
parser.add_argument('-e', required=True,help='Directory of the experiment')
args = parser.parse_args()

config = ConfigObj(args.e+"/design.ini")

features = config["features"]

i = 1
numberOfFeatureSets = 0

while i <= len(features):
    i += 1
    featureSet = list(itertools.combinations(features, i))
    print featureSet
    numberOfFeatureSets += len(featureSet)

print "The total number of features are " + str(len(features))
print "The total number of feature sets are " + str(numberOfFeatureSets)
