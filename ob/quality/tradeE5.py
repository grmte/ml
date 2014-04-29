#!/usr/bin/python
from __future__ import division
from __future__ import print_function
import os, sys, argparse
from configobj import ConfigObj

parser = argparse.ArgumentParser(description='This program will do trades to measure the quality of the experiment. An e.g. command line is tarde.py -d ob/data/20140207/ -e ob/e/1 -a logitr -entryCL 0.90 -exitCL .55 -entryCLCutoff .75 -exitCLCutoff .55')
parser.add_argument('-d', required=True,help='Directory of the data file')
parser.add_argument('-e', required=True,help='Directory of the experiment')
parser.add_argument('-a', required=True,help='Algorithm name')
parser.add_argument('-entryCL', required=True,help='Percentage of the confidence level used to enter the trades')
parser.add_argument('-exitCL', required=True,help='Percentage of the confidence level used to exit the trades')
args = parser.parse_args()

sys.path.append("./src/")
sys.path.append("./ob/generators/")
import dataFile, colNumberOfData, common

experimentName = os.path.basename(os.path.abspath(args.e))
gTickSize = 25000
def getPredictedValuesIntoDict(pPredictedValuesDict):
    # The following will take care if args.e = "ob/e1/" or args.e = "ob/e1"
    dirName = args.d.replace('/ro/','/wf/')
    predictedValuesFileName = dirName+"/p/"+experimentName+args.a+".predictions"
    print("Predicted values file : "+ predictedValuesFileName)
    sys.stdout.flush()
    predictedValuesFile = open(predictedValuesFileName)
    fileHasHeader = True
    numberOfLinesInPredictedValuesFile = 0
    for line in predictedValuesFile:
        if fileHasHeader == True:
            fileHasHeader = False
            continue
        line=line.rstrip('\n')
        splitLine = line.split(',')
        timeStamp = float(splitLine[1])
        predictedProb = {}
        try:#TODO: remove this and then run the code to identify errors.
            predictedProb[-2] = float(splitLine[2])
            predictedProb[-1] = float(splitLine[3])
            predictedProb[0] = float(splitLine[4])
            predictedProb[1] = float(splitLine[5])
            predictedProb[2] = float(splitLine[6])
        except:
            predictedProb = {-2:0,-1:0,0:0,1:0,2:0}
        pPredictedValuesDict[timeStamp] = predictedProb
        numberOfLinesInPredictedValuesFile += 1
    print("Finished reading the predicted values file")    
    print("The number of elements in the predicted values dictionary is : " + str(len(pPredictedValuesDict)))
    if (numberOfLinesInPredictedValuesFile != len(pPredictedValuesDict)):
        print("Number of duplicate timestamps rejected = " + str(numberOfLinesInPredictedValuesFile - len(pPredictedValuesDict)))
        os._exit(-1)
    sys.stdout.flush()

