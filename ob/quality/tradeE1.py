#!/usr/bin/python
from __future__ import division
from __future__ import print_function
import os, sys, argparse
from configobj import ConfigObj

parser = argparse.ArgumentParser(description='This program will do trades to measure the quality of the experiment. An e.g. command line is tarde.py -d ob/data/20140207/ -e ob/e/1 -a logitr')
parser.add_argument('-td', required=True,help='Directory of the training data file')
parser.add_argument('-pd', required=True,help='Directory of the prediction data file')
parser.add_argument('-dt',required=False,help="Number of days it was trained")  
parser.add_argument('-targetClass',required=False,help="For which model was used ; binomial(target takes only true and false) / multinomial (target values takes more than 2 values)")
parser.add_argument('-e', required=True,help='Directory of the experiment')
parser.add_argument('-a', required=True,help='Algorithm name')
parser.add_argument('-entryCL', required=True,help='Percentage of the confidence level used to enter the trades')
parser.add_argument('-exitCL', required=True,help='Percentage of the confidence level used to exit the trades')
parser.add_argument("-skipT",required=False,help="Skip creating trade files if already generated")
parser.add_argument('-tickSize',required=True,help="Nse Currency = 25000 , Future Options = 5")
# "sequence of commands" is not required since this does not generate sub commands.
args = parser.parse_args()

if args.skipT == None:
    args.skipT = "no"
if args.dt == None:
    args.dt = "1"
if args.targetClass == None:
    args.targetClass = "binomial"
        
sys.path.append("./src/")
sys.path.append("./ob/generators/")
import dataFile, colNumberOfData, common

absPathOfExperimentName = os.path.abspath(args.e)
pathAfterE = absPathOfExperimentName[absPathOfExperimentName.index("/e/")+3:]
if "/" in pathAfterE:
    mainExperimentName = pathAfterE[:pathAfterE.index("/")]
else:
    mainExperimentName = pathAfterE
    
experimentName = os.path.basename(absPathOfExperimentName)
initialFileName = args.a + '-td.' + os.path.basename(os.path.abspath(args.td)) + \
               '-dt.' + args.dt + '-targetClass.' + args.targetClass + '-f.' + experimentName + \
               '-l.'+args.entryCL+"-"+args.exitCL + "-te1" 

def getPredictedValuesIntoDict(pPredictedValuesDict):
    # The following will take care if args.e = "ob/e1/" or args.e = "ob/e1"
    config = ConfigObj(args.e+"/design.ini")
    target = config["target"]
    dirName = args.pd.replace('/ro/','/wf/')
    predictedValuesFileName = dirName+"/p/"+mainExperimentName+"/"+args.a + target.keys()[0] + '-td.' + os.path.basename(os.path.abspath(args.td)) + \
                                 '-dt.' + args.dt + '-targetClass.' + args.targetClass + '-f.' + experimentName + ".predictions"
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
        splitLine = line.split(',',2)
        timeStamp = float(splitLine[1])
        try:#TODO: remove this and then run the code to identify errors.
            predictedProb = float(splitLine[2])
        except:
            predictedProb = 0
        pPredictedValuesDict[timeStamp] = predictedProb
        numberOfLinesInPredictedValuesFile += 1
    print("Finished reading the predicted values file")    
    print("The number of elements in the predicted values dictionary is : " + str(len(pPredictedValuesDict)))
    if (numberOfLinesInPredictedValuesFile != len(pPredictedValuesDict)):
        print("Number of duplicate timestamps rejected = " + str(numberOfLinesInPredictedValuesFile - len(pPredictedValuesDict)))
        os._exit(-1)
    sys.stdout.flush()

