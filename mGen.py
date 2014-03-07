#!/usr/bin/python

import os
import argparse
from configobj import ConfigObj

parser = argparse.ArgumentParser(description='Generate the R script to train the model')
parser.add_argument('-c', required=True,help='Config file to use to find the features and targets')
args = parser.parse_args()

print "Using the config file " + args.c

config = ConfigObj(args.c)

print config

f = open(args.c[:args.c.find('.')]+'.train.r','w')

f.write('# Setting the environment \n')
f.write('#!/usr/bin/Rscript \n')
f.write('rm(list=ls()) \n')
f.write('setwd("'+ config["workingDirectory"] +'") \n\n')

f.write('# Read in the data files \n')
f.write('feature1Vector=read.csv("'+config["feature1"]+'.feature", header=FALSE) \n')
f.write('feature2Vector=read.csv("'+config["feature2"]+'.feature", header=FALSE) \n')
f.write('targetVector=read.csv("'+config["target"]+'.target", header=FALSE) \n\n')

f.write('# Creating the data frame \n')
f.write('df = data.frame('+config["target"]+'=targetVector$V2,'+config["feature1"]+'=feature1Vector$V2,'+config["feature2"]+'=feature2Vector$V2) \n\n')

f.write('# Running logistic regression \n')
f.write('logistic.fit <- glm ('+config["target"]+' ~ '+config["feature1"]+' + '+config["feature2"]+' , data = df,family = binomial(link="logit") ) \n')
f.close()
