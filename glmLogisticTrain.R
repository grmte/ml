rm(list=ls())
getwd()
setwd("~/Downloads/data/")

trainingData=read.csv("M2-D7-Expiry-25FebY14-USDINR--1-0-pdepth-5.txt",header=TRUE,sep=";")
targetVector=read.csv("M2-D7-Expiry-25FebY14-USDINR--1-0-pdepth-5.txt.target")

df = data.frame(target=targetVector,
				AskP0=trainingData$AskP0,BidP0=trainingData$BidP0,AskQ0=trainingData$AskQ0,BidQ0=trainingData$BidQ0,
				AskP1=trainingData$AskP1,BidP1=trainingData$BidP1,AskQ1=trainingData$AskQ1,BidQ1=trainingData$BidQ1,
                AskP2=trainingData$AskP2,BidP2=trainingData$BidP2,AskQ2=trainingData$AskQ2,BidQ2=trainingData$BidQ2,
                AskP3=trainingData$AskP3,BidP3=trainingData$BidP3,AskQ3=trainingData$AskQ3,BidQ3=trainingData$BidQ3,
                LTP=trainingData$LTP
                )


# Running logistic regression
logistic.fit <- glm (X0 ~ AskP0 + BidP0 + AskQ0 + BidQ0 + AskP1 + BidP1+ AskQ1 + BidQ1 +AskP2+BidP2 +AskQ2 + BidQ2 + AskP3+BidP3 +AskQ3 + BidQ3 + LTP, data = df,family = binomial(link="logit") )
summary(logistic.fit)
confint(logistic.fit)

