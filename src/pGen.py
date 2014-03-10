#!/usr/bin/python

import os
import argparse
from configobj import ConfigObj

parser = argparse.ArgumentParser(description='Generates predict.r which will use design.model to make predictions. Sample command is pGen.py -e ob/e1/')
parser.add_argument('-e', required=True,help='Directory to find the experiement designs')
args = parser.parse_args()

print "Using the experiment folder " + args.e

config = ConfigObj(args.e+"/design.ini")

print "\nThe config parameters that I am working with are"
print config 
print ""

dirName=os.path.dirname(args.e)

f = open(dirName+'/predict.r','w')

f.write('#!/usr/bin/Rscript \n')

f.write('print ("Section1: Setting the environment") \n')
f.write('rm(list=ls()) \n')

f.write('args <- commandArgs(trailingOnly = TRUE) \n')
f.write('if(length(args) < 2) \n')
f.write('{ \n')
f.write('  stop("Not enough arguments. Please supply 2 arguments.") \n')
f.write('} \n')

f.write('if((args[1]=="-d") == TRUE ) { \n')
f.write('   print ("Parameter check passed") \n')
f.write('}else{ \n')
f.write('   stop ("cannot proceed. Specify the parameters properly. The correct way to use this is predict.r -d data/20140207") \n')    
f.write('} \n')

f.write('print ("Section2: checking if the predictions file already exists") \n')
f.write('fileName = paste(args[2],"' + os.path.basename(os.path.dirname(args.e)) +'.predictions",sep="") \n')
f.write('if(file.exists(fileName)){ \n')
f.write("    stop ('The predictions already exist. Delete it and then run the program again') \n")
f.write("} \n")

f.write('\nprint ("Section3: Read in the feature files") \n')
features = config["features"]
for feature in features:
    f.write('print ("Reading in '+ features[feature] +'.feature' + '") \n')
    f.write(feature+'=read.csv(paste(args[2],"'+features[feature]+'.feature",sep=""), header=FALSE) \n')

f.write('\nprint ("Section4: Making sure all feature vectors are of same length") \n')
features = config["features"]
currentFeatureNumber = 0
while currentFeatureNumber  <  (len(features) - 1) :
  f.write('if (length(' + features.keys()[currentFeatureNumber] + '$V1) != length(' + features.keys()[currentFeatureNumber+1] + '$V1)) { \n')
  f.write('print ("The feature lengths do not match for ' + features.keys()[currentFeatureNumber] + features.values()[currentFeatureNumber] +' and '+features.keys()[currentFeatureNumber+1]+ features.values()[currentFeatureNumber+1]+'") \n')
  f.write('quit() \n')
  f.write('}else{ \n')
  f.write('print ("Length of ' + features.keys()[currentFeatureNumber] + ' is same as length of '+features.keys()[currentFeatureNumber+1] +'")\n')
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
  f.write('print ("Timestamps of ' + features.keys()[currentFeatureNumber] + ' is same as timestamp of '+features.keys()[currentFeatureNumber+1] +'")\n')
  f.write('}\n')
  currentFeatureNumber = currentFeatureNumber + 1

f.write('\nprint ("Section6: Read in the prediction model") \n')
f.write('load("'+args.e+'/design.model")')

f.write('\n\nprint ("Section7: Creating the data frame") \n')
f.write('df = data.frame(')
currentFeatureNumber=0
for feature in features:
    f.write(features[feature]+'='+feature+'$V2')
    currentFeatureNumber = currentFeatureNumber+1
    if(len(features) > currentFeatureNumber):
            f.write(',')
f.write(")\n\n")

f.write('print ("Section8: Running logistic regression prediction") \n')
f.write('df$Prob <- predict (logistic.fit, newdata = df, type = "response")')
f.write("\n\n")

f.write('\nprint ("Section9: Creating the data frame to write in the file") \n')
f.write('dfForFile <- data.frame('+features.keys()[0]+'$V1) \n')

f.write('\nprint ("Section10: Putting the probabilities in the data frame") \n')
f.write('dfForFile <- cbind(dfForFile,df$Prob) \n')

f.write('\nprint ("Section11: Saving the predictions in file '+ os.path.basename(os.path.dirname(args.e)) +'.predictions") \n')
f.write('fileName = paste(args[2],"' + os.path.basename(os.path.dirname(args.e)) +'.predictions",sep="") \n')
f.write('print (fileName) \n')
f.write('write.table(format(dfForFile,digits=16), file = fileName,sep=",",quote=FALSE)')

f.close()

print "Finished generating the R program"
print 'predict.r' + "\n"