def checkIfPreviousDecisionToEnterOrExitTradeWasSuccessful(pCurrentDataRow,pTTQAtTimeOfPreviousDataRow,pAskP0AtTimeOfPreviousDataRow, pBidP0AtTimeOfPreviousDataRow, pEnterTrade, pTradeStats,pReasonForTrade):
    if(pEnterTrade == 0):
        return
    elif(pEnterTrade == -1): # Need to sell we come here only if currentPosition is greater than 0 so no need to check again.
        currentLTP = float(pCurrentDataRow[colNumberOfData.LTP])
        currentTTQ = float(pCurrentDataRow[colNumberOfData.TTQ])    
        if(currentTTQ <= pTTQAtTimeOfPreviousDataRow):
            pReasonForTrade['VolumeDidNotIncreaseDuringSellAttempt'] += 1
        elif(currentLTP != pAskP0AtTimeOfPreviousDataRow): 
            pReasonForTrade['LTPDoesNotEqualAskP0'] += 1
        else:    
            pReasonForTrade['AssumingSellTradeHappened'] += 1
            pTradeStats['totalSellValue'] += 1 * pAskP0AtTimeOfPreviousDataRow
            pTradeStats['currentPosition'] -= 1
    elif(pEnterTrade == 1 and pTradeStats['currentPosition'] == 0): # Need to buy
        currentLTP = float(pCurrentDataRow[colNumberOfData.LTP])
        currentTTQ = float(pCurrentDataRow[colNumberOfData.TTQ])             
        # Let me find out if i was able to buy
        if(currentTTQ <= pTTQAtTimeOfPreviousDataRow):
            pReasonForTrade['VolumeDidNotIncreaseDuringBuyAttempt'] += 1
        elif(currentLTP != pBidP0AtTimeOfPreviousDataRow): 
            pReasonForTrade['LTPDoesNotEqualBidP0'] += 1
        else:    
            pReasonForTrade['AssumingBuyTradeHappened'] += 1
            pTradeStats['totalBuyValue'] += 1 * pBidP0AtTimeOfPreviousDataRow
            pTradeStats['currentPosition'] += 1

