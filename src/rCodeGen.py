#!/usr/bin/python

import os
import argparse
from configobj import ConfigObj
import attribute

skipRows = 10000
skipRowCode = "" if skipRows == 0 else "[-c(1:" + str(skipRows) + "),]"

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
    
def ToReadTargetFile(rScript,config):
    rScript.write('print ("Section2: Read target files") \n')
    lTargetSet = config["target"]
    rScript.write('lDirectorySet<-strsplit(args[2],";",fixed=TRUE,useBytes=FALSE)\n')
    for target in lTargetSet:
        userFriendlyName = lTargetSet[target]
        userFriendlyName = userFriendlyName.replace('[','')
        userFriendlyName = userFriendlyName.replace(']','')
        fileToRead = lTargetSet[target]+ attribute.generateExtension() 
        rScript.write('lengthOfEachDay = numeric()\n')
        rScript.write('lFlag=FALSE\n')
        rScript.write('for (file in lDirectorySet[[1]]){\n')
        rScript.write('    if (!lFlag){\n')
        rScript.write('        load(paste(file,"/t/'+fileToRead+'.bin",sep=""))\n')
        rScript.write('        ' + target+'<- ' + userFriendlyName + skipRowCode + '\n')
        rScript.write('        rm(' + userFriendlyName + ')\n')
        rScript.write('        lengthOfEachDay = c(lengthOfEachDay,nrow(' + target + '))\n')
        rScript.write('        lFlag=TRUE\n')   
        rScript.write('    }\n')
        rScript.write('    else{\n')
        rScript.write('        load(paste(file,"/t/'+fileToRead+'.bin",sep=""))\n')
        rScript.write('        temp<-' + userFriendlyName + skipRowCode + '\n')
        rScript.write('        rm(' + userFriendlyName + ')\n')
        rScript.write('        lengthOfEachDay = c(lengthOfEachDay,nrow(temp))\n')
        rScript.write('        '+target+'<-rbind('+target+',temp)\n')
        rScript.write('        rm(temp)\n')
        rScript.write('    }\n')
        rScript.write('    print ("Reading '+ fileToRead +'.target' + '") \n')
        rScript.write('}\n')

def ForWtVectorGeneration(rScript,weightType):
    rScript.write('lWtType="'+weightType+'"\n')
    rScript.write('weightVector = numeric()\n')
    rScript.write('print(lengthOfEachDay)\n')
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
    
def ToReadFeatureFiles(rScript,config,targetVariable,pUseWhichArgumentForData=2):
    features = config["features-"+targetVariable]
    rScript.write('\nprint ("Section3: Read feature files") \n')
    if pUseWhichArgumentForData == 4:
        rScript.write('lDirectorySet<-strsplit(args[4],";",fixed=TRUE,useBytes=FALSE)\n')
    else:
        rScript.write('lDirectorySet<-strsplit(args[2],";",fixed=TRUE,useBytes=FALSE)\n')
    for feature in features:
        userFriendlyName = features[feature]
        userFriendlyName = userFriendlyName.replace('[','')
        userFriendlyName = userFriendlyName.replace(']','')
        userFriendlyName = userFriendlyName.replace('(','')
        userFriendlyName = userFriendlyName.replace(')','')
        featureNameWithoutBrackets = features[feature].replace('(','').replace(')','') + attribute.generateExtension() 
        rScript.write('lFlag=FALSE\n')
        rScript.write('for (file in lDirectorySet[[1]]){\n')
        rScript.write('    if (!lFlag){\n')
        rScript.write('        load(paste(file,"/f/'+featureNameWithoutBrackets+'.bin",sep=""))\n')
        rScript.write('        '+feature+targetVariable+'<-get("'+userFriendlyName+'")' + skipRowCode + ' \n')
        rScript.write('        rm("' + userFriendlyName + '")\n')
        rScript.write('        lFlag=TRUE\n')
        rScript.write('    }\n')
        rScript.write('    else {\n')  
        rScript.write('        load(paste(file,"/f/'+featureNameWithoutBrackets+'.bin",sep=""))\n')
        rScript.write('        temp<-get("'+userFriendlyName+ '")' + skipRowCode + '\n')  
        rScript.write('        rm("' + userFriendlyName + '")\n')
        rScript.write('        '+feature+targetVariable+'<-rbind('+feature+targetVariable+',temp)\n')    
        rScript.write('        rm(temp)\n')
        rScript.write('    }\n')
        rScript.write('    print ("Reading '+ featureNameWithoutBrackets +'.feature' + '") \n')
        rScript.write('}\n')

