#!/usr/bin/python
from __future__ import division
import os, sys, argparse, decimal
from configobj import ConfigObj

parser = argparse.ArgumentParser(description='This program will do trades to measure the quality of the experiment. An e.g. command line is tarde.py -d ob/data/20140207/ -e ob/e/1 -a logitr')
parser.add_argument('-d', required=True,help='Directory of the data file')
parser.add_argument('-e', required=True,help='Directory of the experiment')
parser.add_argument('-a', required=True,help='Algorithm name')
parser.add_argument('-entryCL', required=True,help='Percentage of the confidence level used to enter the trades')
parser.add_argument('-exitCL', required=True,help='Percentage of the confidence level used to exit the trades')
args = parser.parse_args()

sys.path.append("/Users/vikaskedia/ml/src/")
sys.path.append("/Users/vikaskedia/ml/ob/generators/")
import dataFile, colNumberOfData, common

def getPredictedValuesIntoDict(pPredictedValuesDict):
    # The following will take care if args.e = "ob/e1/" or args.e = "ob/e1"
    experimentName = os.path.basename(os.path.abspath(args.e))
    predictedValuesFileName = args.d+"/p/"+experimentName+args.a+".predictions"
    print "Reading predicted values from: "+ predictedValuesFileName
    predictedValuesFile = open(predictedValuesFileName)
    fileHasHeader = True
    timeStampAlreadyExistsInDict = 0
    for line in predictedValuesFile:
        if fileHasHeader == True:
            fileHasHeader = False
            continue
        line=line.rstrip('\n')
        splitLine = line.split(',',2)
        timeStamp = decimal.Decimal(splitLine[1])
        predictedProb = float(splitLine[2])
        if timeStamp in pPredictedValuesDict:
            timeStampAlreadyExistsInDict +=1
            print "This timestamp already exists :" + str(timeStamp)
        else:    
            pPredictedValuesDict[timeStamp] = predictedProb     
    print "Finished reading the predicted values file"    
    print "Number of duplicate timestamps rejected = " + str(timeStampAlreadyExistsInDict)

def checkIfPreviousDecisionToEnterOrExitTradeWasSuccessful(pCurrentDataRow,pTTQAtTimeOfPreviousDateRow,pAskP0AtTimeOfPreviousDataRow, pBidP0AtTimeOfPreviousDataRow, pEnterTrade, pTotalSalePrice, pTotalBuyPrice,pCurrentPosition):
    if(pEnterTrade == 0):
        return
    elif(pEnterTrade == -1 and pCurrentPosition > 0): # Need to sell
        if(pCurrentDataRow[colNumberOfData.LTP] == pAskP0AtTimeOfPreviousDataRow and pCurrentDataRow[colNumberOfData.TTQ] > pTTQAtTimeOfPreviousDateRow):
            pTotalSellPrice = 1 * pAskP0AtTimeOfPreviousDataRow
    elif(pEnterTrade == 1 and pCurrentPosition == 0): # Need to buy
        if(pCurrentDataRow[colNumberOfData.LTP] == pBidP0AtTimeOfPreviousDataRow and pCurrentDataRow[colNumberOfData.TTQ] > pTTQAtTimeOfPreviousDateRow):
            pTotalBuyPrice = 1 * pBidP0AtTimeOfPreviousDataRow

def main():
   dataFile.getDataIntoMatrix(args.d)
   predictedValuesDict = dict()
   getPredictedValuesIntoDict(predictedValuesDict)
   enterTrade = 0
   currentPosition = 0
   ttqAtTimeOfPreviousDataRow = 0
   askP0AtTimeOfPreviousDataRow = 0
   bidP0AtTimeOfPreviousDataRow = 0
   totalSalePrice = 0
   totalBuyPrice = 0
   noPredictionForThisRow = 0
   currentPredictedValue = 0
   entryCL = float(args.entryCL)
   exitCL = float(args.exitCL)

   for currentDataRow in dataFile.matrix:
       checkIfPreviousDecisionToEnterOrExitTradeWasSuccessful(currentDataRow,ttqAtTimeOfPreviousDataRow,askP0AtTimeOfPreviousDataRow,bidP0AtTimeOfPreviousDataRow,enterTrade,totalSalePrice,totalBuyPrice, currentPosition)
       currentTimeStamp = common.convertTimeStampFromStringToDecimal(currentDataRow[colNumberOfData.TimeStamp])

       try:
           currentPredictedValue = float(predictedValuesDict[currentTimeStamp])
       except:
           noPredictionForThisRow += 1

       if(currentPredictedValue > entryCL):
           enterTrade = 1
       elif(currentPredictedValue < exitCL):
           enterTrade = -1  # Implies to exit the trade
       else:
           enterTrade = 0  # Implies make no change

       ttqAtTimeOfPreviousDataRow = currentDataRow[colNumberOfData.TTQ] 
       askP0AtTimeOfPreviousDataRow = float(currentDataRow[colNumberOfData.AskP0])
       bidP0AtTimeOfPreviousDataRow = float(currentDataRow[colNumberOfData.BidP0])
    
   print "The net results are: " + str(totalSalePrice - totalBuyPrice)    
   print "Number of rows for which there is no prediction: " + str(noPredictionForThisRow)    

if __name__ == "__main__":
    main()

