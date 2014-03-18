#!/usr/bin/python

import os
import argparse
from configobj import ConfigObj

parser = argparse.ArgumentParser(description='Generates train.r. A sample command is mGen.py -e ob/e1/ ')
parser.add_argument('-e', required=True,help='Experiement folder to use to find the features and targets')
parser.add_argument('-a', required=True,help='Algorithm name')
args = parser.parse_args()

print "Using the experiment folder " + args.e

config = ConfigObj(args.e+"/design.ini")

print "\nThe config parameters that I am working with are"
print config 
print ""

dirName=os.path.dirname(args.e)

if args.a is None:
    algo = 'glmnet'
else:
    algo = args.a

rProgName = "train-"+algo+".r"
rProgLocation = dirName+'/'+rProgName
f = open(rProgLocation,'w')

f.write('#!/usr/bin/Rscript \n')

if(algo == 'glmnet'):
    f.write('require (glmnet) \n')
elif(algo == 'randomForest'):
    f.write('require (randomForest) \n')
elif(algo == 'mda'):
    f.write('require (mda) \n')

f.write('print ("Section1: Clearing the environment and making sure the data directory has been passed") \n')
f.write('rm(list=ls()) \n')

f.write('args <- commandArgs(trailingOnly = TRUE) \n')

f.write('if(length(args) < 2) \n')
f.write('{ \n')
f.write('  stop("Not enough arguments. Please supply 2 arguments.") \n')
f.write('} \n')

f.write('if((args[1]=="-d") == TRUE ) { \n')
f.write('   print ("Checking if parameter -d has been given: PASS") \n')
f.write('}else{ \n')
f.write('   stop ("cannot proceed. Specify the parameters properly. The correct way to use this is train.r -d data/20140207") \n')    
f.write('} \n')

f.write('print ("Section2: Read target files") \n')
f.write('targetVector=read.csv(paste(args[2],"/t/","'+config["target"]+'.target",sep=""), header=FALSE) \n\n')


f.write('\nprint ("Section3: Read feature files") \n')
features = config["features"]
for feature in features:
    f.write('print ("Reading '+ features[feature] +'.feature' + '") \n')
    f.write(feature+'=read.csv(paste(args[2],"/f/","'+features[feature]+'.feature",sep=""), header=FALSE) \n')

f.write('\nprint ("Section4: Making sure all feature vectors are of same length") \n')
features = config["features"]
currentFeatureNumber = 0
while currentFeatureNumber  <  (len(features) - 1) :
  f.write('if (length(' + features.keys()[currentFeatureNumber] + '$V1) != length(' + features.keys()[currentFeatureNumber+1] + '$V1)) { \n')
  f.write('print ("The feature lengths do not match for ' + features.keys()[currentFeatureNumber] + features.values()[currentFeatureNumber] +' and '+features.keys()[currentFeatureNumber+1]+ features.values()[currentFeatureNumber+1]+'") \n')
  f.write('quit() \n')
  f.write('}else{ \n')
  f.write('print ("Length of ' + features.keys()[currentFeatureNumber] + ' == '+features.keys()[currentFeatureNumber+1] +'")\n')
  f.write('}\n')
  currentFeatureNumber = currentFeatureNumber + 1

f.write('\nprint ("Section5: Making sure all feature vectors have same time stamp over each row") \n')
features = config["features"]
currentFeatureNumber = 0
while currentFeatureNumber  <  (len(features) - 1) :
  f.write('if (all(' + features.keys()[currentFeatureNumber] + '$V1 == ' + features.keys()[currentFeatureNumber+1] + '$V1) != TRUE) { \n')
  f.write('print ("The feature timestamps do not match for ' + features.keys()[currentFeatureNumber] + features.values()[currentFeatureNumber] +' and '+features.keys()[currentFeatureNumber+1]+ features.values()[currentFeatureNumber+1]+'") \n')
  f.write('quit() \n')
  f.write('}else{ \n')
  f.write('print ("Timestamps of ' + features.keys()[currentFeatureNumber] + ' == '+features.keys()[currentFeatureNumber+1] +'")\n')
  f.write('}\n')
  currentFeatureNumber = currentFeatureNumber + 1

f.write('\nprint ("Section6: Creating the data frame") \n')
f.write('df = data.frame('+config["target"]+'=targetVector$V2')
for feature in features:
    userFriendlyName = features[feature] 
    userFriendlyName = userFriendlyName.replace('[','')
    userFriendlyName = userFriendlyName.replace(']','')
    f.write(','+userFriendlyName+'='+feature+'$V2')
f.write(")\n\n")



if(args.a == 'glmnet'):
    f.write('print ("Section7: Running glmnet") \n')
    f.write('X <- cbind(')
    currentFeatureNumber=0
    for feature in features:
        f.write(features.keys()[currentFeatureNumber]+'$V2')
        currentFeatureNumber = currentFeatureNumber+1
        if(len(features) > currentFeatureNumber):
            f.write(',')    
    f.write(')\n')
    f.write('fit = cv.glmnet(x =X, y = targetVector$V2) \n') # ref: http://www.stanford.edu/~hastie/glmnet/glmnet_alpha.html
elif(args.a == 'logitr'):
    f.write('print ("Section7: Running logistic regression") \n')
    f.write('fit <- glm ('+config["target"]+' ~ ')
    currentFeatureNumber=0
    for feature in features:
        f.write(features[feature])
        currentFeatureNumber = currentFeatureNumber+1
        if(len(features) > currentFeatureNumber):
            f.write('+')
    f.write(' , data = df,family = binomial(link="logit") ) \n')
elif(args.a == 'randomForest'):
    f.write('print ("Section7: Running random forest training") \n')
    f.write('X <- cbind(')
    currentFeatureNumber=0
    for feature in features:
        f.write(features.keys()[currentFeatureNumber]+'$V2')
        currentFeatureNumber = currentFeatureNumber+1
        if(len(features) > currentFeatureNumber):
            f.write(',')    
    f.write(')\n')
    f.write('fit = randomForest(x =X, y = targetVector$V2,importance = TRUE) \n') 
elif(args.a == 'mda'):
    f.write('print ("Section7: Running mda training") \n')
    f.write('X <- cbind(')
    currentFeatureNumber=0
    for feature in features:
        f.write(features.keys()[currentFeatureNumber]+'$V2')
        currentFeatureNumber = currentFeatureNumber+1
        if(len(features) > currentFeatureNumber):
            f.write(',')    
    f.write(')\n')
    f.write('fit = mda(x =X, y = targetVector$V2) \n') 
    
outputFileName = args.e+'/'+algo+'.model'

f.write('\nprint (paste("Section8: Saving the model in file '+ outputFileName +'")) \n')
f.write('save(fit, file = "'+ outputFileName+'")')

f.close()

print "Finished generating R training program: " + rProgLocation + "\n"
os.system("chmod +x "+rProgLocation)
