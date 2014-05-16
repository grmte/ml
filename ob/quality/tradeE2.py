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
args = parser.parse_args()

sys.path.append("/Volumes/SsdData/ml/src/")
sys.path.append("/Volumes/SsdData/ml/ob/generators/")
import dataFile, colNumberOfData, common

if args.skipT == None:
    args.skipT = "no"
if args.dt == None:
    args.dt = "1"
if args.targetClass == None:
    args.targetClass = "binomial"
        
absPathOfExperimentName = os.path.abspath(args.e)
pathAfterE = absPathOfExperimentName[absPathOfExperimentName.index("/e/")+3:]
if "/" in pathAfterE:
    mainExperimentName = pathAfterE[:pathAfterE.index("/")]
else:
    mainExperimentName = pathAfterE
    
experimentName = os.path.basename(absPathOfExperimentName)
initialFileName = args.a + '-td.' + os.path.basename(os.path.abspath(args.td)) + \
               '-dt.' + args.dt + '-targetClass.' + args.targetClass + '-f.' + experimentName + \
               '-l.'+args.entryCL+"-"+args.exitCL + "-te2"    

def getPredictedValuesIntoDict(pPredictedValuesDict):
    # The following will take care if args.e = "ob/e1/" or args.e = "ob/e1"
    config = ConfigObj(args.e+"/design.ini")
    target = config["target"]
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

def checkIfPreviousDecisionToEnterOrExitTradeWasSuccessful(pCurrentDataRow,pVarsAtTimeOfTradeDecision, pEnterTradeRecommendation, pTradeStats,pReasonForTrade):
    if(pEnterTradeRecommendation == 0):
        return
    elif(pEnterTradeRecommendation == -1): # Need to sell we come here only if currentPosition is greater than 0 so no need to check again.
        currentLTP = float(pCurrentDataRow[colNumberOfData.LTP])
        currentTTQ = float(pCurrentDataRow[colNumberOfData.TTQ])    
        if(pVarsAtTimeOfTradeDecision['qtyTradedAtAskP0'] <= (.8 * pVarsAtTimeOfTradeDecision['askQ0']) ):
            pReasonForTrade['VolumeDidNotIncreaseSufficientlyDuringSellAttempt'] += 1
        elif(currentLTP != pVarsAtTimeOfTradeDecision['askP0']): 
            pReasonForTrade['LTPDoesNotEqualAskP0'] += 1
        else:    # When we reach here we are assuming that a fill happened.
            pReasonForTrade['AssumingSellTradeHappened'] += 1
            pTradeStats['totalSellValue'] += 1 * pVarsAtTimeOfTradeDecision['askP0']
            pTradeStats['currentPosition'] -= 1
    elif(pEnterTradeRecommendation == 1 and pTradeStats['currentPosition'] == 0): # Need to buy   # 1st and 2nd condition
        currentLTP = float(pCurrentDataRow[colNumberOfData.LTP])
        currentTTQ = float(pCurrentDataRow[colNumberOfData.TTQ])             
        # Let me find out if i was able to buy
        if(pVarsAtTimeOfTradeDecision['qtyTradedAtBidP0'] <= (.8 * pVarsAtTimeOfTradeDecision['bidQ0']) ):     # 3rd condition 
            pReasonForTrade['VolumeDidNotIncreaseSufficientlyDuringBuyAttempt'] += 1
        elif(currentLTP != pVarsAtTimeOfTradeDecision['bidP0']): # 4th condition
            pReasonForTrade['LTPDoesNotEqualBidP0'] += 1
        else:    # When we reach here we are assuming that a fill happened.
            pReasonForTrade['AssumingBuyTradeHappened'] += 1
            pTradeStats['totalBuyValue'] += 1 * pVarsAtTimeOfTradeDecision['bidP0']
            pTradeStats['currentPosition'] += 1


def updateVarsAtTimeOfTradeDecision(currentDataRow,enterTrade):
    localVarsAtTimeOfTradeDecision = dict()
    localVarsAtTimeOfTradeDecision['ttq'] = float(currentDataRow[colNumberOfData.TTQ]) 
    localVarsAtTimeOfTradeDecision['askP0'] = float(currentDataRow[colNumberOfData.AskP0])
    localVarsAtTimeOfTradeDecision['bidP0'] = float(currentDataRow[colNumberOfData.BidP0])
    localVarsAtTimeOfTradeDecision['askQ0'] = float(currentDataRow[colNumberOfData.AskQ0])
    localVarsAtTimeOfTradeDecision['bidQ0'] = float(currentDataRow[colNumberOfData.BidQ0])
    localVarsAtTimeOfTradeDecision['decision'] = enterTrade
    localVarsAtTimeOfTradeDecision['qtyTradedAtBidP0'] = 0
    localVarsAtTimeOfTradeDecision['qtyTradedAtAskP0'] = 0
    return localVarsAtTimeOfTradeDecision