def checkIfPreviousDecisionToEnterOrExitTradeWasSuccessful(pCurrentDataRow,pTTQAtTimeOfPreviousDataRow,pAskP0AtTimeOfPreviousDataRow, pBidP0AtTimeOfPreviousDataRow, pEnterTradeShort, pEnterTradeLong, pTradeStats,pReasonForTrade):
    global gTickSize
    spreadAtTimeOfPreviousDataRow = pAskP0AtTimeOfPreviousDataRow - pBidP0AtTimeOfPreviousDataRow
    
    if(pEnterTradeShort == 0 and pEnterTradeLong == 0):
        return
    
    #close buy
    if(pEnterTradeShort == -1): # Need to buy we come here only if currentPosition is greater than 0 so no need to check again.
        #standing
        if spreadAtTimeOfPreviousDataRow > gTickSize:        
            currentLTP = float(pCurrentDataRow[colNumberOfData.LTP])
            currentTTQ = float(pCurrentDataRow[colNumberOfData.TTQ])    
            if(currentTTQ <= pTTQAtTimeOfPreviousDataRow):
                pReasonForTrade['VolumeDidNotIncreaseDuringBuyAttemptShort'] += 1
            elif(currentLTP != pBidP0AtTimeOfPreviousDataRow): 
                pReasonForTrade['LTPDoesNotEqualBidP0Short'] += 1
            else:    
                pReasonForTrade['AssumingBuyTradeHappenedShort'] += 1
                pTradeStats['totalBuyValueShort'] += 1 * (pBidP0AtTimeOfPreviousDataRow + gTickSize)
                pTradeStats['currentPositionShort'] -= 1
        #hitting
        else:
            pReasonForTrade['AssumingBuyTradeHappenedShort'] += 1
            pTradeStats['totalBuyValueShort'] += 1 * (pAskP0AtTimeOfPreviousDataRow)
            pTradeStats['currentPositionShort'] -= 1
    #open sell
    elif(pEnterTradeShort == 1 and pTradeStats['currentPositionShort'] == 0): # Need to sell
        #standing
        if spreadAtTimeOfPreviousDataRow > gTickSize:        
            currentLTP = float(pCurrentDataRow[colNumberOfData.LTP])
            currentTTQ = float(pCurrentDataRow[colNumberOfData.TTQ])
            if(currentTTQ <= pTTQAtTimeOfPreviousDataRow):
                pReasonForTrade['VolumeDidNotIncreaseDuringSellAttemptShort'] += 1
            elif(currentLTP != pAskP0AtTimeOfPreviousDataRow):
                pReasonForTrade['LTPDoesNotEqualAskP0Short'] += 1
            else:
                pReasonForTrade['AssumingSellTradeHappenedShort'] += 1
                pTradeStats['totalSellValueShort'] += 1 * (pAskP0AtTimeOfPreviousDataRow - gTickSize)
                pTradeStats['currentPositionShort'] += 1
        #hitting
        else:
            pReasonForTrade['AssumingSellTradeHappenedShort'] += 1
            pTradeStats['totalSellValueShort'] += 1 * (pBidP0AtTimeOfPreviousDataRow)
            pTradeStats['currentPositionShort'] += 1
            
        
    #close sell
    if(pEnterTradeLong == -1): # Need to sell we come here only if currentPosition is greater than 0 so no need to check again.
        #standing
        if spreadAtTimeOfPreviousDataRow > gTickSize:        
            currentLTP = float(pCurrentDataRow[colNumberOfData.LTP])
            currentTTQ = float(pCurrentDataRow[colNumberOfData.TTQ])    
            if(currentTTQ <= pTTQAtTimeOfPreviousDataRow):
                pReasonForTrade['VolumeDidNotIncreaseDuringSellAttemptLong'] += 1
            elif(currentLTP != pAskP0AtTimeOfPreviousDataRow): 
                pReasonForTrade['LTPDoesNotEqualAskP0Long'] += 1
            else:    
                pReasonForTrade['AssumingSellTradeHappenedLong'] += 1
                pTradeStats['totalSellValueLong'] += 1 * (pAskP0AtTimeOfPreviousDataRow - gTickSize)
                pTradeStats['currentPositionLong'] -= 1
        #hitting
        else:
            pReasonForTrade['AssumingSellTradeHappenedLong'] += 1
            pTradeStats['totalSellValueLong'] += 1 * (pBidP0AtTimeOfPreviousDataRow)
            pTradeStats['currentPositionLong'] -= 1
    #open buy
    elif(pEnterTradeLong == 1 and pTradeStats['currentPositionLong'] == 0): # Need to buy
        #standing
        if spreadAtTimeOfPreviousDataRow > gTickSize:        
            currentLTP = float(pCurrentDataRow[colNumberOfData.LTP])
            currentTTQ = float(pCurrentDataRow[colNumberOfData.TTQ])
            if(currentTTQ <= pTTQAtTimeOfPreviousDataRow):
                pReasonForTrade['VolumeDidNotIncreaseDuringBuyAttemptLong'] += 1
            elif(currentLTP != pBidP0AtTimeOfPreviousDataRow):
                pReasonForTrade['LTPDoesNotEqualBidP0Long'] += 1
            else:
                pReasonForTrade['AssumingBuyTradeHappenedLong'] += 1
                pTradeStats['totalBuyValueLong'] += 1 * (pBidP0AtTimeOfPreviousDataRow + gTickSize)
                pTradeStats['currentPositionLong'] += 1
        #hitting
        else:
            pReasonForTrade['AssumingBuyTradeHappenedLong'] += 1
            pTradeStats['totalBuyValueLong'] += 1 * (pAskP0AtTimeOfPreviousDataRow)
            pTradeStats['currentPositionLong'] += 1