def ToReadPredictionFiles(rScript,config,targetVariable,configInit):
    probs = config["predictions-"+targetVariable]
    rScript.write('\nprint ("Section: Read prediction files") \n')
    rScript.write('lDirectorySet<-strsplit(args[2],";",fixed=TRUE,useBytes=FALSE)\n')
    rScript.write('lTDirectorySet<-strsplit(args[4],";",fixed=TRUE,useBytes=FALSE)\n')
    for prob in probs:
        ident = probs[prob][:probs[prob].find("Prob")]
        rScript.write('lFlag=FALSE\n')
        rScript.write('len = length(lDirectorySet[[1]])\n')
        rScript.write('for (i in c(1:len)){\n')
        rScript.write('    file = lDirectorySet[[1]][i]\n')
        rScript.write('    pfile = lTDirectorySet[[1]][i]\n')
        rScript.write('    fileName = paste("glmnet","' + ident + '","-td.",pfile,"-dt.10-targetClass.binomial-f.AmBRAmB-wt.default.predictions",sep="")\n')
        rScript.write('    if (!lFlag){\n')
        rScript.write('        temp <- read.csv(paste(file,"/p/ABAll_AmBRAmBAll/",fileName,sep=""))\n')
        rScript.write('        ' + prob + ' = temp[ ,2]\n')
        rScript.write('        rm(temp)\n')
        rScript.write('        lFlag=TRUE\n')
        rScript.write('    }\n')
        rScript.write('    else {\n')  
        rScript.write('        temp <- read.csv(paste(file,"/p/ABAll_AmBRAmBAll/",fileName,sep=""))\n')
        rScript.write('        '+ prob +'<-c(' + prob + ',temp[ ,2])\n')
        rScript.write('        rm(temp)\n')
        rScript.write('    }\n')
        rScript.write('    print (paste("Reading ",paste(file,"/p/ABAll_AmBRAmBAll/",fileName,sep=""),sep="")) \n')
        rScript.write('}\n')

def ForSanityChecks(rScript,config,targetVariable):
    features = config["features-"+targetVariable]
    #Renaming all features if model and predictions are done simultaneously , so that training and prediction data set do not conflict
    rScript.write('\nprint ("Section4: Making sure all feature vectors are of same length") \n')
    currentFeatureNumber = 0
    while currentFeatureNumber  <  (len(features) - 1) :
        rScript.write('if (length(' + features.keys()[currentFeatureNumber]+targetVariable + '[,1]) != length(' + features.keys()[currentFeatureNumber+1] +targetVariable+ '[,1])) { \n')
        rScript.write('print ("The feature lengths do not match for ' + features.keys()[currentFeatureNumber]+targetVariable +  '=' + features.values()[currentFeatureNumber] +' and '+features.keys()[currentFeatureNumber+1]+targetVariable + '=' + features.values()[currentFeatureNumber+1]+'") \n')
        rScript.write("quit('no',-1) \n")
        rScript.write('}else{ \n')
        rScript.write('print ("Length of ' + features.keys()[currentFeatureNumber]+targetVariable + ' == '+features.keys()[currentFeatureNumber+1]+targetVariable +'")\n')
        rScript.write('}\n')
        currentFeatureNumber = currentFeatureNumber + 1
        
    rScript.write('\nprint ("Section5: Making sure all feature vectors have same time stamp over each row") \n')
    features = config["features-"+targetVariable]
    currentFeatureNumber = 0
    while currentFeatureNumber  <  (len(features) - 1) :
        rScript.write('if (all(sprintf("%.6f",as.numeric(' + features.keys()[currentFeatureNumber] + targetVariable + '[,1])) == sprintf("%.6f",as.numeric(' + features.keys()[currentFeatureNumber+1] + targetVariable + '[,1]))) != TRUE) { \n')
        #rScript.write('if (all(' + features.keys()[currentFeatureNumber] + targetVariable + '[,1] == ' + features.keys()[currentFeatureNumber+1] + targetVariable + '[,1]) != TRUE) { \n')
        rScript.write('print ("The feature timestamps do not match for ' + features.keys()[currentFeatureNumber]+targetVariable + '=' + features.values()[currentFeatureNumber] +' and '+features.keys()[currentFeatureNumber+1]+targetVariable + '=' + features.values()[currentFeatureNumber+1]+'") \n')
        rScript.write("quit('no',-1) \n")
        rScript.write('}else{ \n')
        rScript.write('print ("Timestamps of ' + features.keys()[currentFeatureNumber]+targetVariable + ' == '+features.keys()[currentFeatureNumber+1]+targetVariable +'")\n')
        rScript.write('}\n')
        currentFeatureNumber = currentFeatureNumber + 1

