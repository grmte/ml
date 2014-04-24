#!/usr/bin/python

import os
import argparse
from configobj import ConfigObj

def getAlgoName(args):
    if args.a is None:
        algo = 'glmnet'
    else:
        algo = args.a
    return algo    
        
def ForSetUpChecks(rScript):
    rScript.write('print ("Section1: Clearing the environment and making sure the data directory has been passed") \n')
    rScript.write('rm(list=ls()) \n')
    
    rScript.write('args <- commandArgs(trailingOnly = TRUE) \n')

    rScript.write('if(length(args) < 2) \n')
    rScript.write('{ \n')
    rScript.write('  stop("Not enough arguments. Please supply 2 arguments.") \n')
    rScript.write('} \n')
    
    rScript.write('if((args[1]=="-d") == TRUE ) { \n')
    rScript.write('   print ("Checking if parameter -d has been given: PASS") \n')
    rScript.write('}else{ \n')
    rScript.write('   stop ("cannot proceed. Specify the parameters properly. The correct way to use this is train.r -d data/20140207") \n')    
    rScript.write('} \n')

def CheckIfPredictionsFileAlreadyExists(rScript,args):
    rScript.write('print ("Section2: Checking if predictions file already exists") \n')
    rScript.write('fileName = paste(args[2],"/p/","' + os.path.basename(os.path.dirname(args.e)) + args.a +'.predictions",sep="") \n')
    rScript.write('if(file.exists(fileName)){ \n')
    rScript.write("    print ('Warning: The predictions already exist. Is this what you expected?') \n")
    rScript.write("} \n")

def ToReadTargetFile(rScript,config):
    rScript.write('print ("Section2: Read target files") \n')
    rScript.write('targetVector=read.csv(paste(args[2],"/t/","'+config["target"]+'.target",sep=""), header=TRUE , sep=";", row.names=NULL ) \n\n')

def ToReadFeatureFiles(rScript,config):
    features = config["features"]
    rScript.write('\nprint ("Section3: Read feature files") \n')
    for feature in features:
        rScript.write('print ("Reading '+ features[feature] +'.feature' + '") \n')
        rScript.write(feature+'=read.csv(paste(args[2],"/f/","'+features[feature]+'.feature",sep=""), header=TRUE ,sep=";", row.names=NULL ) \n')

def ForSanityChecks(rScript,config):
    features = config["features"]
    rScript.write('\nprint ("Section4: Making sure all feature vectors are of same length") \n')
    currentFeatureNumber = 0
    while currentFeatureNumber  <  (len(features) - 1) :
        rScript.write('if (length(' + features.keys()[currentFeatureNumber] + '[,1]) != length(' + features.keys()[currentFeatureNumber+1] + '[,1])) { \n')
        rScript.write('print ("The feature lengths do not match for ' + features.keys()[currentFeatureNumber] +  '=' + features.values()[currentFeatureNumber] +' and '+features.keys()[currentFeatureNumber+1] + '=' + features.values()[currentFeatureNumber+1]+'") \n')
        rScript.write("quit('no',-1) \n")
        rScript.write('}else{ \n')
        rScript.write('print ("Length of ' + features.keys()[currentFeatureNumber] + ' == '+features.keys()[currentFeatureNumber+1] +'")\n')
        rScript.write('}\n')
        currentFeatureNumber = currentFeatureNumber + 1
        
    rScript.write('\nprint ("Section5: Making sure all feature vectors have same time stamp over each row") \n')
    features = config["features"]
    currentFeatureNumber = 0
    while currentFeatureNumber  <  (len(features) - 1) :
        rScript.write('if (all(' + features.keys()[currentFeatureNumber] + '[,1] == ' + features.keys()[currentFeatureNumber+1] + '[,1]) != TRUE) { \n')
        rScript.write('print ("The feature timestamps do not match for ' + features.keys()[currentFeatureNumber] + '=' + features.values()[currentFeatureNumber] +' and '+features.keys()[currentFeatureNumber+1] + '=' + features.values()[currentFeatureNumber+1]+'") \n')
        rScript.write("quit('no',-1) \n")
        rScript.write('}else{ \n')
        rScript.write('print ("Timestamps of ' + features.keys()[currentFeatureNumber] + ' == '+features.keys()[currentFeatureNumber+1] +'")\n')
        rScript.write('}\n')
        currentFeatureNumber = currentFeatureNumber + 1

def ToCreateDataFrameForTraining(rScript,config):
    features = config["features"]
    rScript.write('\nprint ("Section6: Creating the data frame") \n')
    rScript.write('df = data.frame('+config["target"]+'=targetVector[,2]')
    for feature in features:
        userFriendlyName = features[feature] 
        userFriendlyName = userFriendlyName.replace('[','')
        userFriendlyName = userFriendlyName.replace(']','')
        rScript.write(','+userFriendlyName+'='+feature+'[,2]')
    rScript.write(")\n\n")

