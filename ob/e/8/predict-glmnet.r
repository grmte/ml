#!/usr/bin/Rscript 
require (glmnet) 
print ("Section1: Setting the environment") 
rm(list=ls()) 
args <- commandArgs(trailingOnly = TRUE) 
if(length(args) < 2) 
{ 
  stop("Not enough arguments. Please supply 2 arguments.") 
} 
if((args[1]=="-d") == TRUE ) { 
   print ("Parameter check passed") 
}else{ 
   stop ("cannot proceed. Specify the parameters properly. The correct way to use this is predict.r -d data/20140207") 
} 
print ("Section2: checking if the predictions file already exists") 
fileName = paste(args[2],"e8glmnet.predictions",sep="") 
if(file.exists(fileName)){ 
    stop ('The predictions already exist. Delete it and then run the program again') 
} 

print ("Section3: Read in the feature files") 
print ("Reading in fBidP0OfCurrentRow.feature") 
feature1=read.csv(paste(args[2],"fBidP0OfCurrentRow.feature",sep=""), header=FALSE) 
print ("Reading in fBidP1OfCurrentRow.feature") 
feature2=read.csv(paste(args[2],"fBidP1OfCurrentRow.feature",sep=""), header=FALSE) 

print ("Section4: Making sure all feature vectors are of same length") 
if (length(feature1$V1) != length(feature2$V1)) { 
print ("The feature lengths do not match for feature1fBidP0OfCurrentRow and feature2fBidP1OfCurrentRow") 
quit() 
}else{ 
print ("Length of feature1 is same as length of feature2")
}

print ("Section5: Making sure all feature vectors have same time stamp over each row") 
if (all(feature1$V1 == feature2$V1) != TRUE) { 
print ("The feature timestamps do not match for feature1fBidP0OfCurrentRow and feature2fBidP1OfCurrentRow") 
quit() 
}else{ 
print ("Timestamps of feature1 is same as timestamp of feature2")
}

print ("Section6: Read in the prediction model") 
load("ob/e8//glmnet.model")

print ("Section7: Creating the data frame") 
df = cbind(feature1$V2,feature2$V2)

print ("Section8: Running glmnet prediction") 
df$Prob <- predict (logistic.fit, newx = df)


print ("Section9: Creating the data frame to write in the file") 
dfForFile <- data.frame(feature1$V1) 

print ("Section10: Putting the probabilities in the data frame") 
dfForFile <- cbind(dfForFile,df$Prob) 

print ("Section11: Saving the predictions in file e8glmnet.predictions") 
fileName = paste(args[2],"e8glmnet.predictions",sep="") 
print (fileName) 
write.table(format(dfForFile,digits=16), file = fileName,sep=",",quote=FALSE)