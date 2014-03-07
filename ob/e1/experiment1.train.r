#!/usr/bin/Rscript 
print ("Section1: Setting the environment") 
rm(list=ls()) 
setwd("~/Downloads/src/data/20140207/") 

print ("Section2: Read in the target files") 
targetVector=read.csv("tBidGreaterThanAskInNext100.target", header=FALSE) 


print ("Section3: Read in the feature files") 
feature1=read.csv("fBidP0OfCurrentRow.feature", header=FALSE) 
feature2=read.csv("fLTPOfCurrentRow.feature", header=FALSE) 

print ("Section4: Creating the data frame") 
df = data.frame(tBidGreaterThanAskInNext100=targetVector$V2,fBidP0OfCurrentRow=feature1$V2,fLTPOfCurrentRow=feature2$V2)

print ("Section5: Running logistic regression") 
logistic.fit <- glm (tBidGreaterThanAskInNext100 ~ fBidP0OfCurrentRow+fLTPOfCurrentRow , data = df,family = binomial(link="logit") ) 

print ("Section6: Saving the model in directory ~/Downloads/src/data/20140207/ in file experiment1.model") 
save(logistic.fit, file = "experiment1.model")