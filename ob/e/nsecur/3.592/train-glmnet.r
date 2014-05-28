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
targetVector=read.csv(paste(args[2],"/t/","tAverageOfNFutureLTPIsGreaterThanCurrentLTP.target",sep=""), header=FALSE) 


print ("Section3: Read in the feature files") 
print ("Reading in fColBidQ0InCurrentRow.feature") 
feature1=read.csv(paste(args[2],"/f/","fColBidQ0InCurrentRow.feature",sep=""), header=FALSE) 
print ("Reading in fColBidQ1InCurrentRow.feature") 
feature2=read.csv(paste(args[2],"/f/","fColBidQ1InCurrentRow.feature",sep=""), header=FALSE) 
print ("Reading in fColBidQ2InCurrentRow.feature") 
feature3=read.csv(paste(args[2],"/f/","fColBidQ2InCurrentRow.feature",sep=""), header=FALSE) 
print ("Reading in fColBidQ3InCurrentRow.feature") 
feature4=read.csv(paste(args[2],"/f/","fColBidQ3InCurrentRow.feature",sep=""), header=FALSE) 
print ("Reading in fColBidQ4InCurrentRow.feature") 
feature5=read.csv(paste(args[2],"/f/","fColBidQ4InCurrentRow.feature",sep=""), header=FALSE) 
print ("Reading in fColAskQ0InCurrentRow.feature") 
feature6=read.csv(paste(args[2],"/f/","fColAskQ0InCurrentRow.feature",sep=""), header=FALSE) 
print ("Reading in fColAskQ1InCurrentRow.feature") 
feature7=read.csv(paste(args[2],"/f/","fColAskQ1InCurrentRow.feature",sep=""), header=FALSE) 
print ("Reading in fColAskQ2InCurrentRow.feature") 
feature8=read.csv(paste(args[2],"/f/","fColAskQ2InCurrentRow.feature",sep=""), header=FALSE) 
print ("Reading in fColAskQ3InCurrentRow.feature") 
feature9=read.csv(paste(args[2],"/f/","fColAskQ3InCurrentRow.feature",sep=""), header=FALSE) 
print ("Reading in fColAskQ4InCurrentRow.feature") 
feature10=read.csv(paste(args[2],"/f/","fColAskQ4InCurrentRow.feature",sep=""), header=FALSE) 
print ("Reading in fRatioOfBidQSumAskQSumInCurrentRow.feature") 
feature11=read.csv(paste(args[2],"/f/","fRatioOfBidQSumAskQSumInCurrentRow.feature",sep=""), header=FALSE) 
print ("Reading in fColLTPInCurrentRow[DivideBy]fMovingAverageOfColLTPInLast200Rows.feature") 
feature12=read.csv(paste(args[2],"/f/","fColLTPInCurrentRow[DivideBy]fMovingAverageOfColLTPInLast200Rows.feature",sep=""), header=FALSE) 
print ("Reading in fEMovingAverageOfColBidP0InLast500Rows.feature") 
feature13=read.csv(paste(args[2],"/f/","fEMovingAverageOfColBidP0InLast500Rows.feature",sep=""), header=FALSE) 
print ("Reading in fMovingAverageOfColBidP0InLast500Rows.feature") 
feature14=read.csv(paste(args[2],"/f/","fMovingAverageOfColBidP0InLast500Rows.feature",sep=""), header=FALSE) 
print ("Reading in fColBidP0InCurrentRow.feature") 
feature15=read.csv(paste(args[2],"/f/","fColBidP0InCurrentRow.feature",sep=""), header=FALSE) 

