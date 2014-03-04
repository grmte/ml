rm(list=ls())
require(glmnet)
getwd()
setwd("~/Downloads/data/")
trainingData=read.csv("M2-D7-Expiry-25FebY14-USDINR--1-0-pdepth-5.txt",header=TRUE,sep=";")
str(trainingData)
summary(trainingData)
trainingData[2,]
plot(trainingData$LTP,type="l",col="red")
par(new=T)
plot(trainingData$AskP0,type="l",col="green")
par(new=T)
plot(trainingData$BidP0,type="l",col="black")

targetVector=read.csv("M2-D7-Expiry-25FebY14-USDINR--1-0-pdepth-5.txt.target")
df = data.frame(target=targetVector,
				AskP0=trainingData$AskP0,BidP0=trainingData$BidP0,AskQ0=trainingData$AskQ0,BidQ0=trainingData$BidQ0,
				AskP1=trainingData$AskP1,BidP1=trainingData$BidP1,AskQ1=trainingData$AskQ1,BidQ1=trainingData$BidQ1,
                AskP2=trainingData$AskP2,BidP2=trainingData$BidP2,AskQ2=trainingData$AskQ2,BidQ2=trainingData$BidQ2,
                AskP3=trainingData$AskP3,BidP3=trainingData$BidP3,AskQ3=trainingData$AskQ3,BidQ3=trainingData$BidQ3,
                LTP=trainingData$LTP
                )

# Running glmnet model
dfm <- as.matrix(df[,-1])
Y <- targetVector[ ,1 ]
glmmodel <- cv.glmnet(dfm,Y,family="binomial",nfold=5,type.measure="class")

# Running logistic regression from https://www.youtube.com/watch?v=1mJlgets6ds
logistic.fit <- glm (X0 ~ AskP0 + BidP0 + AskQ0 + BidQ0 + AskP1 + BidP1+ AskQ1 + BidQ1 +AskP2+BidP2 +AskQ2 + BidQ2 + AskP3+BidP3 +AskQ3 + BidQ3 + LTP, data = df,family = binomial(link="logit") )
summary(logistic.fit)
confint(logistic.fit)

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
