rm(list=ls())
getwd()
setwd("~/Downloads/data/")

# Now we will load another days data and run prediction on that data
testData=read.csv("M2-D6-Expiry-25FebY14-USDINR--1-0-pdepth-5.txt",header=TRUE,sep=";")
testDF = data.frame(AskP0=testData$AskP0,BidP0=testData$BidP0,AskQ0=testData$AskQ0,BidQ0=testData$BidQ0,
	AskP1=testData$AskP1,BidP1=testData$BidP1,AskQ1=testData$AskQ1,BidQ1=testData$BidQ1,
	AskP2=testData$AskP2,BidP2=testData$BidP2,AskQ2=testData$AskQ2,BidQ2=testData$BidQ2,
	AskP3=testData$AskP3,BidP3=testData$BidP3,AskQ3=testData$AskQ3,BidQ3=testData$BidQ3,
  LTP=testData$LTP)
testData$Prob <- predict(logistic.fit, newdata = testDF, type = "response")
head(testData)
fileOutput = data.frame(testData$Prob,testData$TimeStamp)
write.table(fileOutput,file="d6-r-predictions.txt",sep=";")