def ToFindCorrelationAndPrintingToFile(rScript,config,pTargetVariableKey,pFileName):
    features = config["features-"+pTargetVariableKey]
    rScript.write('\nprint ("Section6: To Find Correlation For ' +pTargetVariableKey  +'") \n')
    rScript.write('string_intercept = paste("CorrelationCoeficient Of ","' + pTargetVariableKey + '" , ":- ","\\n",sep="")\n')
    rScript.write('cat(string_intercept,file="'+ pFileName + '",sep="",append=TRUE)\n')
    for feature in features:
        userFriendlyName = features[feature]
        userFriendlyName = userFriendlyName.replace('[','')
        userFriendlyName = userFriendlyName.replace(']','')
        userFriendlyName = userFriendlyName.replace('(','')
        userFriendlyName = userFriendlyName.replace(')','')
        featureNameWithoutBrackets = features[feature].replace('(','').replace(')','') + attribute.generateExtension() 
        rScript.write('lFlag=FALSE\n')
        rScript.write('for (file in lDirectorySet[[1]]){\n')
        rScript.write('    if (!lFlag){\n')
        rScript.write('        load(paste(file,"/f/'+featureNameWithoutBrackets+'.bin",sep=""))\n')
        rScript.write('        '+feature+pTargetVariableKey+'<-get("'+userFriendlyName+'")' + skipRowCode + ' \n')
        rScript.write('        rm("' + userFriendlyName + '")\n')
        rScript.write('        lFlag=TRUE\n')
        rScript.write('    }\n')
        rScript.write('    else {\n')  
        rScript.write('        load(paste(file,"/f/'+featureNameWithoutBrackets+'.bin",sep=""))\n')
        rScript.write('        temp<-get("'+userFriendlyName+ '")' + skipRowCode + '\n')  
        rScript.write('        rm("' + userFriendlyName + '")\n')
        rScript.write('        '+feature+pTargetVariableKey+'<-rbind('+feature+pTargetVariableKey+',temp)\n')    
        rScript.write('        rm(temp)\n')
        rScript.write('    }\n')
        rScript.write('    print ("Reading '+ featureNameWithoutBrackets +'.feature' + '") \n')
        rScript.write('}\n')
        userFriendlyName = features[feature] 
        rScript.write('tempCor <- cor('+pTargetVariableKey+'[,2] , '+ feature+pTargetVariableKey+'[,2] )\n')
        rScript.write('string_intercept = paste("'+ userFriendlyName +'" ,"=",toString(tempCor),"\\n",sep="")\n')
        rScript.write('cat(string_intercept,file="'+ pFileName + '",sep="",append=TRUE)\n')
        rScript.write('rm('+ feature+pTargetVariableKey + ')\n')
    rScript.write('string_intercept = paste("\\n","\\n",sep="")\n')
    rScript.write('cat(string_intercept,file="'+ pFileName + '",sep="",append=TRUE)\n')
    
