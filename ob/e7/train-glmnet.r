#!/usr/bin/Rscript 
require (glmnet) 
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
print ("Reading in fAskP0OfCurrentRow.feature") 
feature3=read.csv(paste(args[2],"fAskP0OfCurrentRow.feature",sep=""), header=FALSE) 
print ("Reading in fAskP1OfCurrentRow.feature") 
feature4=read.csv(paste(args[2],"fAskP1OfCurrentRow.feature",sep=""), header=FALSE) 
print ("Reading in fBidQ0OfCurrentRow.feature") 
feature5=read.csv(paste(args[2],"fBidQ0OfCurrentRow.feature",sep=""), header=FALSE) 
print ("Reading in fBidQ1OfCurrentRow.feature") 
feature6=read.csv(paste(args[2],"fBidQ1OfCurrentRow.feature",sep=""), header=FALSE) 
print ("Reading in fBidQ2OfCurrentRow.feature") 
feature7=read.csv(paste(args[2],"fBidQ2OfCurrentRow.feature",sep=""), header=FALSE) 
print ("Reading in fBidQ3OfCurrentRow.feature") 
feature8=read.csv(paste(args[2],"fBidQ3OfCurrentRow.feature",sep=""), header=FALSE) 
print ("Reading in fBidQ4OfCurrentRow.feature") 
feature9=read.csv(paste(args[2],"fBidQ4OfCurrentRow.feature",sep=""), header=FALSE) 
print ("Reading in fAskQ0OfCurrentRow.feature") 
feature10=read.csv(paste(args[2],"fAskQ0OfCurrentRow.feature",sep=""), header=FALSE) 
print ("Reading in fAskQ1OfCurrentRow.feature") 
feature11=read.csv(paste(args[2],"fAskQ1OfCurrentRow.feature",sep=""), header=FALSE) 
print ("Reading in fAskQ2OfCurrentRow.feature") 
feature12=read.csv(paste(args[2],"fAskQ2OfCurrentRow.feature",sep=""), header=FALSE) 
print ("Reading in fAskQ3OfCurrentRow.feature") 
feature13=read.csv(paste(args[2],"fAskQ3OfCurrentRow.feature",sep=""), header=FALSE) 
print ("Reading in fAskQ4OfCurrentRow.feature") 
feature14=read.csv(paste(args[2],"fAskQ4OfCurrentRow.feature",sep=""), header=FALSE) 
print ("Reading in fLTPOfCurrentRow.feature") 
feature15=read.csv(paste(args[2],"fLTPOfCurrentRow.feature",sep=""), header=FALSE) 
print ("Reading in fRatioOfBidQSumAskQSumOfCurrentRow.feature") 
feature16=read.csv(paste(args[2],"fRatioOfBidQSumAskQSumOfCurrentRow.feature",sep=""), header=FALSE) 