def main():
   dataFile.getDataIntoMatrix(args.pd)
   predictedValuesDict = dict()
   getPredictedValuesIntoDict(predictedValuesDict)
   enterTrade = 0
   ttqAtTimeOfPreviousDataRow = 0
   askP0AtTimeOfPreviousDataRow = 0
   bidP0AtTimeOfPreviousDataRow = 0
   tradeStats = dict()
   tradeStats['totalSellValue'] = 0
   tradeStats['totalBuyValue'] = 0
   tradeStats['currentPosition'] = 0
   noPredictionForThisRow = 0
   currentPredictedValue = 0
   entryCL = float(args.entryCL)/100
   exitCL = float(args.exitCL)/100
   numberOfTimesAskedToEnterTrade = 0
   numberOfTimesAskedToExitTrade = 0
   reasonForTrade = dict()
   reasonForTrade['LTPDoesNotEqualBidP0'] = 0
   reasonForTrade['VolumeDidNotIncreaseDuringBuyAttempt'] = 0
   reasonForTrade['AssumingBuyTradeHappened'] = 0
   reasonForTrade['LTPDoesNotEqualAskP0'] = 0
   reasonForTrade['VolumeDidNotIncreaseDuringSellAttempt'] = 0
   reasonForTrade['AssumingSellTradeHappened'] = 0


   print("Processing the data file for trades :")

   for currentDataRow in dataFile.matrix:
       checkIfPreviousDecisionToEnterOrExitTradeWasSuccessful(currentDataRow,ttqAtTimeOfPreviousDataRow,askP0AtTimeOfPreviousDataRow,bidP0AtTimeOfPreviousDataRow,enterTrade,tradeStats,reasonForTrade)
       currentTimeStamp = common.convertTimeStampFromStringToFloat(currentDataRow[colNumberOfData.TimeStamp])

       try:
           currentPredictedValue = float(predictedValuesDict[currentTimeStamp])
       except:
           noPredictionForThisRow += 1

       if(currentPredictedValue > entryCL):
           enterTrade = 1
           numberOfTimesAskedToEnterTrade += 1
       elif(currentPredictedValue < exitCL and tradeStats['currentPosition'] > 0):
           numberOfTimesAskedToExitTrade += 1
           enterTrade = -1  # Implies to exit the trade
       else:
           enterTrade = 0  # Implies make no change

       ttqAtTimeOfPreviousDataRow = float(currentDataRow[colNumberOfData.TTQ]) 
       askP0AtTimeOfPreviousDataRow = float(currentDataRow[colNumberOfData.AskP0])
       bidP0AtTimeOfPreviousDataRow = float(currentDataRow[colNumberOfData.BidP0])
    
   dirName = args.pd.replace('/ro/','/rs/')    
   tradeResultMainDirName = dirName+"/r/"
   if not os.path.exists(tradeResultMainDirName):
        os.mkdir(tradeResultMainDirName)
   tradeResultSubDirectoryName =  tradeResultMainDirName + mainExperimentName+"/"
   if not os.path.exists(tradeResultSubDirectoryName):
        os.mkdir(tradeResultSubDirectoryName)
   fileName = tradeResultSubDirectoryName+experimentName+initialFileName+".result" 
   outputFile = open(fileName,"w")

   print("Starting to write: "+fileName)
   print("The net results are: " + str(tradeStats['totalSellValue'] - tradeStats['totalBuyValue']), file = outputFile)    
   print("Number of rows for which there is no prediction: " + str(noPredictionForThisRow), file = outputFile)    
   print("Number of times asked to enter trade: " + str(numberOfTimesAskedToEnterTrade), file = outputFile)    
   print("Number of times asked to exit trade: " + str(numberOfTimesAskedToExitTrade), file = outputFile)    
   print("Assumed buy trade did not happen since volume did not increase: " + str(reasonForTrade['VolumeDidNotIncreaseDuringBuyAttempt']), file = outputFile)
   print("Assumed buy trade did not happen since bidP0 not same as LTP: " + str(reasonForTrade['LTPDoesNotEqualBidP0']), file = outputFile)
   print("Assumed buy trade happened: " + str(reasonForTrade['AssumingBuyTradeHappened']), file = outputFile)
   print("Assumed sell trade did not happen since volume did not increase: " + str(reasonForTrade['VolumeDidNotIncreaseDuringSellAttempt']), file = outputFile)
   print("Assumed sell trade did not happen since bidP0 not same as LTP: " + str(reasonForTrade['LTPDoesNotEqualAskP0']), file = outputFile)
   print("Assumed sell trade happened: " + str(reasonForTrade['AssumingSellTradeHappened']), file = outputFile)
   print("The total sell value is: " + str(tradeStats['totalSellValue']), file = outputFile)
   print("The total buy value is: " + str(tradeStats['totalBuyValue']), file = outputFile)
   try:
       averageSellPrice = tradeStats['totalSellValue']/reasonForTrade['AssumingSellTradeHappened']
       averageBuyPrice = tradeStats['totalBuyValue']/reasonForTrade['AssumingBuyTradeHappened']
   except:
       averageSellPrice = 0 
       averageBuyPrice = 0
   print("Average sell price per unit is: " + str(averageSellPrice), file = outputFile)
   print("Average buy price per unit is: " + str(averageBuyPrice), file = outputFile)
   print("The current position: " + str(tradeStats['currentPosition']), file = outputFile)
   print("Profit or loss per Qty traded is: " + str(averageSellPrice - averageBuyPrice), file = outputFile)
   pLPerLot=(averageSellPrice - averageBuyPrice)* 1000
   print("1 lot has 1000 qty's so P/L per lot is: " + str(pLPerLot), file = outputFile)
   print("P/L for trading 10 lots is: " + str(pLPerLot * 10), file = outputFile)

if __name__ == "__main__":
   dirName = args.pd.replace('/ro/','/rs/')
   fileName = dirName + "/r/" + mainExperimentName + "/" + experimentName+initialFileName+".result"
   if os.path.isfile(fileName) and args.skipT == "yes":
       print("Trade results file " + fileName + "Already exist. Not regenerating it. If you want to rerun it by making -skipT = no ")
   else: 
       print ("\nRunning the simulated trading program")
       main()