def main():
   dataFile.getDataIntoMatrix(args.d)
   predictedValuesDict = dict()
   getPredictedValuesIntoDict(predictedValuesDict)
   enterTradeShort = 0
   enterTradeLong = 0
   ttqAtTimeOfPreviousDataRow = 0
   askP0AtTimeOfPreviousDataRow = 0
   bidP0AtTimeOfPreviousDataRow = 0
   tradeStats = dict()
   tradeStats['totalSellValueShort'] = 0
   tradeStats['totalBuyValueShort'] = 0
   tradeStats['currentPositionShort'] = 0
   tradeStats['totalSellValueLong'] = 0
   tradeStats['totalBuyValueLong'] = 0
   tradeStats['currentPositionLong'] = 0
   noPredictionForThisRow = 0
   currentPredictedValueShort = 0
   currentPredictedValueLong = 0
   entryCL = float(args.entryCL)
   exitCL = float(args.exitCL)
 #  entryCLCutoff = float(args.entryCLCutoff)
 #  exitCLCutoff = float(args.exitCLCutoff)
   numberOfTimesAskedToEnterTradeShort = 0
   numberOfTimesAskedToEnterTradeLong = 0
   numberOfTimesAskedToExitTradeShort = 0
   numberOfTimesAskedToExitTradeLong = 0
   reasonForTrade = dict()
   reasonForTrade['LTPDoesNotEqualBidP0Short'] = 0
   reasonForTrade['LTPDoesNotEqualAskP0Short'] = 0
   reasonForTrade['VolumeDidNotIncreaseDuringBuyAttemptShort'] = 0
   reasonForTrade['VolumeDidNotIncreaseDuringBuyAttemptLong'] = 0
   reasonForTrade['AssumingBuyTradeHappenedShort'] = 0
   reasonForTrade['AssumingBuyTradeHappenedLong'] = 0
   reasonForTrade['LTPDoesNotEqualAskP0Long'] = 0
   reasonForTrade['LTPDoesNotEqualBidP0Long'] = 0
   reasonForTrade['VolumeDidNotIncreaseDuringSellAttemptShort'] = 0
   reasonForTrade['VolumeDidNotIncreaseDuringSellAttemptLong'] = 0
   reasonForTrade['AssumingSellTradeHappenedShort'] = 0
   reasonForTrade['AssumingSellTradeHappenedLong'] = 0


   print("Processing the data file for trades :")

   for currentDataRow in dataFile.matrix:
       checkIfPreviousDecisionToEnterOrExitTradeWasSuccessful(currentDataRow,ttqAtTimeOfPreviousDataRow,askP0AtTimeOfPreviousDataRow,bidP0AtTimeOfPreviousDataRow,enterTradeShort,enterTradeLong,tradeStats,reasonForTrade)
       currentTimeStamp = common.convertTimeStampFromStringToFloat(currentDataRow[colNumberOfData.TimeStamp])

       try:
           currentPredictedValueShort = (float(predictedValuesDict[currentTimeStamp][-2]) + float(predictedValuesDict[currentTimeStamp][-1])) \
                                        - (float(predictedValuesDict[currentTimeStamp][2]) + float(predictedValuesDict[currentTimeStamp][1]))
           currentPredictedValueLong = (float(predictedValuesDict[currentTimeStamp][2]) + float(predictedValuesDict[currentTimeStamp][1])) \
                                        - (float(predictedValuesDict[currentTimeStamp][-2]) + float(predictedValuesDict[currentTimeStamp][-1]))
       except:
           noPredictionForThisRow += 1

       #short decisions
       if(currentPredictedValueShort > entryCL):
           enterTradeShort = 1
           numberOfTimesAskedToEnterTradeShort += 1
       elif(currentPredictedValueShort < exitCL and tradeStats['currentPositionShort'] > 0):
           numberOfTimesAskedToExitTradeShort += 1
           enterTradeShort = -1  # Implies to exit the trade
       else:
           enterTradeShort = 0  # Implies make no change
           
