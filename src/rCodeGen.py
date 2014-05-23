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

def ForSetUpChecksForTrainPredictTogather(rScript):
    rScript.write('print ("Section1: Clearing the environment and making sure the data directory has been passed") \n')
    rScript.write('rm(list=ls()) \n')
    
    rScript.write('args <- commandArgs(trailingOnly = TRUE) \n')

    rScript.write('if(length(args) < 4) \n')
    rScript.write('{ \n')
    rScript.write('  stop("Not enough arguments. Please supply 4 arguments.") \n')
    rScript.write('} \n')
    
    rScript.write('if((args[1]=="-td") == TRUE ) { \n')
    rScript.write('   print ("Checking if parameter -td has been given: PASS") \n')
    rScript.write('}else{ \n')
    rScript.write('   stop ("cannot proceed. Specify the parameters properly. The correct way to use this is train-predict.r -td data/20140207 -pd data/20140208") \n')    
    rScript.write('} \n')
    
    rScript.write('if((args[3]=="-pd") == TRUE ) { \n')
    rScript.write('   print ("Checking if parameter -pd has been given: PASS") \n')
    rScript.write('}else{ \n')
    rScript.write('   stop ("cannot proceed. Specify the parameters properly. The correct way to use this is train-predict.r -td data/20140207 -pd data/20140208") \n')    
    rScript.write('} \n')
    
def CheckIfPredictionsFileAlreadyExists(rScript,args,pUseWhichArgumentForData=2):
    rScript.write('print ("Section2: Checking if predictions file already exists") \n')
    if pUseWhichArgumentForData == 4:
        rScript.write('fileName = paste(args[4],"/p/","'+os.path.basename(os.path.dirname(args.e))+'/'+ os.path.basename(os.path.dirname(args.e)) + args.a +'.predictions",sep="") \n')
    else:
        rScript.write('fileName = paste(args[2],"/p/","'+os.path.basename(os.path.dirname(args.e))+'/'+ os.path.basename(os.path.dirname(args.e)) + args.a +'.predictions",sep="") \n')
    rScript.write('if(file.exists(fileName)){ \n')
    rScript.write("    print ('Warning: The predictions already exist. Is this what you expected?') \n")
    rScript.write("} \n")

def ToReadTargetFile(rScript,config):
    rScript.write('print ("Section2: Read target files") \n')
    lTargetSet = config["target"]
    rScript.write('lDirectorySet<-strsplit(args[2],";",fixed=TRUE,useBytes=FALSE)\n')
    for target in lTargetSet:
        rScript.write('lengthOfEachDay = numeric()\n')
        rScript.write('lFlag=FALSE\n')
        rScript.write('for (file in lDirectorySet[[1]]){\n')
        rScript.write('    if (!lFlag){\n')
        rScript.write('        ' + target+'<- read.csv(paste(file,"/t/'+lTargetSet[target]+'.target",sep=""), header=TRUE ,sep=";", row.names=NULL ) \n')
        rScript.write('        lengthOfEachDay = c(lengthOfEachDay,length(' + target + '))\n')
        rScript.write('        lFlag=TRUE\n')   
        rScript.write('    }\n')
        rScript.write('    else{\n')
        rScript.write('        temp<-read.csv(paste(file,"/t/'+lTargetSet[target]+'.target",sep=""), header=TRUE ,sep=";", row.names=NULL ) \n')
        rScript.write('        lengthOfEachDay = c(lengthOfEachDay,length(temp))\n')
        rScript.write('        '+target+'<-rbind('+target+',temp)\n')
        rScript.write('        rm(temp)\n')
        rScript.write('    }\n')
        rScript.write('    print ("Reading '+ lTargetSet[target] +'.target' + '") \n')
        rScript.write('}\n')

def ForWtVectorGeneration(rScript,weightType):
    rScript.write('lWtType="'+weightType+'"\n')
    rScript.write('weightVector = numeric()\n')
    rScript.write('sumOfAllDaysLength = sum(lengthOfEachDay)\n')
    rScript.write('sumOfDaysExp = 0\n')
    rScript.write('lDayIndex = 0\n')
    rScript.write('for (len in lengthOfEachDay){\n')
    rScript.write('    temp = numeric(len)\n')
    rScript.write('    if( lWtType=="default"){\n')
    rScript.write('        temp = temp+1\n')
    rScript.write('    }else if( lWtType =="exp"){\n')
    rScript.write('        valueToBeAddedToVector = exp(lDayIndex)\n')
    rScript.write('        temp = temp + valueToBeAddedToVector \n')
    rScript.write('        sumOfDaysExp = sumOfDaysExp + ( valueToBeAddedToVector * len)\n')
    rScript.write('    }\n')
    rScript.write('    lDayIndex = lDayIndex + 1\n')
    rScript.write('    weightVector = c(weightVector,temp)\n')
    rScript.write('}\n')
    rScript.write('if(lWtType=="exp"){\n')
    rScript.write('    weightVector = ( sumOfAllDaysLength / sumOfDaysExp ) * weightVector\n')
    rScript.write('}\n')
    