def main():
    
   dirName = args.pd.replace('/ro/','/rs/')  
   tradeResultMainDirName = dirName+"/r/"
   if not os.path.exists(tradeResultMainDirName):
        os.mkdir(tradeResultMainDirName)
   tradeResultSubDirectoryName =  tradeResultMainDirName + mainExperimentName+"/"
   if not os.path.exists(tradeResultSubDirectoryName):
        os.mkdir(tradeResultSubDirectoryName)
   outputFileName = tradeResultSubDirectoryName+experimentName+initialFileName+".result" 
   
   #if os.path.isfile(outputFileName):
   #    print("The results file already exisits. Delete it to run the program again" + outputFileName)
   #    return 1
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
   entryCL = float(args.entryCL)
   exitCL = float(args.exitCL)
   numberOfTimesAskedToEnterTrade = 0
   numberOfTimesAskedToExitTrade = 0
   reasonForTrade = dict()
   reasonForTrade['LTPDoesNotEqualBidP0'] = 0
   reasonForTrade['VolumeDidNotIncreaseSufficientlyDuringBuyAttempt'] = 0
   reasonForTrade['AssumingBuyTradeHappened'] = 0
   reasonForTrade['LTPDoesNotEqualAskP0'] = 0
   reasonForTrade['VolumeDidNotIncreaseSufficientlyDuringSellAttempt'] = 0
   reasonForTrade['AssumingSellTradeHappened'] = 0
   varsAtTimeOfTradeDecision = dict()
   varsAtTimeOfTradeDecision['decision'] = 0
   varsAtTimeOfTradeDecision['bidP0'] = 0
   varsAtTimeOfTradeDecision['qtyTradedAtBidP0'] = 0
   varsAtTimeOfTradeDecision['ttq'] = 0
   varsAtTimeOfTradeDecision['askP0'] = 0
   varsAtTimeOfTradeDecision['qtyTradedAtAskP0'] = 0

   print("Processing the data file for trades :")

   for currentDataRow in dataFile.matrix: #currentDataRow has the new tick
       if(enterTrade == varsAtTimeOfTradeDecision['decision'] and enterTrade == 1 and varsAtTimeOfTradeDecision['bidP0'] >= float(currentDataRow[colNumberOfData.BidP0])):
           print("Position not lost in the queue")
           if(varsAtTimeOfTradeDecision['bidP0'] == float(currentDataRow[colNumberOfData.LTP]) and float(currentDataRow[colNumberOfData.TTQ]) > varsAtTimeOfTradeDecision['ttq']):
               varsAtTimeOfTradeDecision['qtyTradedAtBidP0'] += float(currentDataRow[colNumberOfData.TTQ]) - varsAtTimeOfTradeDecision['ttq']
       elif(enterTrade == varsAtTimeOfTradeDecision['decision'] and enterTrade == -1 and varsAtTimeOfTradeDecision['askP0'] <= float(currentDataRow[colNumberOfData.AskP0])):
           print("Position not lost in the queue")
           if(varsAtTimeOfTradeDecision['askP0'] == float(currentDataRow[colNumberOfData.LTP]) and float(currentDataRow[colNumberOfData.TTQ]) > varsAtTimeOfTradeDecision['ttq']):
               varsAtTimeOfTradeDecision['qtyTradedAtAskP0'] += float(currentDataRow[colNumberOfData.TTQ]) - varsAtTimeOfTradeDecision['ttq']
       else:
           positionLostInQueue = True

       checkIfPreviousDecisionToEnterOrExitTradeWasSuccessful(currentDataRow,varsAtTimeOfTradeDecision,enterTrade,tradeStats,reasonForTrade)
       
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
       
       if(positionLostInQueue == True):
           varsAtTimeOfTradeDecision = updateVarsAtTimeOfTradeDecision(currentDataRow,enterTrade)   # This implies that the position in the queue is lost.

    
   outputFile = open(outputFileName,"w")
   print("Starting to write: "+outputFileName)
   print("The net results are: " + str(tradeStats['totalSellValue'] - tradeStats['totalBuyValue']), file = outputFile)    
   print("Number of rows for which there is no prediction: " + str(noPredictionForThisRow), file = outputFile)    
   print("Number of times asked to enter trade: " + str(numberOfTimesAskedToEnterTrade), file = outputFile)    
   print("Number of times asked to exit trade: " + str(numberOfTimesAskedToExitTrade), file = outputFile)    
   print("Assumed buy trade did not happen since volume did not increase: " + str(reasonForTrade['VolumeDidNotIncreaseSufficientlyDuringBuyAttempt']), file = outputFile)
   print("Assumed buy trade did not happen since bidP0 not same as LTP: " + str(reasonForTrade['LTPDoesNotEqualBidP0']), file = outputFile)
   print("Assumed buy trade happened: " + str(reasonForTrade['AssumingBuyTradeHappened']), file = outputFile)
   print("Assumed sell trade did not happen since volume did not increase: " + str(reasonForTrade['VolumeDidNotIncreaseSufficientlyDuringSellAttempt']), file = outputFile)
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


