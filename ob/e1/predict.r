#!/usr/bin/Rscript 
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

print ("Section2: Read in the feature files") 
feature1=read.csv(paste(args[2],"fBidP0OfCurrentRow.feature",sep=""), header=FALSE) 
feature2=read.csv(paste(args[2],"fLTPOfCurrentRow.feature",sep=""), header=FALSE) 

print ("Section3: Read in the prediction model") 
load("ob/e1//design.model")

print ("Section4: Creating the data frame") 
df = data.frame(fBidP0OfCurrentRow=feature1$V2,fLTPOfCurrentRow=feature2$V2)

print ("Section5: Running logistic regression prediction") 
df$Prob <- predict (logistic.fit, newdata = df, type = "response")


print ("Section6: Saving the predictions in file e1.predictions") 
fileName = paste(args[2],"e1.predictions",sep="") 
print (fileName) 
write.table(df, file = fileName)