print ("Section4: Making sure all feature vectors are of same length") 
if (length(feature1$V1) != length(feature2$V1)) { 
print ("The feature lengths do not match for feature1fColBidQ0InCurrentRow and feature2fColBidQ1InCurrentRow") 
quit() 
}else{ 
print ("Length of feature1 is same as length of feature2")
}
if (length(feature2$V1) != length(feature3$V1)) { 
print ("The feature lengths do not match for feature2fColBidQ1InCurrentRow and feature3fColBidQ2InCurrentRow") 
quit() 
}else{ 
print ("Length of feature2 is same as length of feature3")
}
if (length(feature3$V1) != length(feature4$V1)) { 
print ("The feature lengths do not match for feature3fColBidQ2InCurrentRow and feature4fColBidQ3InCurrentRow") 
quit() 
}else{ 
print ("Length of feature3 is same as length of feature4")
}
if (length(feature4$V1) != length(feature5$V1)) { 
print ("The feature lengths do not match for feature4fColBidQ3InCurrentRow and feature5fColBidQ4InCurrentRow") 
quit() 
}else{ 
print ("Length of feature4 is same as length of feature5")
}
if (length(feature5$V1) != length(feature6$V1)) { 
print ("The feature lengths do not match for feature5fColBidQ4InCurrentRow and feature6fColAskQ0InCurrentRow") 
quit() 
}else{ 
print ("Length of feature5 is same as length of feature6")
}
if (length(feature6$V1) != length(feature7$V1)) { 
print ("The feature lengths do not match for feature6fColAskQ0InCurrentRow and feature7fColAskQ1InCurrentRow") 
quit() 
}else{ 
print ("Length of feature6 is same as length of feature7")
}
if (length(feature7$V1) != length(feature8$V1)) { 
print ("The feature lengths do not match for feature7fColAskQ1InCurrentRow and feature8fColAskQ2InCurrentRow") 
quit() 
}else{ 
print ("Length of feature7 is same as length of feature8")
}
if (length(feature8$V1) != length(feature9$V1)) { 
print ("The feature lengths do not match for feature8fColAskQ2InCurrentRow and feature9fColAskQ3InCurrentRow") 
quit() 
}else{ 
print ("Length of feature8 is same as length of feature9")
}
if (length(feature9$V1) != length(feature10$V1)) { 
print ("The feature lengths do not match for feature9fColAskQ3InCurrentRow and feature10fColAskQ4InCurrentRow") 
quit() 
}else{ 
print ("Length of feature9 is same as length of feature10")
}
if (length(feature10$V1) != length(feature11$V1)) { 
print ("The feature lengths do not match for feature10fColAskQ4InCurrentRow and feature11fRatioOfBidQSumAskQSumInCurrentRow") 
quit() 
}else{ 
print ("Length of feature10 is same as length of feature11")
}
if (length(feature11$V1) != length(feature12$V1)) { 
print ("The feature lengths do not match for feature11fRatioOfBidQSumAskQSumInCurrentRow and feature12fColLTPInCurrentRow[DivideBy]fMovingAverageOfColLTPInLast200Rows") 
quit() 
}else{ 
print ("Length of feature11 is same as length of feature12")
}
if (length(feature12$V1) != length(feature13$V1)) { 
print ("The feature lengths do not match for feature12fColLTPInCurrentRow[DivideBy]fMovingAverageOfColLTPInLast200Rows and feature13fEMovingAverageOfColBidP0InLast500Rows") 
quit() 
}else{ 
print ("Length of feature12 is same as length of feature13")
}
if (length(feature13$V1) != length(feature14$V1)) { 
print ("The feature lengths do not match for feature13fEMovingAverageOfColBidP0InLast500Rows and feature14fMovingAverageOfColBidP0InLast500Rows") 
quit() 
}else{ 
print ("Length of feature13 is same as length of feature14")
}
if (length(feature14$V1) != length(feature15$V1)) { 
print ("The feature lengths do not match for feature14fMovingAverageOfColBidP0InLast500Rows and feature15fColBidP0InCurrentRow") 
quit() 
}else{ 
print ("Length of feature14 is same as length of feature15")
}

