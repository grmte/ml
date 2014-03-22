#!/usr/bin/python
from __future__ import division
import os, sys, argparse
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
    print "Predicted values file : "+ predictedValuesFileName
    sys.stdout.flush()
    predictedValuesFile = open(predictedValuesFileName)
    fileHasHeader = True
    numberOfLinesInPredictedValuesFile = 0
    for line in predictedValuesFile:
        if fileHasHeader == True:
            fileHasHeader = False
            continue
        line=line.rstrip('\n')
        splitLine = line.split(',',2)
        timeStamp = float(splitLine[1])
        predictedProb = float(splitLine[2])
        pPredictedValuesDict[timeStamp] = predictedProb
        numberOfLinesInPredictedValuesFile += 1
    print "Finished reading the predicted values file"    
    print "The number of elements in the predicted values dictionary is : " + str(len(pPredictedValuesDict))
    if (numberOfLinesInPredictedValuesFile != len(pPredictedValuesDict)):
        print "Number of duplicate timestamps rejected = " + str(numberOfLinesInPredictedValuesFile - len(pPredictedValuesDict))
        os._exit(-1)
    sys.stdout.flush()

def checkIfPreviousDecisionToEnterOrExitTradeWasSuccessful(pCurrentDataRow,pTTQAtTimeOfPreviousDateRow,pAskP0AtTimeOfPreviousDataRow, pBidP0AtTimeOfPreviousDataRow, pEnterTrade, pTradeStats,pCurrentPosition,pReasonForBuyTrade):
    if(pEnterTrade == 0):
        return
    elif(pEnterTrade == -1 and pCurrentPosition > 0): # Need to sell
        currentLTP = float(pCurrentDataRow[colNumberOfData.LTP])
        currentTTQ = float(pCurrentDataRow[colNumberOfData.TTQ])    
        if(currentLTP == pAskP0AtTimeOfPreviousDataRow and currentTTQ > pTTQAtTimeOfPreviousDateRow): # if false hence i was able to sell
            pTradeStats['totalSellPrice'] += 1 * pAskP0AtTimeOfPreviousDataRow
            pCurrentPosition -= 1
    elif(pEnterTrade == 1 and pCurrentPosition == 0): # Need to buy
        currentLTP = float(pCurrentDataRow[colNumberOfData.LTP])
        currentTTQ = float(pCurrentDataRow[colNumberOfData.TTQ])             
        # Let me find out if i was able to buy
        if(currentTTQ <= pTTQAtTimeOfPreviousDateRow):
            pReasonForBuyTrade['VolumeDidNotIncrease'] += 1
        elif(currentLTP != pBidP0AtTimeOfPreviousDataRow): 
            pReasonForBuyTrade['LTPDoesNotEqualBidP0'] += 1
        else:    
            pReasonForBuyTrade['AssumingTradeHappened'] += 1
            pTradeStats['totalBuyPrice'] += 1 * pBidP0AtTimeOfPreviousDataRow
            pCurrentPosition += 1

def main():
   dataFile.getDataIntoMatrix(args.d)
   predictedValuesDict = dict()
   getPredictedValuesIntoDict(predictedValuesDict)
   enterTrade = 0
   currentPosition = 0
   ttqAtTimeOfPreviousDataRow = 0
   askP0AtTimeOfPreviousDataRow = 0
   bidP0AtTimeOfPreviousDataRow = 0
   tradeStats = dict()
   tradeStats['totalSalePrice'] = 0
   tradeStats['totalBuyPrice'] = 0
   noPredictionForThisRow = 0
   currentPredictedValue = 0
   entryCL = float(args.entryCL)
   exitCL = float(args.exitCL)
   numberOfTimesAskedToEnterTrade = 0
   numberOfTimesAskedToExitTrade = 0
   reasonForBuyTrade = dict()
   reasonForBuyTrade['LTPDoesNotEqualBidP0'] = 0
   reasonForBuyTrade['VolumeDidNotIncrease'] = 0
   reasonForBuyTrade['AssumingTradeHappened'] = 0


   print "Processing the data file for trades :"

   for currentDataRow in dataFile.matrix:
       checkIfPreviousDecisionToEnterOrExitTradeWasSuccessful(currentDataRow,ttqAtTimeOfPreviousDataRow,askP0AtTimeOfPreviousDataRow,bidP0AtTimeOfPreviousDataRow,enterTrade,tradeStats,currentPosition,reasonForBuyTrade)
       currentTimeStamp = common.convertTimeStampFromStringToFloat(currentDataRow[colNumberOfData.TimeStamp])

       try:
           currentPredictedValue = float(predictedValuesDict[currentTimeStamp])
       except:
           noPredictionForThisRow += 1

       if(currentPredictedValue > entryCL):
           enterTrade = 1
           numberOfTimesAskedToEnterTrade += 1
       elif(currentPredictedValue < exitCL):
           numberOfTimesAskedToExitTrade += 1
           enterTrade = -1  # Implies to exit the trade
       else:
           enterTrade = 0  # Implies make no change

       ttqAtTimeOfPreviousDataRow = float(currentDataRow[colNumberOfData.TTQ]) 
       askP0AtTimeOfPreviousDataRow = float(currentDataRow[colNumberOfData.AskP0])
       bidP0AtTimeOfPreviousDataRow = float(currentDataRow[colNumberOfData.BidP0])
    
   print "The net results are: " + str(tradeStats['totalSalePrice'] - tradeStats['totalBuyPrice'])    
   print "Number of rows for which there is no prediction: " + str(noPredictionForThisRow)    
   print "Number of times asked to enter trade: " + str(numberOfTimesAskedToEnterTrade)    
   print "Number of times asked to exit trade: " + str(numberOfTimesAskedToExitTrade)    
   print "Assumed trade did not happen since volume did not increase: " + str(reasonForBuyTrade['VolumeDidNotIncrease'])
   print "Assumed trade did not happen since bidP0 not same as LTP: " + str(reasonForBuyTrade['LTPDoesNotEqualBidP0'])
   print "Assumed trade happened: " + str(reasonForBuyTrade['AssumingTradeHappened'])

if __name__ == "__main__":
    main()