def ToFindCorrelationDatewiseAndPrintingToFile(rScript,config,pTargetVariableKey,pFileName):
    features = config["features-"+pTargetVariableKey]
    rScript.write('\nprint ("Section6: To Find Correlation For ' +pTargetVariableKey  +'") \n')
    rScript.write('string_intercept = paste("CorrelationCoeficient Of ","' + pTargetVariableKey + '" , ":- ","\\n",sep="")\n')
    rScript.write('cat(string_intercept,file="'+ pFileName + '",sep="",append=TRUE)\n')
    for feature in features:
        userFriendlyName = features[feature]
        userFriendlyName = userFriendlyName.replace('[','')
        userFriendlyName = userFriendlyName.replace(']','')
        userFriendlyName = userFriendlyName.replace('(','')
        userFriendlyName = userFriendlyName.replace(')','')
        featureNameWithoutBrackets = features[feature].replace('(','').replace(')','') + attribute.generateExtension() 
        rScript.write('lFlag=FALSE\n')
        rScript.write('for (file in lDirectorySet[[1]]){\n')
        rScript.write('    if (!lFlag){\n')
        rScript.write('        load(paste(file,"/f/'+featureNameWithoutBrackets+'.bin",sep=""))\n')
        rScript.write('        '+feature+pTargetVariableKey+'<-get("'+userFriendlyName+'")' + skipRowCode + ' \n')
        rScript.write('        rm("' + userFriendlyName + '")\n')
        rScript.write('        lFlag=TRUE\n')
        rScript.write('    }\n')
        rScript.write('    else {\n')  
        rScript.write('        load(paste(file,"/f/'+featureNameWithoutBrackets+'.bin",sep=""))\n')
        rScript.write('        temp<-get("'+userFriendlyName+ '")' + skipRowCode + '\n')  
        rScript.write('        rm("' + userFriendlyName + '")\n')
        rScript.write('        '+feature+pTargetVariableKey+'<-rbind('+feature+pTargetVariableKey+',temp)\n')    
        rScript.write('        rm(temp)\n')
        rScript.write('    }\n')
        rScript.write('    print ("Reading '+ featureNameWithoutBrackets +'.feature' + '") \n')
        rScript.write('}\n')
        userFriendlyName = features[feature] 
        rScript.write('tempXY <- sum('+pTargetVariableKey+'[,2] * '+ feature+pTargetVariableKey+'[,2] )\n')
        rScript.write('tempY2 <- sum('+pTargetVariableKey+'[,2] ^ 2 )\n')
        rScript.write('tempX2 <- sum('+feature+pTargetVariableKey+'[,2] ^ 2 )\n')
        rScript.write('tempY <- sum('+pTargetVariableKey+'[,2] )\n')
        rScript.write('tempX <- sum('+feature+pTargetVariableKey+'[,2] )\n')
        rScript.write('n <- length('+feature+pTargetVariableKey+'[,2] )\n')
        rScript.write('string_intercept = paste("'+ userFriendlyName +'_XY" ,"=",toString(tempXY),"\\n"')
        rScript.write(',"'+ userFriendlyName +'_Y2" ,"=",toString(tempY2),"\\n"')
        rScript.write(',"'+ userFriendlyName +'_X2" ,"=",toString(tempX2),"\\n"')
        rScript.write(',"'+ userFriendlyName +'_Y" ,"=",toString(tempY),"\\n"')
        rScript.write(',"'+ userFriendlyName +'_X" ,"=",toString(tempX),"\\n"')
        rScript.write(',"'+ userFriendlyName +'_n" ,"=",toString(n),"\\n"')
        rScript.write(',sep="")\n')
        rScript.write('cat(string_intercept,file="'+ pFileName + '",sep="",append=TRUE)\n')
        rScript.write('rm('+ feature+pTargetVariableKey + ')\n')
    rScript.write('string_intercept = paste("\\n","\\n",sep="")\n')
    rScript.write('cat(string_intercept,file="'+ pFileName + '",sep="",append=TRUE)\n')
    
