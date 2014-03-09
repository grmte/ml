#!/usr/bin/python


import argparse
parser = argparse.ArgumentParser(description='This program will run fGen.py for all available features. An e.g. command line is fGenAll.py -d ob/data/20140207/')
parser.add_argument('-d', required=True,help='Directory of data file')
parser.add_argument('-m', required=True,help='Directory of feature generators')
args = parser.parse_args()

import glob
AllFeatureGenerators = glob.glob(args.m+"f*.py")

import subprocess

for featureGenerator in AllFeatureGenerators:
    print "Generating for " + featureGenerator
    subprocess.call(["fGen.py","-d",args.d,"-m",featureGenerator])
    