print ("Section4: Making sure all feature vectors are of same length") 
if (length(feature1$V1) != length(feature2$V1)) { 
print ("The feature lengths do not match for feature1fBidP0OfCurrentRow and feature2fBidP1OfCurrentRow") 
quit() 
}else{ 
print ("Length of feature1 is same as length of feature2")
}
if (length(feature2$V1) != length(feature3$V1)) { 
print ("The feature lengths do not match for feature2fBidP1OfCurrentRow and feature3fAskP0OfCurrentRow") 
quit() 
}else{ 
print ("Length of feature2 is same as length of feature3")
}
if (length(feature3$V1) != length(feature4$V1)) { 
print ("The feature lengths do not match for feature3fAskP0OfCurrentRow and feature4fAskP1OfCurrentRow") 
quit() 
}else{ 
print ("Length of feature3 is same as length of feature4")
}
if (length(feature4$V1) != length(feature5$V1)) { 
print ("The feature lengths do not match for feature4fAskP1OfCurrentRow and feature5fBidQ0OfCurrentRow") 
quit() 
}else{ 
print ("Length of feature4 is same as length of feature5")
}
if (length(feature5$V1) != length(feature6$V1)) { 
print ("The feature lengths do not match for feature5fBidQ0OfCurrentRow and feature6fBidQ1OfCurrentRow") 
quit() 
}else{ 
print ("Length of feature5 is same as length of feature6")
}
if (length(feature6$V1) != length(feature7$V1)) { 
print ("The feature lengths do not match for feature6fBidQ1OfCurrentRow and feature7fBidQ2OfCurrentRow") 
quit() 
}else{ 
print ("Length of feature6 is same as length of feature7")
}
if (length(feature7$V1) != length(feature8$V1)) { 
print ("The feature lengths do not match for feature7fBidQ2OfCurrentRow and feature8fBidQ3OfCurrentRow") 
quit() 
}else{ 
print ("Length of feature7 is same as length of feature8")
}
if (length(feature8$V1) != length(feature9$V1)) { 
print ("The feature lengths do not match for feature8fBidQ3OfCurrentRow and feature9fBidQ4OfCurrentRow") 
quit() 
}else{ 
print ("Length of feature8 is same as length of feature9")
}
if (length(feature9$V1) != length(feature10$V1)) { 
print ("The feature lengths do not match for feature9fBidQ4OfCurrentRow and feature10fAskQ0OfCurrentRow") 
quit() 
}else{ 
print ("Length of feature9 is same as length of feature10")
}
if (length(feature10$V1) != length(feature11$V1)) { 
print ("The feature lengths do not match for feature10fAskQ0OfCurrentRow and feature11fAskQ1OfCurrentRow") 
quit() 
}else{ 
print ("Length of feature10 is same as length of feature11")
}
if (length(feature11$V1) != length(feature12$V1)) { 
print ("The feature lengths do not match for feature11fAskQ1OfCurrentRow and feature12fAskQ2OfCurrentRow") 
quit() 
}else{ 
print ("Length of feature11 is same as length of feature12")
}
if (length(feature12$V1) != length(feature13$V1)) { 
print ("The feature lengths do not match for feature12fAskQ2OfCurrentRow and feature13fAskQ3OfCurrentRow") 
quit() 
}else{ 
print ("Length of feature12 is same as length of feature13")
}
if (length(feature13$V1) != length(feature14$V1)) { 
print ("The feature lengths do not match for feature13fAskQ3OfCurrentRow and feature14fAskQ4OfCurrentRow") 
quit() 
}else{ 
print ("Length of feature13 is same as length of feature14")
}
if (length(feature14$V1) != length(feature15$V1)) { 
print ("The feature lengths do not match for feature14fAskQ4OfCurrentRow and feature15fLTPOfCurrentRow") 
quit() 
}else{ 
print ("Length of feature14 is same as length of feature15")
}
if (length(feature15$V1) != length(feature16$V1)) { 
print ("The feature lengths do not match for feature15fLTPOfCurrentRow and feature16fRatioOfBidQSumAskQSumOfCurrentRow") 
quit() 
}else{ 
print ("Length of feature15 is same as length of feature16")
}