def saveTrainingModel(rScript,args,path,pTargetVariableKey,pDouble="", treeOrNot = "", treeFileName = ""):
    algo = getAlgoName(args)    
    if len(pDouble)==0:
        outputFileName = path+'/'+algo+pTargetVariableKey+ '-td.' + os.path.basename(os.path.abspath(args.td)) + '-dt.' + args.dt + '-targetClass.' + \
                         args.targetClass + "-wt." + args.wt+ attribute.generateExtension()  +'.model'
        modelValueFileName = path+'/'+algo+ '-td.' + os.path.basename(os.path.abspath(args.td)) + '-dt.' + args.dt + '-targetClass.' + \
                         args.targetClass + "-wt." + args.wt+ attribute.generateExtension()  +'.coef'
    else:
        outputFileName = path+'/'+algo+pTargetVariableKey+ '-td.' + os.path.basename(os.path.abspath(args.td)) + '-dt.' + args.dt + '-targetClass.' + \
                         args.targetClass + "-wt." + args.wt+ attribute.generateExtension()  +'double.model'
        modelValueFileName = path+'/'+algo+ '-td.' + os.path.basename(os.path.abspath(args.td)) + '-dt.' + args.dt + '-targetClass.' + \
                         args.targetClass + "-wt." + args.wt+ attribute.generateExtension()  +'double.coef'        
    rScript.write('\nprint (paste("Section8: Saving the model in file '+ outputFileName +'")) \n')
    rScript.write('save(fit, file = "'+ outputFileName+'")\n')
    rScript.write('l = coef(fit, s = "lambda.min")\n')
    rScript.write('string_intercept = paste("' + pTargetVariableKey + '" , "-intercept-value = ",toString(l[1]),"\\n",sep="")\n')
    rScript.write('string_intercept = paste(string_intercept,"vector-of-alphas-'+ pTargetVariableKey + ' = ",sep="")\n')
    rScript.write('for(i in 2:length(l)){\n')
    rScript.write('    string_intercept = paste(string_intercept,l[i],",",sep="")\n')
    rScript.write('}\n')         
    rScript.write('string_intercept = paste(string_intercept,"\\n",sep="")\n')
    rScript.write('cat(string_intercept,file="'+ modelValueFileName + '",sep="",append=TRUE)\n')
            
def ToCreateDataFrameForTraining(rScript,config,pTargetVariableKey):
    features = config["features-"+pTargetVariableKey]
    rScript.write('\nprint ("Section6: Creating the data frame") \n')
    rScript.write('df = data.frame('+config["target"][pTargetVariableKey]+'='+pTargetVariableKey+'[,2]')
    for feature in features:
        userFriendlyName = features[feature] 
        userFriendlyName = userFriendlyName.replace('[','')
        userFriendlyName = userFriendlyName.replace(']','')
        userFriendlyName = userFriendlyName.replace('(','')
        userFriendlyName = userFriendlyName.replace(')','')
        rScript.write(','+userFriendlyName+'='+feature+pTargetVariableKey+'[,2]')
    rScript.write(")\n\n")

def ToRenameDataBeforeTraining(rScript,config,pTargetVariableKey):
    features = config["features-"+pTargetVariableKey]
    rScript.write('\nprint ("Section6: Renaming the variables") \n')
    rScript.write(pTargetVariableKey+'='+pTargetVariableKey+'[,2]\n')
    for feature in features:
        rScript.write(feature+'='+feature+pTargetVariableKey+'[,2]\n')
    rScript.write("\n")
        

def forPreparingWtVectorForDoubleTraining(rScript,args,pTargetVariableKey):
    rScript.write('Prob <- predict (fit, newx = X , s = "lambda.min",type = "response")')
    rScript.write("\n\n")  
    rScript.write('weightVector = ifelse(' + pTargetVariableKey + '[,2] == 1, Prob, 1 - Prob)\n')  
    lStringToRunGlmnet = 'fit = cv.glmnet(x =X, y = as.factor(' + pTargetVariableKey + '[,2]),family=\''+args.targetClass+'\',alpha=1,maxit=200000,weights=weightVector) \n'
    rScript.write(lStringToRunGlmnet) # ref: http://www.stanford.edu/~hastie/glmnet/glmnet_alpha.html

