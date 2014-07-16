#!/usr/bin/python

import itertools, os,argparse
from configobj import ConfigObj

parser = argparse.ArgumentParser(description='This program will generate the design.ini for each subexperiment. An e.g. command line is genAllSubE.py -e e1/. So if an experiment has 12 features it will generate approximately 4083 sub experiments.')
parser.add_argument('-e', required=True,help='Directory of the experiment')
args = parser.parse_args()

config = ConfigObj(args.e+"/design.ini")

targets = config["target"]
features = config["features-"+targets.keys()[0]]

i = 1
numberOfFeatureSet = 1
numberOfFeatureSets = 0

# lets make a directory if it does not already exist
try:
    os.stat(args.e+"/s/")
except:
    os.mkdir(args.e+"/s/")
    
while i < len(features):
    i += 1
    # lets make a directory if it does not already exist
    try:
        os.stat(args.e+"/s/"+str(i)+"c")
    except:
        os.mkdir(args.e+"/s/"+str(i)+"c")       

    featureSets = list(itertools.combinations(features, i))
    for featureSet in featureSets:
        newConfig = ConfigObj()
        try:
            os.stat(args.e+"/s/"+str(i)+"c/"+''.join(featureSet))
        except:
            os.mkdir(args.e+"/s/"+str(i)+"c/"+''.join(featureSet))       
        newConfig.filename = args.e+"/s/"+str(i)+"c/"+''.join(featureSet) + "/design.ini"
        newConfig['target'] = {}
        for target in targets:
            newConfig['target'][target] = targets[target]
            newConfig['features-'+target] = {}
            for feature in featureSet:
                newConfig['features-'+target][feature] = features[feature]
        newConfig.write()
        numberOfFeatureSet += 1

    numberOfFeatureSets += len(featureSets)

print "The total number of features are " + str(len(features))
print "The total number of feature sets are " + str(numberOfFeatureSets)