def ToReadFeatureFiles(rScript,config,pUseWhichArgumentForData=2):
    features = config["features"]
    rScript.write('\nprint ("Section3: Read feature files") \n')
    if pUseWhichArgumentForData == 4:
        rScript.write('lDirectorySet<-strsplit(args[4],";",fixed=TRUE,useBytes=FALSE)\n')
    else:
        rScript.write('lDirectorySet<-strsplit(args[2],";",fixed=TRUE,useBytes=FALSE)\n')
    for feature in features:
        rScript.write('lFlag=FALSE\n')
        rScript.write('for (file in lDirectorySet[[1]]){\n')
        rScript.write('    if (!lFlag){\n')
        rScript.write('        '+feature+'<-read.csv(paste(file,"/f/'+features[feature]+'.feature",sep=""), header=TRUE ,sep=";", row.names=NULL ) \n')
        rScript.write('        lFlag=TRUE\n')
        rScript.write('    }\n')
        rScript.write('    else {\n')  
        rScript.write('        temp<-read.csv(paste(file,"/f/'+features[feature]+'.feature",sep=""), header=TRUE ,sep=";", row.names=NULL ) \n')  
        rScript.write('        '+feature+'<-rbind('+feature+',temp)\n')    
        rScript.write('        rm(temp)\n')
        rScript.write('    }\n')
        rScript.write('    print ("Reading '+ features[feature] +'.feature' + '") \n')
        rScript.write('}\n')

def ForSanityChecks(rScript,config):
    features = config["features"]
    #Renaming all features if model and predictions are done simultaneously , so that training and prediction data set do not conflict
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

def ToCreateDataFrameForTraining(rScript,config,pTargetVariableKey):
    features = config["features"]
    rScript.write('\nprint ("Section6: Creating the data frame") \n')
    rScript.write('df = data.frame('+config["target"][pTargetVariableKey]+'='+pTargetVariableKey+'[,2]')
    for feature in features:
        userFriendlyName = features[feature] 
        userFriendlyName = userFriendlyName.replace('[','')
        userFriendlyName = userFriendlyName.replace(']','')
        rScript.write(','+userFriendlyName+'='+feature+'[,2]')
    rScript.write(")\n\n")

def ForTraining(rScript,args,config,pTargetVariableKey):
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
        lStringToRunGlmnet = 'fit = cv.glmnet(x =X, y = as.factor(' + pTargetVariableKey + '[,2]),family=\''+args.targetClass+'\',alpha=1,weights=weightVector) \n'
        rScript.write(lStringToRunGlmnet) # ref: http://www.stanford.edu/~hastie/glmnet/glmnet_alpha.html
    elif(args.a == 'logitr'):
        rScript.write('print ("Section7: Running logistic regression") \n')
        rScript.write('fit <- glm ('+config["target"][pTargetVariableKey]+' ~ ')
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
        rScript.write('fit = randomForest(x =X, y = ' + pTargetVariableKey + '[,2],importance = TRUE) \n') 
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
        rScript.write('fit = mda(x =X, y = ' + pTargetVariableKey + '[,2]) \n') 
    


def saveTrainingModel(rScript,args,path,pTargetVariableKey):
    algo = getAlgoName(args)    
    outputFileName = path+'/'+algo+pTargetVariableKey+ '-td.' + os.path.basename(os.path.abspath(args.td)) + '-dt.' + args.dt + '-targetClass.' + args.targetClass +'.model'
    rScript.write('\nprint (paste("Section8: Saving the model in file '+ outputFileName +'")) \n')
    rScript.write('save(fit, file = "'+ outputFileName+'")')

def ForPredictions(rScript,config,args,pathToDesignFile,pTargetVariableKey,pUseWhichArgumentForData=2):
    features = config["features"]
    #Renaming all features if model and predictions are done simultaneously , so that training and prediction data set do not conflict
    algo = getAlgoName(args)
    predictionModel = algo + pTargetVariableKey + '-td.' + os.path.basename(os.path.abspath(args.td)) + '-dt.' + args.dt + '-targetClass.' + args.targetClass + '.model'
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
    
    rScript.write('\nprint ("Section11: Saving the predictions in file /p/'+ os.path.basename(os.path.dirname(args.e))+'/' + args.a + pTargetVariableKey + '-td.' + os.path.basename(os.path.abspath(args.td)) + \
                                 '-dt.' + args.dt + '-targetClass.' + args.targetClass + '-f.' + os.path.basename(os.path.dirname(pathToDesignFile)) +'.predictions") \n')
    if pUseWhichArgumentForData == 4:
        rScript.write('fileName = paste(args[4],"/p/","' +os.path.basename(os.path.dirname(args.e))+'/'+ args.a + pTargetVariableKey + '-td.' + os.path.basename(os.path.abspath(args.td)) + \
                                 '-dt.' + args.dt + '-targetClass.' + args.targetClass + '-f.' + os.path.basename(os.path.dirname(pathToDesignFile))+ '.predictions",sep="") \n')
    else:
        rScript.write('fileName = paste(args[2],"/p/","' +os.path.basename(os.path.dirname(args.e))+'/'+ args.a + pTargetVariableKey + '-td.' + os.path.basename(os.path.abspath(args.td)) + \
                                 '-dt.' + args.dt + '-targetClass.' + args.targetClass + '-f.' + os.path.basename(os.path.dirname(pathToDesignFile)) +'.predictions",sep="") \n')
    rScript.write('print (fileName) \n')
    rScript.write('write.table(format(dfForFile,digits=16), file = fileName,sep=",",quote=FALSE)')
