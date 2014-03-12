#!/usr/bin/Rscript 
print ("Section1: Clearing the environment and making sure the data directory has been passed") 
rm(list=ls()) 
args <- commandArgs(trailingOnly = TRUE) 
if(length(args) < 2) 
{ 
  stop("Not enough arguments. Please supply 2 arguments.") 
} 
if((args[1]=="-d") == TRUE ) { 
   print ("Parameter check passed") 
}else{ 
   stop ("cannot proceed. Specify the parameters properly. The correct way to use this is train.r -d data/20140207") 
} 
print ("Section2: Read in the target files") 
targetVector=read.csv(paste(args[2],"tBidEqualToAskInNext100.target",sep=""), header=FALSE) 


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

print ("Section6: Creating the data frame") 
df = data.frame(tBidEqualToAskInNext100=targetVector$V2,fBidP0OfCurrentRow=feature1$V2,fBidP1OfCurrentRow=feature2$V2)

print ("Section7: Running logistic regression") 
logistic.fit <- glm (tBidEqualToAskInNext100 ~ fBidP0OfCurrentRow+fBidP1OfCurrentRow , data = df,family = binomial(link="logit") ) 

print (paste("Section8: Saving the model in file ob/e8/logitr.model")) 
save(logistic.fit, file = "ob/e8/logitr.model")