def ForLoadingModel(rScript,args,path,pTargetVariableKey,config):
    features = config["features-"+pTargetVariableKey]
    if(args.a == 'glmnet'):
        rScript.write('print ("Section7: Running glmnet") \n')
        rScript.write('X <- cbind(')
        currentFeatureNumber=0
        for feature in features:
            rScript.write(features.keys()[currentFeatureNumber]+pTargetVariableKey+'[,2]')
            currentFeatureNumber = currentFeatureNumber+1
            if(len(features) > currentFeatureNumber):
                rScript.write(',')
        rScript.write(')\n')

    predictionModel = args.a + pTargetVariableKey + '-td.' + os.path.basename(os.path.abspath(args.td)) + '-dt.' + args.dt + '-targetClass.' + args.targetClass +\
                        "-wt." + args.wt+ attribute.generateExtension()  + '.model'   

    rScript.write('load("'+os.path.dirname(path)+'/'+predictionModel+'")\n')  
           
def ForTraining(rScript,args,config,pTargetVariableKey):
    features = config["features-"+pTargetVariableKey]
    if(args.a == 'glmnet'):
        rScript.write('print ("Section7: Running glmnet") \n')
        rScript.write('X <- cbind(')
        currentFeatureNumber=0
        for feature in features:
            rScript.write(features.keys()[currentFeatureNumber]+pTargetVariableKey+'[,2]')
            currentFeatureNumber = currentFeatureNumber+1
            if(len(features) > currentFeatureNumber):
                rScript.write(',')    
        rScript.write(')\n')
        lStringToRunGlmnet = 'fit = cv.glmnet(x =X, y = as.factor(' + pTargetVariableKey + '[,2]),family=\''+args.targetClass+'\',alpha=1,maxit=200000,weights=weightVector) \n'
        rScript.write(lStringToRunGlmnet) # ref: http://www.stanford.edu/~hastie/glmnet/glmnet_alpha.html
    elif(args.a == 'logitr'):
        rScript.write('print ("Section7: Running logistic regression") \n')
        rScript.write('fit <- glm ('+config["target"][pTargetVariableKey]+' ~ ')
        currentFeatureNumber=0
        for feature in features:
            userFriendlyName = features[feature] 
            userFriendlyName = userFriendlyName.replace('[','')
            userFriendlyName = userFriendlyName.replace(']','')   
            userFriendlyName = userFriendlyName.replace('(','')
            userFriendlyName = userFriendlyName.replace(')','')            
            rScript.write(userFriendlyName)
            currentFeatureNumber = currentFeatureNumber+1
            if(len(features) > currentFeatureNumber):
                rScript.write('+')
        rScript.write(' , data = df,family = binomial(link="logit") ) \n')
    elif(args.a == 'randomForest'):
        rScript.write('print ("Section7: Running random forest training") \n')
        rScript.write('X <- cbind(')
        currentFeatureNumber=0
        for feature in features:
            rScript.write(features.keys()[currentFeatureNumber]+pTargetVariableKey+'[,2]')
            currentFeatureNumber = currentFeatureNumber+1
            if(len(features) > currentFeatureNumber):
                rScript.write(',')    
        rScript.write(')\n')
        rScript.write('fit = randomForest(x =X, y = ' + pTargetVariableKey + '[,2],importance = TRUE, ntree = 100, sampsize = length(' + pTargetVariableKey + '[,2])) \n') 
    elif(args.a == 'bigRandomForest'):
        rScript.write('print("Section7: Running big random forest training") \n')
        rScript.write('require(doParallel) \n')
        rScript.write('registerDoParallel(cores = 8) \n')
        rScript.write('require(bigrf) \n')
        rScript.write('x = data.frame(')
        currentFeatureNumber=0
        for feature in features:
            rScript.write(features.keys()[currentFeatureNumber]+pTargetVariableKey+'[,2]')
            currentFeatureNumber = currentFeatureNumber+1
            if(len(features) > currentFeatureNumber):
                rScript.write(',')    
        rScript.write(')\n')
        rScript.write('y = as.factor(' + pTargetVariableKey + '[,2]) \n')
        rScript.write('fit <- bigrfc(x, y, ntree = 10, maxndsize = 10000) \n')

    elif(args.a == 'mda'):
        rScript.write('print ("Section7: Running mda training") \n')
        rScript.write('X <- cbind(')
        currentFeatureNumber=0
        for feature in features:
            rScript.write(features.keys()[currentFeatureNumber]+pTargetVariableKey+'[,2]')
            currentFeatureNumber = currentFeatureNumber+1
            if(len(features) > currentFeatureNumber):
                rScript.write(',')    
        rScript.write(')\n')
        rScript.write('fit = mda(x =X, y = as.factor(' + pTargetVariableKey + '[,2])) \n')
        
