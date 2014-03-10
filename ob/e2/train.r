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
targetVector=read.csv(paste(args[2],"tBidGreaterThanAskInNext100.target",sep=""), header=FALSE) 


print ("Section3: Read in the feature files") 
feature1=read.csv(paste(args[2],"fBidP0OfCurrentRow.feature",sep=""), header=FALSE) 
feature2=read.csv(paste(args[2],"fBidP1OfCurrentRow.feature",sep=""), header=FALSE) 
feature3=read.csv(paste(args[2],"fBidP2OfCurrentRow.feature",sep=""), header=FALSE) 
feature4=read.csv(paste(args[2],"fBidP3OfCurrentRow.feature",sep=""), header=FALSE) 
feature5=read.csv(paste(args[2],"fBidP4OfCurrentRow.feature",sep=""), header=FALSE) 
feature6=read.csv(paste(args[2],"fAskP0OfCurrentRow.feature",sep=""), header=FALSE) 
feature7=read.csv(paste(args[2],"fAskP1OfCurrentRow.feature",sep=""), header=FALSE) 
feature8=read.csv(paste(args[2],"fAskP2OfCurrentRow.feature",sep=""), header=FALSE) 
feature9=read.csv(paste(args[2],"fAskP3OfCurrentRow.feature",sep=""), header=FALSE) 
feature10=read.csv(paste(args[2],"fAskP4OfCurrentRow.feature",sep=""), header=FALSE) 
feature11=read.csv(paste(args[2],"fRatioOfBidAskQ0OfCurrentRow.feature",sep=""), header=FALSE) 
feature12=read.csv(paste(args[2],"fRatioOfBidAskQ1OfCurrentRow.feature",sep=""), header=FALSE) 
feature13=read.csv(paste(args[2],"fRatioOfBidAskQ2OfCurrentRow.feature",sep=""), header=FALSE) 
feature14=read.csv(paste(args[2],"fRatioOfBidAskQ3OfCurrentRow.feature",sep=""), header=FALSE) 
feature15=read.csv(paste(args[2],"fRatioOfBidAskQ4OfCurrentRow.feature",sep=""), header=FALSE) 
feature16=read.csv(paste(args[2],"fLTPOfCurrentRow.feature",sep=""), header=FALSE) 

print ("Section4: Creating the data frame") 
df = data.frame(tBidGreaterThanAskInNext100=targetVector$V2,fBidP0OfCurrentRow=feature1$V2,fBidP1OfCurrentRow=feature2$V2,fBidP2OfCurrentRow=feature3$V2,fBidP3OfCurrentRow=feature4$V2,fBidP4OfCurrentRow=feature5$V2,fAskP0OfCurrentRow=feature6$V2,fAskP1OfCurrentRow=feature7$V2,fAskP2OfCurrentRow=feature8$V2,fAskP3OfCurrentRow=feature9$V2,fAskP4OfCurrentRow=feature10$V2,fRatioOfBidAskQ0OfCurrentRow=feature11$V2,fRatioOfBidAskQ1OfCurrentRow=feature12$V2,fRatioOfBidAskQ2OfCurrentRow=feature13$V2,fRatioOfBidAskQ3OfCurrentRow=feature14$V2,fRatioOfBidAskQ4OfCurrentRow=feature15$V2,fLTPOfCurrentRow=feature16$V2)

print ("Section5: Running logistic regression") 
logistic.fit <- glm (tBidGreaterThanAskInNext100 ~ fBidP0OfCurrentRow+fBidP1OfCurrentRow+fBidP2OfCurrentRow+fBidP3OfCurrentRow+fBidP4OfCurrentRow+fAskP0OfCurrentRow+fAskP1OfCurrentRow+fAskP2OfCurrentRow+fAskP3OfCurrentRow+fAskP4OfCurrentRow+fRatioOfBidAskQ0OfCurrentRow+fRatioOfBidAskQ1OfCurrentRow+fRatioOfBidAskQ2OfCurrentRow+fRatioOfBidAskQ3OfCurrentRow+fRatioOfBidAskQ4OfCurrentRow+fLTPOfCurrentRow , data = df,family = binomial(link="logit") ) 

print (paste("Section6: Saving the model in file e2/design.model")) 
save(logistic.fit, file = "e2/design.model")