def ForTraining(rScript,args,config):
    features = config["features"]
    if(args.a == 'glmnet'):
        rScript.write('print ("Section7: Running glmnet") \n')
        rScript.write('X <- cbind(')
        currentFeatureNumber=0
        for feature in features:
            rScript.write(features.keys()[currentFeatureNumber]+'[,2]')
            currentFeatureNumber = currentFeatureNumber+1
            if(len(features) > currentFeatureNumber):
                rScript.write(',')    
        rScript.write(')\n')
        rScript.write('fit = cv.glmnet(x =X, y = as.factor(targetVector[,2]),family=\'multinomial\',alpha=1) \n') # ref: http://www.stanford.edu/~hastie/glmnet/glmnet_alpha.html
    elif(args.a == 'logitr'):
        rScript.write('print ("Section7: Running logistic regression") \n')
        rScript.write('fit <- glm ('+config["target"]+' ~ ')
        currentFeatureNumber=0
        for feature in features:
            rScript.write(features[feature])
            currentFeatureNumber = currentFeatureNumber+1
            if(len(features) > currentFeatureNumber):
                rScript.write('+')
        rScript.write(' , data = df,family = binomial(link="logit") ) \n')
    elif(args.a == 'randomForest'):
        rScript.write('print ("Section7: Running random forest training") \n')
        rScript.write('X <- cbind(')
        currentFeatureNumber=0
        for feature in features:
            rScript.write(features.keys()[currentFeatureNumber]+'[,2]')
            currentFeatureNumber = currentFeatureNumber+1
            if(len(features) > currentFeatureNumber):
                rScript.write(',')    
        rScript.write(')\n')
        rScript.write('fit = randomForest(x =X, y = targetVector[,2],importance = TRUE) \n') 
    elif(args.a == 'mda'):
        rScript.write('print ("Section7: Running mda training") \n')
        rScript.write('X <- cbind(')
        currentFeatureNumber=0
        for feature in features:
            rScript.write(features.keys()[currentFeatureNumber]+'[,2]')
            currentFeatureNumber = currentFeatureNumber+1
            if(len(features) > currentFeatureNumber):
                rScript.write(',')    
        rScript.write(')\n')
        rScript.write('fit = mda(x =X, y = targetVector[,2]) \n') 
    


def saveTrainingModel(rScript,args,path):
    algo = getAlgoName(args)    
    outputFileName = path+'/'+algo+'.model'
    rScript.write('\nprint (paste("Section8: Saving the model in file '+ outputFileName +'")) \n')
    rScript.write('save(fit, file = "'+ outputFileName+'")')

def ForPredictions(rScript,config,args,pathToDesignFile):
    features = config["features"]
    algo = getAlgoName(args)
    predictionModel = algo+'.model'
    rScript.write('\nprint ("Section6: Read in prediction model'+os.path.dirname(pathToDesignFile)+'/'+predictionModel+'") \n')
    rScript.write('load("'+os.path.dirname(pathToDesignFile)+'/'+predictionModel+'")')

    if(args.a == 'glmnet'):
        rScript.write('\n\nprint ("Section7: Creating data frame") \n')
        rScript.write('df = cbind(')
        currentFeatureNumber=0
        for feature in features:
            rScript.write(feature+'[,2]')
            currentFeatureNumber = currentFeatureNumber+1
            if(len(features) > currentFeatureNumber):
                rScript.write(',')
        rScript.write(")\n\n")

        rScript.write('print ("Section8: Running ' + args.a + ' prediction") \n')
        rScript.write('Prob <- predict (fit, newx = df,s = "lambda.min",type = "response")')
        rScript.write("\n\n")
    elif(args.a == 'logitr'):
        rScript.write('\n\nprint ("Section7: Creating the data frame") \n')
        rScript.write('df = data.frame(')
        currentFeatureNumber=0
        for feature in features:
            rScript.write(features[feature]+'='+feature+'[,2]')
            currentFeatureNumber = currentFeatureNumber+1
            if(len(features) > currentFeatureNumber):
                rScript.write(',')
        rScript.write(")\n\n")

        rScript.write('print ("Section8: Running ' + args.a + ' prediction") \n')
        rScript.write('Prob<- predict (fit, newdata = df, type = "response")')
        rScript.write("\n\n")
    elif(args.a == 'randomForest'):
        rScript.write('\n\nprint ("Section7: Creating the data frame") \n')
        rScript.write('df = data.frame(')
        currentFeatureNumber=0
        for feature in features:
            rScript.write(features[feature]+'='+feature+'[,2]')
            currentFeatureNumber = currentFeatureNumber+1
            if(len(features) > currentFeatureNumber):
                rScript.write(',')
        rScript.write(")\n\n")

        rScript.write('print ("Section8: Running ' + args.a + ' prediction") \n')
        rScript.write('Prob<- predict (fit, df)')
        rScript.write("\n\n")
    elif(args.a == 'mda'):
        rScript.write('\n\nprint ("Section7: Creating the data frame") \n')
        rScript.write('df = data.frame(')
        currentFeatureNumber=0
        for feature in features:
            rScript.write(features[feature]+'='+feature+'[,2]')
            currentFeatureNumber = currentFeatureNumber+1
            if(len(features) > currentFeatureNumber):
                rScript.write(',')
        rScript.write(")\n\n")

        rScript.write('print ("Section8: Running ' + algo + ' prediction") \n')
        rScript.write('Prob<- predict (fit, df)')
        rScript.write("\n\n")
    else:
        print "The only valid options are glmnet, logitr, randomForest or mda"
        os._exit(-1)

    rScript.write('\nprint ("Section9: Creating the data frame to write in the file") \n')
    rScript.write('dfForFile <- data.frame('+features.keys()[0]+'[,1]) \n')
    
    rScript.write('\nprint ("Section10: Putting the probabilities in the data frame") \n')
    rScript.write('dfForFile <- cbind(dfForFile,Prob) \n')
    
    rScript.write('\nprint ("Section11: Saving the predictions in file /p/'+ os.path.basename(os.path.dirname(pathToDesignFile)) + args.a +'.predictions") \n')
    rScript.write('fileName = paste(args[2],"/p/","' + os.path.basename(os.path.dirname(pathToDesignFile)) + args.a +'.predictions",sep="") \n')
    rScript.write('print (fileName) \n')
    rScript.write('write.table(format(dfForFile,digits=16), file = fileName,sep=",",quote=FALSE)')
