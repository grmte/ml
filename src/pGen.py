#!/usr/bin/python

import os
import argparse
from configobj import ConfigObj

parser = argparse.ArgumentParser(description='Generates predict.r which will use design.model to make predictions. Sample command is pGen.py -c ob/e1/design.ini')
parser.add_argument('-c', required=True,help='Config file to use to find the features')
args = parser.parse_args()

print "Using the config file " + args.c

config = ConfigObj(args.c)

print "\nThe config parameters that I am working with are"
print config 
print ""

dirName=os.path.dirname(args.c)

f = open(dirName+'/predict.r','w')

f.write('#!/usr/bin/Rscript \n')
f.write('print ("Section1: Setting the environment") \n')
f.write('rm(list=ls()) \n')
f.write('setwd("'+ config["workingDirectory"] +'") \n\n')


f.write('\nprint ("Section2: Read in the feature files") \n')
features = config["features"]
for feature in features:
    f.write(feature+'=read.csv("'+features[feature]+'.feature", header=FALSE) \n')

f.write('\nprint ("Section3: Read in the prediction model") \n')
f.write('load("'+args.c[:args.c.find('.')]+'.model")')


f.write('\n\nprint ("Section4: Creating the data frame") \n')
f.write('df = data.frame(')
currentFeatureNumber=0
for feature in features:
    f.write(features[feature]+'='+feature+'$V2')
    currentFeatureNumber = currentFeatureNumber+1
    if(len(features) > currentFeatureNumber):
            f.write(',')
f.write(")\n\n")

f.write('print ("Section5: Running logistic regression prediction") \n')
f.write('df$Prob <- predict (logistic.fit, newdata = df, type = "response")')
f.write("\n\n")

f.write('\nprint ("Section6: Saving the predictions in directory '+ config["workingDirectory"] +' in file '+args.c[:args.c.find('.')] +'.predictions") \n')
f.write('write.table(df, file = "' +  args.c[:args.c.find('.')] +'.predictions")')

f.close()

print "Finished generating the R program"
print 'predict.r' + "\n"