def ForTrainingTree(rScript,args,config,pTargetVariableKey, treeType = '1'):
    features = config["features-"+pTargetVariableKey]
    probs = config["predictions-"+pTargetVariableKey]
    rScript.write('\nprint ("Section7: Running decision tree") \n')
    rScript.write('len = length(' + pTargetVariableKey + ')\n')
    rScript.write('minsp = len * 0.005\n')
    rScript.write('minb = minsp / 3.0\n')
    rScript.write('dep = 10\n')
    rScript.write('tree_' + pTargetVariableKey + ' <- rpart(formula = ')
    rScript.write(pTargetVariableKey + ' ~ ')
    plusFlag = True
    for feature in features:
        if plusFlag == False:
            rScript.write(' + ' + feature)  
        else:
            rScript.write(feature)
            plusFlag = False
    for prob in probs:
        rScript.write(' + ' + prob)
    if treeType == '1':
        rScript.write(', method = "class", ')
    else:
        rScript.write(', method = "anova", ')
    rScript.write('parms = list(split = "information"), control = rpart.control( minsplit = minsp, ')
    rScript.write('minbucket = minb, maxdepth = dep, cp = 0.00001, usesurrogate = 0, maxsurrogate = 0))\n')
    
def saveTrainingTree(rScript,args,path,pTargetVariableKey, treeFileName = ""):
    rScript.write('\nprint ("Section8 : Saving the tree file in ' + treeFileName + '")\n')
    rScript.write('sink("' + treeFileName + '", append = FALSE)\n')
    rScript.write('tree_' + pTargetVariableKey + '\n')
    rScript.write('sink()\n\n')
    
