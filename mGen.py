#!/usr/bin/python

import os
import argparse
from configobj import ConfigObj

parser = argparse.ArgumentParser(description='Generate the R script to train the model. A sample command is ./mGen.py -c experiment1.ini')
parser.add_argument('-c', required=True,help='Config file to use to find the features and targets')
args = parser.parse_args()

print "Using the config file " + args.c

config = ConfigObj(args.c)

print "\nThe config parameters that I am working with are"
print config 
print ""

f = open(args.c[:args.c.find('.')]+'.train.r','w')

f.write('#!/usr/bin/Rscript \n')
f.write('print ("Section1: Setting the environment") \n')
f.write('rm(list=ls()) \n')
f.write('setwd("'+ config["workingDirectory"] +'") \n\n')


f.write('print ("Section2: Read in the target files") \n')
f.write('targetVector=read.csv("'+config["target"]+'.target", header=FALSE) \n\n')


f.write('\nprint ("Section3: Read in the feature files") \n')
features = config["features"]
for feature in features:
    f.write(feature+'=read.csv("'+features[feature]+'.feature", header=FALSE) \n')


f.write('\nprint ("Section4: Creating the data frame") \n')
f.write('df = data.frame('+config["target"]+'=targetVector$V2')
for feature in features:
    f.write(','+features[feature]+'='+feature+'$V2')
f.write(")\n\n")

f.write('print ("Section5: Running logistic regression") \n')
f.write('logistic.fit <- glm ('+config["target"]+' ~ ')
currentFeatureNumber=0
for feature in features:
    f.write(features[feature])
    currentFeatureNumber = currentFeatureNumber+1
    if(len(features) > currentFeatureNumber):
        f.write('+')
f.write(' , data = df,family = binomial(link="logit") ) \n')

f.write('\nprint ("Section6: Saving the model in directory '+ config["workingDirectory"] +' in file '+args.c[:args.c.find('.')] +'.model1.rda") \n')
f.write('save(logistic.fit, file = "' +  args.c[:args.c.find('.')] +'.model1.rda")')

f.close()

print "Finished generating the R program"
print args.c[:args.c.find('.')]+'.train.r' + "\n"
