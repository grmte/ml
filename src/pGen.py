#!/usr/bin/python

import os
import argparse
from configobj import ConfigObj

parser = argparse.ArgumentParser(description='Generates predict.r which will use design.model to make predictions. Sample command is pGen.py -e ob/e1/')
parser.add_argument('-e', required=True,help='Directory to find the experiement designs')
parser.add_argument('-a', required=True,help='Algorithm name')
args = parser.parse_args()

print "Using the experiment folder " + args.e

config = ConfigObj(args.e+"/design.ini")

print "\nThe config parameters that I am working with are"
print config 
print ""

dirName=os.path.dirname(args.e)

if args.a is None:
    algo ='glmnet'
else:
    algo =args.a

rProgName = "predict-"+algo+".r"
rProgLocation = dirName+'/'+rProgName
f = open(rProgLocation,'w')

f.write('#!/usr/bin/Rscript \n')
if(args.a == 'glmnet'):
    f.write('require (glmnet) \n')
elif(args.a == 'randomForest'):
    f.write('require (randomForest) \n')

f.write('print ("Section1: Setting the environment") \n')
f.write('rm(list=ls()) \n')

f.write('args <- commandArgs(trailingOnly = TRUE) \n')
f.write('if(length(args) < 2) \n')
f.write('{ \n')
f.write('  stop("Not enough arguments. Please supply 2 arguments.") \n')
f.write('} \n')

f.write('if((args[1]=="-d") == TRUE ) { \n')
f.write('   print ("Checking if parameter -d has been given: PASS") \n')
f.write('}else{ \n')
f.write('   stop ("cannot proceed. Specify the parameters properly. The correct way to use this is predict.r -d data/20140207") \n')    
f.write('} \n')

f.write('print ("Section2: Checking if predictions file already exists") \n')
f.write('fileName = paste(args[2],"/p/","' + os.path.basename(os.path.dirname(args.e)) + args.a +'.predictions",sep="") \n')
f.write('if(file.exists(fileName)){ \n')
f.write("    print ('Warning: The predictions already exist. Is this what you expected?') \n")
f.write("} \n")

f.write('\nprint ("Section3: Read in the feature files") \n')
features = config["features"]
for feature in features:
    f.write('print ("Reading '+ features[feature] +'.feature' + '") \n')
    f.write(feature+'=read.csv(paste(args[2],"f/","'+features[feature]+'.feature",sep=""), header=FALSE) \n')

f.write('\nprint ("Section4: Making sure all feature vectors have same length") \n')
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

f.write('\nprint ("Section6: Read in prediction model") \n')
predictionModel = algo+'.model'

f.write('load("'+args.e+'/'+predictionModel+'")')

if(args.a == 'glmnet'):
    f.write('\n\nprint ("Section7: Creating data frame") \n')
    f.write('df = cbind(')
    currentFeatureNumber=0
    for feature in features:
        f.write(feature+'$V2')
        currentFeatureNumber = currentFeatureNumber+1
        if(len(features) > currentFeatureNumber):
            f.write(',')
    f.write(")\n\n")

    f.write('print ("Section8: Running ' + args.a + ' prediction") \n')
    f.write('Prob <- predict (fit, newx = df,s = "lambda.min")')
    f.write("\n\n")
elif(args.a == 'logitr'):
    f.write('\n\nprint ("Section7: Creating the data frame") \n')
    f.write('df = data.frame(')
    currentFeatureNumber=0
    for feature in features:
        f.write(features[feature]+'='+feature+'$V2')
        currentFeatureNumber = currentFeatureNumber+1
        if(len(features) > currentFeatureNumber):
            f.write(',')
    f.write(")\n\n")

    f.write('print ("Section8: Running ' + args.a + ' prediction") \n')
    f.write('Prob<- predict (fit, newdata = df, type = "response")')
    f.write("\n\n")
elif(args.a == 'randomForest'):
    f.write('\n\nprint ("Section7: Creating the data frame") \n')
    f.write('df = data.frame(')
    currentFeatureNumber=0
    for feature in features:
        f.write(features[feature]+'='+feature+'$V2')
        currentFeatureNumber = currentFeatureNumber+1
        if(len(features) > currentFeatureNumber):
            f.write(',')
    f.write(")\n\n")

    f.write('print ("Section8: Running ' + args.a + ' prediction") \n')
    f.write('Prob<- predict (fit, df)')
    f.write("\n\n")
elif(args.a == 'mda'):
    f.write('\n\nprint ("Section7: Creating the data frame") \n')
    f.write('df = data.frame(')
    currentFeatureNumber=0
    for feature in features:
        f.write(features[feature]+'='+feature+'$V2')
        currentFeatureNumber = currentFeatureNumber+1
        if(len(features) > currentFeatureNumber):
            f.write(',')
    f.write(")\n\n")

    f.write('print ("Section8: Running ' + algo + ' prediction") \n')
    f.write('Prob<- predict (fit, df)')
    f.write("\n\n")
else:
    print "The only valid options are glmnet, logitr, randomForest or mda"
    os._exit(-1)

f.write('\nprint ("Section9: Creating the data frame to write in the file") \n')
f.write('dfForFile <- data.frame('+features.keys()[0]+'$V1) \n')

f.write('\nprint ("Section10: Putting the probabilities in the data frame") \n')
f.write('dfForFile <- cbind(dfForFile,Prob) \n')

f.write('\nprint ("Section11: Saving the predictions in file /p/'+ os.path.basename(os.path.dirname(args.e)) +args.a +'.predictions") \n')
f.write('fileName = paste(args[2],"/p/","' + os.path.basename(os.path.dirname(args.e)) + args.a +'.predictions",sep="") \n')
f.write('print (fileName) \n')
f.write('write.table(format(dfForFile,digits=16), file = fileName,sep=",",quote=FALSE)')

f.close()

print "Finished generating R prediction program: " + rProgLocation + "\n"
os.system("chmod +x "+rProgLocation)