print ("Section5: Making sure all feature vectors have same time stamp over each row") 
if (all(feature1$V1 == feature2$V1) != TRUE) { 
print ("The feature timestamps do not match for feature1fBidP0OfCurrentRow and feature2fBidP1OfCurrentRow") 
quit() 
}else{ 
print ("Timestamps of feature1 is same as timestamp of feature2")
}
if (all(feature2$V1 == feature3$V1) != TRUE) { 
print ("The feature timestamps do not match for feature2fBidP1OfCurrentRow and feature3fAskP0OfCurrentRow") 
quit() 
}else{ 
print ("Timestamps of feature2 is same as timestamp of feature3")
}
if (all(feature3$V1 == feature4$V1) != TRUE) { 
print ("The feature timestamps do not match for feature3fAskP0OfCurrentRow and feature4fAskP1OfCurrentRow") 
quit() 
}else{ 
print ("Timestamps of feature3 is same as timestamp of feature4")
}
if (all(feature4$V1 == feature5$V1) != TRUE) { 
print ("The feature timestamps do not match for feature4fAskP1OfCurrentRow and feature5fBidQ0OfCurrentRow") 
quit() 
}else{ 
print ("Timestamps of feature4 is same as timestamp of feature5")
}
if (all(feature5$V1 == feature6$V1) != TRUE) { 
print ("The feature timestamps do not match for feature5fBidQ0OfCurrentRow and feature6fBidQ1OfCurrentRow") 
quit() 
}else{ 
print ("Timestamps of feature5 is same as timestamp of feature6")
}
if (all(feature6$V1 == feature7$V1) != TRUE) { 
print ("The feature timestamps do not match for feature6fBidQ1OfCurrentRow and feature7fBidQ2OfCurrentRow") 
quit() 
}else{ 
print ("Timestamps of feature6 is same as timestamp of feature7")
}
if (all(feature7$V1 == feature8$V1) != TRUE) { 
print ("The feature timestamps do not match for feature7fBidQ2OfCurrentRow and feature8fBidQ3OfCurrentRow") 
quit() 
}else{ 
print ("Timestamps of feature7 is same as timestamp of feature8")
}
if (all(feature8$V1 == feature9$V1) != TRUE) { 
print ("The feature timestamps do not match for feature8fBidQ3OfCurrentRow and feature9fBidQ4OfCurrentRow") 
quit() 
}else{ 
print ("Timestamps of feature8 is same as timestamp of feature9")
}
if (all(feature9$V1 == feature10$V1) != TRUE) { 
print ("The feature timestamps do not match for feature9fBidQ4OfCurrentRow and feature10fAskQ0OfCurrentRow") 
quit() 
}else{ 
print ("Timestamps of feature9 is same as timestamp of feature10")
}
if (all(feature10$V1 == feature11$V1) != TRUE) { 
print ("The feature timestamps do not match for feature10fAskQ0OfCurrentRow and feature11fAskQ1OfCurrentRow") 
quit() 
}else{ 
print ("Timestamps of feature10 is same as timestamp of feature11")
}
if (all(feature11$V1 == feature12$V1) != TRUE) { 
print ("The feature timestamps do not match for feature11fAskQ1OfCurrentRow and feature12fAskQ2OfCurrentRow") 
quit() 
}else{ 
print ("Timestamps of feature11 is same as timestamp of feature12")
}
if (all(feature12$V1 == feature13$V1) != TRUE) { 
print ("The feature timestamps do not match for feature12fAskQ2OfCurrentRow and feature13fAskQ3OfCurrentRow") 
quit() 
}else{ 
print ("Timestamps of feature12 is same as timestamp of feature13")
}
if (all(feature13$V1 == feature14$V1) != TRUE) { 
print ("The feature timestamps do not match for feature13fAskQ3OfCurrentRow and feature14fAskQ4OfCurrentRow") 
quit() 
}else{ 
print ("Timestamps of feature13 is same as timestamp of feature14")
}
if (all(feature14$V1 == feature15$V1) != TRUE) { 
print ("The feature timestamps do not match for feature14fAskQ4OfCurrentRow and feature15fLTPOfCurrentRow") 
quit() 
}else{ 
print ("Timestamps of feature14 is same as timestamp of feature15")
}
if (all(feature15$V1 == feature16$V1) != TRUE) { 
print ("The feature timestamps do not match for feature15fLTPOfCurrentRow and feature16fRatioOfBidQSumAskQSumOfCurrentRow") 
quit() 
}else{ 
print ("Timestamps of feature15 is same as timestamp of feature16")
}

print ("Section6: Creating the data frame") 
df = data.frame(tBidEqualToAskInNext100=targetVector$V2,fBidP0OfCurrentRow=feature1$V2,fBidP1OfCurrentRow=feature2$V2,fAskP0OfCurrentRow=feature3$V2,fAskP1OfCurrentRow=feature4$V2,fBidQ0OfCurrentRow=feature5$V2,fBidQ1OfCurrentRow=feature6$V2,fBidQ2OfCurrentRow=feature7$V2,fBidQ3OfCurrentRow=feature8$V2,fBidQ4OfCurrentRow=feature9$V2,fAskQ0OfCurrentRow=feature10$V2,fAskQ1OfCurrentRow=feature11$V2,fAskQ2OfCurrentRow=feature12$V2,fAskQ3OfCurrentRow=feature13$V2,fAskQ4OfCurrentRow=feature14$V2,fLTPOfCurrentRow=feature15$V2,fRatioOfBidQSumAskQSumOfCurrentRow=feature16$V2)

print ("Section7: Running glmnet") 
X <- cbind(feature1$V2,feature2$V2,feature3$V2,feature4$V2,feature5$V2,feature6$V2,feature7$V2,feature8$V2,feature9$V2,feature10$V2,feature11$V2,feature12$V2,feature13$V2,feature14$V2,feature15$V2,feature16$V2)
fit <- glmnet (x = X, y = targetVector$V2)
cvfit = cv.glmnet(x =X, y = targetVector$V2) 
fit <- cvfit
print (paste("Section8: Saving the model in file ob/e7/glmnet.model")) 
save(fit, file = "ob/e7/glmnet.model")