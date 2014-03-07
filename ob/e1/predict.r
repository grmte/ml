#!/usr/bin/Rscript 
print ("Section1: Setting the environment") 
rm(list=ls()) 
setwd("~/Downloads/src/data/20140207/") 


print ("Section2: Read in the feature files") 
feature1=read.csv("fBidP0OfCurrentRow.feature", header=FALSE) 
feature2=read.csv("fLTPOfCurrentRow.feature", header=FALSE) 

print ("Section3: Read in the prediction model") 
load("ob/e1/design.model")

print ("Section4: Creating the data frame") 
df = data.frame(fBidP0OfCurrentRow=feature1$V2,fLTPOfCurrentRow=feature2$V2)

print ("Section5: Running logistic regression prediction") 
df$Prob <- predict (logistic.fit, newdata = df, type = "response")


print ("Section6: Saving the predictions in directory ~/Downloads/src/data/20140207/ in file ob/e1/design.predictions") 
write.table(df, file = "ob/e1/design.predictions")