#       if enterTradeShort == 1:
#           if currentPredictedValue <= entryCLCutoff:
#               enterTrade = 0
#       if enterTrade == -1:
#           if currentPredictedValue >= exitCLCutoff:
#               enterTrade = 0
               
       #long decisions
       if(currentPredictedValueLong > entryCL):
           enterTradeLong = 1
           numberOfTimesAskedToEnterTradeLong += 1
       elif(currentPredictedValueLong < exitCL and tradeStats['currentPositionLong'] > 0):
           numberOfTimesAskedToExitTradeLong += 1
           enterTradeLong = -1  # Implies to exit the trade
       else:
           enterTradeLong = 0  # Implies make no change
       
       ttqAtTimeOfPreviousDataRow = float(currentDataRow[colNumberOfData.TTQ]) 
       askP0AtTimeOfPreviousDataRow = float(currentDataRow[colNumberOfData.AskP0])
       bidP0AtTimeOfPreviousDataRow = float(currentDataRow[colNumberOfData.BidP0])
   dirName = args.d.replace('/ro/','/rs/')
   fileName = dirName+"/t/"+experimentName+args.a+args.entryCL+"-"+args.exitCL+".trade" 
   outputFile = open(fileName,"w")
   
   #changed file write to modify it to Short Long version
   print("Starting to write: "+fileName)
   print("The net results for Short are: " + str(tradeStats['totalSellValueShort'] - tradeStats['totalBuyValueShort']), file = outputFile)
   print("The net results for Long are: " + str(tradeStats['totalSellValueLong'] - tradeStats['totalBuyValueLong']), file = outputFile)
   print("Number of rows for which there is no prediction: " + str(noPredictionForThisRow), file = outputFile)    
   print("Number of times asked to enter trade Short: " + str(numberOfTimesAskedToEnterTradeShort), file = outputFile)    
   print("Number of times asked to enter trade Long: " + str(numberOfTimesAskedToEnterTradeLong), file = outputFile)    
   print("Number of times asked to exit trade Short: " + str(numberOfTimesAskedToExitTradeShort), file = outputFile)
   print("Number of times asked to exit trade Long: " + str(numberOfTimesAskedToExitTradeLong), file = outputFile)
   print("Assumed close buy trade did not happen since volume did not increase: " + str(reasonForTrade['VolumeDidNotIncreaseDuringBuyAttemptShort']), file = outputFile)
   print("Assumed open buy trade did not happen since volume did not increase: " + str(reasonForTrade['VolumeDidNotIncreaseDuringBuyAttemptLong']), file = outputFile)
   print("Assumed close buy trade did not happen since bidP0 not same as LTP: " + str(reasonForTrade['LTPDoesNotEqualBidP0Short']), file = outputFile)
   print("Assumed open buy trade did not happen since bidP0 not same as LTP: " + str(reasonForTrade['LTPDoesNotEqualBidP0Long']), file = outputFile)
   print("Assumed close buy trade happened: " + str(reasonForTrade['AssumingBuyTradeHappenedShort']), file = outputFile)
   print("Assumed open buy trade happened: " + str(reasonForTrade['AssumingBuyTradeHappenedLong']), file = outputFile)
   print("Assumed open sell trade did not happen since volume did not increase: " + str(reasonForTrade['VolumeDidNotIncreaseDuringSellAttemptShort']), file = outputFile)
   print("Assumed close sell trade did not happen since volume did not increase: " + str(reasonForTrade['VolumeDidNotIncreaseDuringSellAttemptLong']), file = outputFile)
   print("Assumed open sell trade did not happen since bidP0 not same as LTP: " + str(reasonForTrade['LTPDoesNotEqualAskP0Short']), file = outputFile)
   print("Assumed close sell trade did not happen since bidP0 not same as LTP: " + str(reasonForTrade['LTPDoesNotEqualAskP0Long']), file = outputFile)
   print("Assumed open sell trade happened: " + str(reasonForTrade['AssumingSellTradeHappenedShort']), file = outputFile)
   print("Assumed close sell trade happened: " + str(reasonForTrade['AssumingSellTradeHappenedLong']), file = outputFile)
   print("The total open sell value is: " + str(tradeStats['totalSellValueShort']), file = outputFile)
   print("The total close sell value is: " + str(tradeStats['totalSellValueLong']), file = outputFile)
   print("The total close buy value is: " + str(tradeStats['totalBuyValueShort']), file = outputFile)
   print("The total open buy value is: " + str(tradeStats['totalBuyValueLong']), file = outputFile)

   try:
       averageOpenSellPrice = tradeStats['totalSellValueShort']/reasonForTrade['AssumingSellTradeHappenedShort']
       averageCloseBuyPrice = tradeStats['totalBuyValueShort']/reasonForTrade['AssumingBuyTradeHappenedShort']
   except:
       averageOpenSellPrice = 0 
       averageCloseBuyPrice = 0
   try:
       averageCloseSellPrice = tradeStats['totalSellValueLong']/reasonForTrade['AssumingSellTradeHappenedLong']
       averageOpenBuyPrice = tradeStats['totalBuyValueLong']/reasonForTrade['AssumingBuyTradeHappenedLong']
   except:
       averageCloseSellPrice = 0
       averageOpenBuyPrice = 0 

   print("Average open sell price per unit is: " + str(averageOpenSellPrice), file = outputFile)
   print("Average close sell price per unit is: " + str(averageCloseSellPrice), file = outputFile)
   print("Average open buy price per unit is: " + str(averageOpenBuyPrice), file = outputFile)
   print("Average close buy price per unit is: " + str(averageCloseBuyPrice), file = outputFile)
   print("The current position Short: " + str(tradeStats['currentPositionShort']), file = outputFile)
   print("The current position Long: " + str(tradeStats['currentPositionLong']), file = outputFile)
   print("Profit or loss per Qty traded Short is: " + str(averageOpenSellPrice - averageCloseBuyPrice), file = outputFile)
   print("Profit or loss per Qty traded Long is: " + str(averageCloseSellPrice - averageOpenBuyPrice), file = outputFile)
   pLPerLotShort=(averageOpenSellPrice - averageCloseBuyPrice)* 1000
   pLPerLotLong=(averageCloseSellPrice - averageOpenBuyPrice)* 1000
   print("1 lot has 1000 qty's so P/L Short per lot is: " + str(pLPerLotShort), file = outputFile)
   print("1 lot has 1000 qty's so P/L Long per lot is: " + str(pLPerLotLong), file = outputFile)
   print("P/L for Short trading 10 lots is: " + str(pLPerLotShort * 10), file = outputFile)
   print("P/L for Long trading 10 lots is: " + str(pLPerLotLong * 10), file = outputFile)


if __name__ == "__main__":
    print ("\nRunning the simulated trading program")
    main()