print ("Section5: Making sure all feature vectors have same time stamp over each row") 
if (all(feature1$V1 == feature2$V1) != TRUE) { 
print ("The feature timestamps do not match for feature1fColBidQ0InCurrentRow and feature2fColBidQ1InCurrentRow") 
quit() 
}else{ 
print ("Timestamps of feature1 is same as timestamp of feature2")
}
if (all(feature2$V1 == feature3$V1) != TRUE) { 
print ("The feature timestamps do not match for feature2fColBidQ1InCurrentRow and feature3fColBidQ2InCurrentRow") 
quit() 
}else{ 
print ("Timestamps of feature2 is same as timestamp of feature3")
}
if (all(feature3$V1 == feature4$V1) != TRUE) { 
print ("The feature timestamps do not match for feature3fColBidQ2InCurrentRow and feature4fColBidQ3InCurrentRow") 
quit() 
}else{ 
print ("Timestamps of feature3 is same as timestamp of feature4")
}
if (all(feature4$V1 == feature5$V1) != TRUE) { 
print ("The feature timestamps do not match for feature4fColBidQ3InCurrentRow and feature5fColBidQ4InCurrentRow") 
quit() 
}else{ 
print ("Timestamps of feature4 is same as timestamp of feature5")
}
if (all(feature5$V1 == feature6$V1) != TRUE) { 
print ("The feature timestamps do not match for feature5fColBidQ4InCurrentRow and feature6fColAskQ0InCurrentRow") 
quit() 
}else{ 
print ("Timestamps of feature5 is same as timestamp of feature6")
}
if (all(feature6$V1 == feature7$V1) != TRUE) { 
print ("The feature timestamps do not match for feature6fColAskQ0InCurrentRow and feature7fColAskQ1InCurrentRow") 
quit() 
}else{ 
print ("Timestamps of feature6 is same as timestamp of feature7")
}
if (all(feature7$V1 == feature8$V1) != TRUE) { 
print ("The feature timestamps do not match for feature7fColAskQ1InCurrentRow and feature8fColAskQ2InCurrentRow") 
quit() 
}else{ 
print ("Timestamps of feature7 is same as timestamp of feature8")
}
if (all(feature8$V1 == feature9$V1) != TRUE) { 
print ("The feature timestamps do not match for feature8fColAskQ2InCurrentRow and feature9fColAskQ3InCurrentRow") 
quit() 
}else{ 
print ("Timestamps of feature8 is same as timestamp of feature9")
}
if (all(feature9$V1 == feature10$V1) != TRUE) { 
print ("The feature timestamps do not match for feature9fColAskQ3InCurrentRow and feature10fColAskQ4InCurrentRow") 
quit() 
}else{ 
print ("Timestamps of feature9 is same as timestamp of feature10")
}
if (all(feature10$V1 == feature11$V1) != TRUE) { 
print ("The feature timestamps do not match for feature10fColAskQ4InCurrentRow and feature11fRatioOfBidQSumAskQSumInCurrentRow") 
quit() 
}else{ 
print ("Timestamps of feature10 is same as timestamp of feature11")
}
if (all(feature11$V1 == feature12$V1) != TRUE) { 
print ("The feature timestamps do not match for feature11fRatioOfBidQSumAskQSumInCurrentRow and feature12fColLTPInCurrentRow[DivideBy]fMovingAverageOfColLTPInLast200Rows") 
quit() 
}else{ 
print ("Timestamps of feature11 is same as timestamp of feature12")
}
if (all(feature12$V1 == feature13$V1) != TRUE) { 
print ("The feature timestamps do not match for feature12fColLTPInCurrentRow[DivideBy]fMovingAverageOfColLTPInLast200Rows and feature13fEMovingAverageOfColBidP0InLast500Rows") 
quit() 
}else{ 
print ("Timestamps of feature12 is same as timestamp of feature13")
}
if (all(feature13$V1 == feature14$V1) != TRUE) { 
print ("The feature timestamps do not match for feature13fEMovingAverageOfColBidP0InLast500Rows and feature14fMovingAverageOfColBidP0InLast500Rows") 
quit() 
}else{ 
print ("Timestamps of feature13 is same as timestamp of feature14")
}
if (all(feature14$V1 == feature15$V1) != TRUE) { 
print ("The feature timestamps do not match for feature14fMovingAverageOfColBidP0InLast500Rows and feature15fColBidP0InCurrentRow") 
quit() 
}else{ 
print ("Timestamps of feature14 is same as timestamp of feature15")
}

print ("Section6: Creating the data frame") 
df = data.frame(tAverageOfNFutureLTPIsGreaterThanCurrentLTP=targetVector$V2,fColBidQ0InCurrentRow=feature1$V2,fColBidQ1InCurrentRow=feature2$V2,fColBidQ2InCurrentRow=feature3$V2,fColBidQ3InCurrentRow=feature4$V2,fColBidQ4InCurrentRow=feature5$V2,fColAskQ0InCurrentRow=feature6$V2,fColAskQ1InCurrentRow=feature7$V2,fColAskQ2InCurrentRow=feature8$V2,fColAskQ3InCurrentRow=feature9$V2,fColAskQ4InCurrentRow=feature10$V2,fRatioOfBidQSumAskQSumInCurrentRow=feature11$V2,fColLTPInCurrentRowDivideByfMovingAverageOfColLTPInLast200Rows=feature12$V2,fEMovingAverageOfColBidP0InLast500Rows=feature13$V2,fMovingAverageOfColBidP0InLast500Rows=feature14$V2,fColBidP0InCurrentRow=feature15$V2)

print ("Section7: Running glmnet") 
X <- cbind(feature1$V2,feature2$V2,feature3$V2,feature4$V2,feature5$V2,feature6$V2,feature7$V2,feature8$V2,feature9$V2,feature10$V2,feature11$V2,feature12$V2,feature13$V2,feature14$V2,feature15$V2)
fit = cv.glmnet(x =X, y = targetVector$V2) 

print (paste("Section8: Saving the model in file ob/e3.592/glmnet.model")) 
save(fit, file = "ob/e3.592/glmnet.model")