def ForPredictions(rScript,config,args,pathToDesignFile,pTargetVariableKey,pUseWhichArgumentForData=2,pDouble=""):
    features = config["features-"+pTargetVariableKey]
    #Renaming all features if model and predictions are done simultaneously , so that training and prediction data set do not conflict
    algo = getAlgoName(args)
    if len(pDouble)==0:
        predictionModel = algo + pTargetVariableKey + '-td.' + os.path.basename(os.path.abspath(args.td)) + '-dt.' + args.dt + '-targetClass.' + args.targetClass +\
                            "-wt." + args.wt+ attribute.generateExtension()  + '.model'
    else:
        predictionModel = algo + pTargetVariableKey + '-td.' + os.path.basename(os.path.abspath(args.td)) + '-dt.' + args.dt + '-targetClass.' + args.targetClass +\
                            "-wt." + args.wt+ attribute.generateExtension()  + 'double.model'       
    rScript.write('\nprint ("Section6: Read in prediction model'+os.path.dirname(pathToDesignFile)+'/'+predictionModel+'") \n')
    rScript.write('load("'+os.path.dirname(pathToDesignFile)+'/'+predictionModel+'")')

    if(args.a == 'glmnet'):
        rScript.write('\n\nprint ("Section7: Creating data frame") \n')
        rScript.write('df = cbind(')
        currentFeatureNumber=0
        for feature in features:
            rScript.write(feature+pTargetVariableKey+'[,2]')
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
            userFriendlyName = features[feature]
            userFriendlyName = userFriendlyName.replace('[','')
            userFriendlyName = userFriendlyName.replace(']','')  
            userFriendlyName = userFriendlyName.replace('(','')
            userFriendlyName = userFriendlyName.replace(')','')        
            rScript.write(userFriendlyName+'='+feature+pTargetVariableKey+'[,2]')
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
            userFriendlyName = features[feature]
            userFriendlyName = userFriendlyName.replace('[','')
            userFriendlyName = userFriendlyName.replace(']','')  
            userFriendlyName = userFriendlyName.replace('(','')
            userFriendlyName = userFriendlyName.replace(')','')  
            rScript.write(userFriendlyName+'='+feature+pTargetVariableKey+'[,2]')
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
            userFriendlyName = features[feature]
            userFriendlyName = userFriendlyName.replace('[','')
            userFriendlyName = userFriendlyName.replace(']','')  
            userFriendlyName = userFriendlyName.replace('(','')
            userFriendlyName = userFriendlyName.replace(')','')  
            rScript.write(userFriendlyName+'='+feature+pTargetVariableKey+'[,2]')
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
    rScript.write('dfForFile <- data.frame('+features.keys()[0]+pTargetVariableKey+'[,1]) \n')
    
    rScript.write('\nprint ("Section10: Putting the probabilities in the data frame") \n')
    rScript.write('dfForFile <- cbind(dfForFile,Prob) \n')
   
    if len(pDouble)==0: 
        rScript.write('\nprint ("Section11: Saving the predictions in file /p/'+ os.path.basename(os.path.dirname(args.e))+'/' + args.a + pTargetVariableKey + '-td.' + os.path.basename(os.path.abspath(args.td)) + \
                                 '-dt.' + args.dt + '-targetClass.' + args.targetClass + '-f.' + os.path.basename(os.path.dirname(pathToDesignFile)) + \
                                 "-wt." + args.wt+ attribute.generateExtension()  +'.predictions") \n')
    else:
        rScript.write('\nprint ("Section11: Saving the predictions in file /p/'+ os.path.basename(os.path.dirname(args.e))+'/' + args.a + pTargetVariableKey + '-td.' + os.path.basename(os.path.abspath(args.td)) + \
                                 '-dt.' + args.dt + '-targetClass.' + args.targetClass + '-f.' + os.path.basename(os.path.dirname(pathToDesignFile)) + \
                                 "-wt." + args.wt+ attribute.generateExtension()  +'double.predictions") \n')
    if pUseWhichArgumentForData == 4:
        if len(pDouble)==0:
            rScript.write('fileName = paste(args[4],"/p/","' +os.path.basename(os.path.dirname(args.e))+'/'+ args.a + pTargetVariableKey + '-td.' + os.path.basename(os.path.abspath(args.td)) + \
                                     '-dt.' + args.dt + '-targetClass.' + args.targetClass + '-f.' + os.path.basename(os.path.dirname(pathToDesignFile))+ \
                                     "-wt." + args.wt+ attribute.generateExtension()  +'.predictions",sep="") \n')
        else:
            rScript.write('fileName = paste(args[4],"/p/","' +os.path.basename(os.path.dirname(args.e))+'/'+ args.a + pTargetVariableKey + '-td.' + os.path.basename(os.path.abspath(args.td)) + \
                                     '-dt.' + args.dt + '-targetClass.' + args.targetClass + '-f.' + os.path.basename(os.path.dirname(pathToDesignFile))+ \
                                     "-wt." + args.wt+ attribute.generateExtension()  +'double.predictions",sep="") \n')            
    else:
        if len(pDouble)==0:
            rScript.write('fileName = paste(args[2],"/p/","' +os.path.basename(os.path.dirname(args.e))+'/'+ args.a + pTargetVariableKey + '-td.' + os.path.basename(os.path.abspath(args.td)) + \
                                     '-dt.' + args.dt + '-targetClass.' + args.targetClass + '-f.' + os.path.basename(os.path.dirname(pathToDesignFile)) +\
                                     "-wt." + args.wt+ attribute.generateExtension()  + '.predictions",sep="") \n')
        else:
            rScript.write('fileName = paste(args[2],"/p/","' +os.path.basename(os.path.dirname(args.e))+'/'+ args.a + pTargetVariableKey + '-td.' + os.path.basename(os.path.abspath(args.td)) + \
                                     '-dt.' + args.dt + '-targetClass.' + args.targetClass + '-f.' + os.path.basename(os.path.dirname(pathToDesignFile)) +\
                                     "-wt." + args.wt+ attribute.generateExtension()  + 'double.predictions",sep="") \n')
            
    rScript.write('print (fileName) \n')
    rScript.write('write.table(format(dfForFile,digits=16), file = fileName,sep=",",quote=FALSE)\n')
    

    
