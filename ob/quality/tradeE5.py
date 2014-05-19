#!/usr/bin/python
from __future__ import division
from __future__ import print_function
import os, sys, argparse
from configobj import ConfigObj

parser = argparse.ArgumentParser(description='This program will do trades to measure the quality of the experiment.\n\
 An e.g. command line is tradeE5.py -d ob/data/20140207/ -e ob/e/1 -a logitr -entryCL 0.90 -exitCL .55 -orderQty 500', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-td', required=True,help='Directory of the training data file')
parser.add_argument('-pd', required=True,help='Directory of the prediction data file')
parser.add_argument('-dt',required=False,help="Number of days it was trained")  
parser.add_argument('-targetClass',required=False,help="For which model was used ; binomial(target takes only true and false) / multinomial (target values takes more than 2 values)")
parser.add_argument('-e', required=True,help='Directory of the experiment or sub experiment e/10/s/3c/ABC')
parser.add_argument('-a', required=True,help='Algorithm name')
parser.add_argument('-entryCL', required=True,help='Percentage of the confidence level used to enter the trades')
parser.add_argument('-exitCL', required=True,help='Percentage of the confidence level used to exit the trades')
parser.add_argument('-orderQty',required=True,help='Order Quantity with which we trade')
parser.add_argument("-skipT",required=False,help="Skip creating trade files if already generated")
args = parser.parse_args()

sys.path.append("./src/")
sys.path.append("./ob/generators/")
import dataFile, colNumberOfData, common
import attribute

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
gTickSize = 25000
gMaxQty = int(args.orderQty)
initialFileName =  args.a + '-td.' + os.path.basename(os.path.abspath(args.td)) + \
                    '-dt.' + args.dt + '-targetClass.' + args.targetClass + '-f.' + experimentName + \
                    '-l.'+args.entryCL+"-"+args.exitCL + "-te5"    
g_quantity_adjustment_list_for_sell = {}
g_quantity_adjustment_list_for_buy = {}

def getPredictedValuesIntoDict(pPredictedValuesDict):
    # The following will take care if args.e = "ob/e1/" or args.e = "ob/e1"
    dirName = args.pd.replace('/ro/','/wf/')
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

def checkIfPreviousDecisionToEnterOrExitTradeWasSuccessful(pCurrentDataRow,pTTQAtTimeOfPreviousDataRow,pAskP0AtTimeOfPreviousDataRow,pBidP0AtTimeOfPreviousDataRow,pAskQ0AtTimeOfPreviousDataRow , pBidQ0AtTimeOfPreviousDataRow , pEnterTradeShort, pEnterTradeLong, pTradeStats,pReasonForTrade ):
    global gTickSize , gMaxQty , g_quantity_adjustment_list_for_sell , g_quantity_adjustment_list_for_buy
    spreadAtTimeOfPreviousDataRow = pAskP0AtTimeOfPreviousDataRow - pBidP0AtTimeOfPreviousDataRow
    lReasonForTradingOrNotTradingShort = ""
    lReasonForTradingOrNotTradingLong = ""

    if(pEnterTradeShort == 0 and pEnterTradeLong == 0):
        return [ lReasonForTradingOrNotTradingShort , lReasonForTradingOrNotTradingLong , pBidQ0AtTimeOfPreviousDataRow , pAskQ0AtTimeOfPreviousDataRow , 0 , 0 ]

    if pBidP0AtTimeOfPreviousDataRow in g_quantity_adjustment_list_for_sell:
        pBidQ0AtTimeOfPreviousDataRow = max( 0 , pBidQ0AtTimeOfPreviousDataRow - g_quantity_adjustment_list_for_sell[pBidP0AtTimeOfPreviousDataRow])
    else:
        g_quantity_adjustment_list_for_sell = {}

    if pAskP0AtTimeOfPreviousDataRow in g_quantity_adjustment_list_for_buy:
        pAskQ0AtTimeOfPreviousDataRow = max( 0 ,pAskQ0AtTimeOfPreviousDataRow - g_quantity_adjustment_list_for_buy[pAskP0AtTimeOfPreviousDataRow])
    else:
        g_quantity_adjustment_list_for_buy = {}    

    currentLTP = float(pCurrentDataRow[colNumberOfData.LTP])
    currentTTQ = float(pCurrentDataRow[colNumberOfData.TTQ])    

    l_dummy_AskQ0 = pAskQ0AtTimeOfPreviousDataRow
    l_dummy_TTQChange_For_Buy = currentTTQ - pTTQAtTimeOfPreviousDataRow
    #close buy
    if(pEnterTradeShort == -1): # Need to buy we come here only if currentPosition is greater than 0 so no need to check again.
        #standing
        if spreadAtTimeOfPreviousDataRow > gTickSize:        
            if(l_dummy_TTQChange_For_Buy<=0):
                pReasonForTrade['VolumeDidNotIncreaseDuringBuyAttemptShort'] += 1
                lReasonForTradingOrNotTradingShort = '(Spread>Pip)&&(NextTickTTQDidNotIncrease)'
            elif(currentLTP != pBidP0AtTimeOfPreviousDataRow): 
                pReasonForTrade['LTPDoesNotEqualBidP0Short'] += 1
                lReasonForTradingOrNotTradingShort = '(Spread>Pip)&&(LTP!=Bid)'
            else:    
               
                lQtyTraded = min(  pTradeStats['currentPositionShort'] , l_dummy_TTQChange_For_Buy )
                l_dummy_TTQChange_For_Buy -= lQtyTraded
                pTradeStats['totalBuyValueShort'] += lQtyTraded * (pBidP0AtTimeOfPreviousDataRow + gTickSize)
                pTradeStats['currentPositionShort'] -= lQtyTraded
                lReasonForTradingOrNotTradingShort = 'CloseBuy(Standing)'
                pReasonForTrade['AssumingBuyTradeHappenedShort'] += lQtyTraded
        #hitting
        else:

            l_buy_qty = min( pTradeStats['currentPositionShort'], pAskQ0AtTimeOfPreviousDataRow)
            if pAskP0AtTimeOfPreviousDataRow in g_quantity_adjustment_list_for_buy:
                    g_quantity_adjustment_list_for_buy[pAskP0AtTimeOfPreviousDataRow] += l_buy_qty
            else:  
                    g_quantity_adjustment_list_for_buy = {} 
                    g_quantity_adjustment_list_for_buy[pAskP0AtTimeOfPreviousDataRow] = l_buy_qty
            l_dummy_AskQ0 -= l_buy_qty
            pTradeStats['totalBuyValueShort'] += l_buy_qty * (pAskP0AtTimeOfPreviousDataRow)
            pTradeStats['currentPositionShort'] -= l_buy_qty
            pReasonForTrade['AssumingBuyTradeHappenedShort'] += l_buy_qty
            lReasonForTradingOrNotTradingShort = 'CloseBuy(Hitting)'
        
    #open buy
    if(pEnterTradeLong == 1 and ( gMaxQty - pTradeStats['currentPositionLong'] ) > 0): # Need to buy
        #standing
        if spreadAtTimeOfPreviousDataRow > gTickSize:        
            if(l_dummy_TTQChange_For_Buy <= 0 ):
                pReasonForTrade['VolumeDidNotIncreaseDuringBuyAttemptLong'] += 1
                lReasonForTradingOrNotTradingLong = '(Spread>Pip)&&(NextTickTTQDidNotIncrease)'
            elif(currentLTP != pBidP0AtTimeOfPreviousDataRow):
                pReasonForTrade['LTPDoesNotEqualBidP0Long'] += 1
                lReasonForTradingOrNotTradingLong = '(Spread>Pip)&&(LTPDoesNotEqualBidP0Long)'
            else:

                lQtyToBeTraded = ( gMaxQty - pTradeStats['currentPositionLong'] )
                lQtyForWhichWeTrade = min( lQtyToBeTraded , l_dummy_TTQChange_For_Buy)
                l_dummy_TTQChange_For_Buy -= lQtyForWhichWeTrade
                pTradeStats['totalBuyValueLong'] += lQtyForWhichWeTrade * (pBidP0AtTimeOfPreviousDataRow + gTickSize)
                pTradeStats['currentPositionLong'] += lQtyForWhichWeTrade
                lReasonForTradingOrNotTradingLong = 'OpenBuy(Standing)'
                pReasonForTrade['AssumingBuyTradeHappenedLong'] += lQtyForWhichWeTrade
        #hitting
        else:
            if l_dummy_AskQ0 > 0 :

                lQtyToBeTraded = ( gMaxQty - pTradeStats['currentPositionLong'] )
                lQtyForWhichWeTrade = min( lQtyToBeTraded , l_dummy_AskQ0 )
                if pAskP0AtTimeOfPreviousDataRow in g_quantity_adjustment_list_for_buy:
                    g_quantity_adjustment_list_for_buy[pAskP0AtTimeOfPreviousDataRow] += lQtyForWhichWeTrade
                else:
                    g_quantity_adjustment_list_for_buy = {}
                    g_quantity_adjustment_list_for_buy[pAskP0AtTimeOfPreviousDataRow] = lQtyForWhichWeTrade
                pTradeStats['totalBuyValueLong'] += lQtyForWhichWeTrade * (pAskP0AtTimeOfPreviousDataRow)
                pTradeStats['currentPositionLong'] += lQtyForWhichWeTrade
                pReasonForTrade['AssumingBuyTradeHappenedLong'] += lQtyForWhichWeTrade
                l_dummy_AskQ0 -= lQtyForWhichWeTrade
                lReasonForTradingOrNotTradingLong = 'OpenBuy(Hitting)'
            else:
                lReasonForTradingOrNotTradingLong = "DummyAskQ0Exhausted"

    l_dummy_BidQ0 = pBidQ0AtTimeOfPreviousDataRow
    l_dummy_TTQChange_For_Sell = currentTTQ - pTTQAtTimeOfPreviousDataRow
    #close sell
    if(pEnterTradeLong == -1): # Need to sell we come here only if currentPosition is greater than 0 so no need to check again.
        #standing
        if spreadAtTimeOfPreviousDataRow > gTickSize:        
            if(l_dummy_TTQChange_For_Sell <= 0 ):
                pReasonForTrade['VolumeDidNotIncreaseDuringSellAttemptLong'] += 1
                lReasonForTradingOrNotTradingLong = '(Spread>Pip)&&(NextTickTTQDidNotIncrease)'
            elif(currentLTP != pAskP0AtTimeOfPreviousDataRow): 
                pReasonForTrade['LTPDoesNotEqualAskP0Long'] += 1
                lReasonForTradingOrNotTradingLong = '(Spread>Pip)&&(NextTickLTP!=Ask)'
            else:    

                lQtyTraded = min(  pTradeStats['currentPositionLong'] , l_dummy_TTQChange_For_Sell )
                pTradeStats['totalSellValueLong'] += lQtyTraded * (pAskP0AtTimeOfPreviousDataRow - gTickSize)
                pTradeStats['currentPositionLong'] -= lQtyTraded
                l_dummy_TTQChange_For_Sell -= lQtyTraded
                lReasonForTradingOrNotTradingLong = 'CloseSell(Standing)'
                pReasonForTrade['AssumingSellTradeHappenedLong'] += lQtyTraded
        #hitting
        else:

            lQtyTraded = min( pTradeStats['currentPositionLong'] , pBidQ0AtTimeOfPreviousDataRow )
            if pBidP0AtTimeOfPreviousDataRow in g_quantity_adjustment_list_for_sell:
                g_quantity_adjustment_list_for_sell[pBidP0AtTimeOfPreviousDataRow] += lQtyTraded
            else:
                g_quantity_adjustment_list_for_sell = {}
                g_quantity_adjustment_list_for_sell[pBidP0AtTimeOfPreviousDataRow] = lQtyTraded
            pTradeStats['totalSellValueLong'] += lQtyTraded * (pBidP0AtTimeOfPreviousDataRow)
            pTradeStats['currentPositionLong'] -= lQtyTraded
            l_dummy_BidQ0 -= lQtyTraded
            lReasonForTradingOrNotTradingLong = 'CloseSell(Hitting)'
            pReasonForTrade['AssumingSellTradeHappenedLong'] += lQtyTraded
    
    #open sell
    if(pEnterTradeShort == 1 and  ( gMaxQty - pTradeStats['currentPositionShort'] ) > 0 ): # Need to sell
        #standing
        if spreadAtTimeOfPreviousDataRow > gTickSize:        
            if(l_dummy_TTQChange_For_Sell <= 0):
                pReasonForTrade['VolumeDidNotIncreaseDuringSellAttemptShort'] += 1
                lReasonForTradingOrNotTradingShort = '(Spread>Pip)&&(NextTickTTQDidNotIncrease)'
            elif(currentLTP != pAskP0AtTimeOfPreviousDataRow):
                pReasonForTrade['LTPDoesNotEqualAskP0Short'] += 1
                lReasonForTradingOrNotTradingShort = '(Spread>Pip)&&(NextTickLTP!=Ask)'
            else:

                lQtyToBeTraded = ( gMaxQty - pTradeStats['currentPositionShort'] )
                lQtyForWhichWeTrade = min( lQtyToBeTraded , l_dummy_TTQChange_For_Sell)
                pTradeStats['totalSellValueShort'] += lQtyForWhichWeTrade * (pAskP0AtTimeOfPreviousDataRow - gTickSize)
                pTradeStats['currentPositionShort'] += lQtyForWhichWeTrade
                l_dummy_TTQChange_For_Sell -= lQtyForWhichWeTrade
                lReasonForTradingOrNotTradingShort = 'OpenSell(Standing)'
                pReasonForTrade['AssumingSellTradeHappenedShort'] += lQtyForWhichWeTrade
        #hitting
        else:
            if l_dummy_BidQ0 > 0 :

                lQtyToBeTraded = ( gMaxQty - pTradeStats['currentPositionShort'] )
                lQtyForWhichWeTrade = min( lQtyToBeTraded , l_dummy_BidQ0 )
                if pBidP0AtTimeOfPreviousDataRow in g_quantity_adjustment_list_for_sell:
                    g_quantity_adjustment_list_for_sell[pBidP0AtTimeOfPreviousDataRow] += lQtyForWhichWeTrade
                else:
                    g_quantity_adjustment_list_for_sell = {}
                    g_quantity_adjustment_list_for_sell[pBidP0AtTimeOfPreviousDataRow] = lQtyForWhichWeTrade
                pTradeStats['totalSellValueShort'] += lQtyForWhichWeTrade * (pBidP0AtTimeOfPreviousDataRow)
                pTradeStats['currentPositionShort'] += lQtyForWhichWeTrade
                lReasonForTradingOrNotTradingShort = 'OpenSell(Hitting)'
                pReasonForTrade['AssumingSellTradeHappenedShort'] += lQtyForWhichWeTrade
                l_dummy_BidQ0 -= lQtyForWhichWeTrade
            else:
                lReasonForTradingOrNotTradingShort = 'DummyBidQZero'

    return [ lReasonForTradingOrNotTradingShort , lReasonForTradingOrNotTradingLong , l_dummy_BidQ0 , l_dummy_AskQ0 , l_dummy_TTQChange_For_Buy , l_dummy_TTQChange_For_Sell]

def main():
   attribute.initList()
   dataFile.getDataIntoMatrix(args.pd)
   predictedValuesDict = dict()
   getPredictedValuesIntoDict(predictedValuesDict)
   enterTradeShort = 0
   enterTradeLong = 0
   ttqAtTimeOfPreviousDataRow = 0
   askP0AtTimeOfPreviousDataRow = 0
   bidP0AtTimeOfPreviousDataRow = 0
   askQ0AtTimeOfPreviousDataRow = 0
   bidQ0AtTimeOfPreviousDataRow = 0
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
   entryCL = float(args.entryCL)/100
   exitCL = float(args.exitCL)/100
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
   currentIndex = 0
   print("Processing the data file for trades :")
   attribute.initList()
   for currentDataRow in dataFile.matrix:
       
       lReturnList = checkIfPreviousDecisionToEnterOrExitTradeWasSuccessful(currentDataRow,ttqAtTimeOfPreviousDataRow,askP0AtTimeOfPreviousDataRow,bidP0AtTimeOfPreviousDataRow,askQ0AtTimeOfPreviousDataRow , bidQ0AtTimeOfPreviousDataRow , enterTradeShort,enterTradeLong,tradeStats,reasonForTrade )

       lReasonForTradingOrNotTradingShort = lReturnList[0]
       lReasonForTradingOrNotTradingLong = lReturnList[1] 
       lDummyBidQ0 = lReturnList[2]
       lDummyAskQ0 = lReturnList[3]
       lDummyTTQForBuy = lReturnList[4]
       lDummyTTQForSell = lReturnList[5]
       if currentIndex > 0:
           attribute.aList[currentIndex-1][0] = currentTimeStamp
           attribute.aList[currentIndex-1][1] = tradeStats['currentPositionLong']
           attribute.aList[currentIndex-1][2] = tradeStats['currentPositionShort']
           listOfStringsToPrint = [ str(bidQ0AtTimeOfPreviousDataRow) , str(bidP0AtTimeOfPreviousDataRow) , str(askP0AtTimeOfPreviousDataRow) , str(askQ0AtTimeOfPreviousDataRow) , str(ttqAtTimeOfPreviousDataRow) , str(ltpAtTimeOfPreviousDataRow) , str(currentPredictedValueShort) , str(enterTradeShort) ,lReasonForTradingOrNotTradingShort , str(currentPredictedValueLong) , str(enterTradeLong) ,lReasonForTradingOrNotTradingLong , str(reasonForTrade['AssumingBuyTradeHappenedShort']),str(reasonForTrade['AssumingBuyTradeHappenedLong']),str(reasonForTrade['AssumingSellTradeHappenedShort']),str(reasonForTrade['AssumingSellTradeHappenedLong']),str(lDummyBidQ0),str(lDummyAskQ0),str(lDummyTTQForBuy),str(lDummyTTQForSell)]
           attribute.aList[currentIndex-1][3] =  ";".join(listOfStringsToPrint)
       currentTimeStamp = common.convertTimeStampFromStringToFloat(currentDataRow[colNumberOfData.TimeStamp])

       try:
           currentPredictedValueShort = (float(predictedValuesDict[currentTimeStamp][-2]) + float(predictedValuesDict[currentTimeStamp][-1])) 
           currentPredictedValueLong = (float(predictedValuesDict[currentTimeStamp][2]) + float(predictedValuesDict[currentTimeStamp][1])) 
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
       askQ0AtTimeOfPreviousDataRow = float(currentDataRow[colNumberOfData.AskQ0])
       bidQ0AtTimeOfPreviousDataRow = float(currentDataRow[colNumberOfData.BidQ0])
       ltpAtTimeOfPreviousDataRow = float(currentDataRow[colNumberOfData.LTP])
       currentIndex = currentIndex + 1

# Squaring off if some open position there   
   if tradeStats['currentPositionLong'] > 0:
       reasonForTrade['AssumingSellTradeHappenedLong'] += tradeStats['currentPositionLong']
       tradeStats['totalSellValueLong'] += tradeStats['currentPositionLong'] * (bidP0AtTimeOfPreviousDataRow)
       tradeStats['currentPositionLong'] = 0
       lReasonForTradingOrNotTradingLong = 'CloseSell(Hitting)'
   elif tradeStats['currentPositionShort'] > 0:
       reasonForTrade['AssumingBuyTradeHappenedShort'] += tradeStats['currentPositionShort']
       tradeStats['totalBuyValueShort'] += tradeStats['currentPositionShort'] * (askP0AtTimeOfPreviousDataRow)
       tradeStats['currentPositionShort'] = 0
       lReasonForTradingOrNotTradingLong = 'CloseBuy(Hitting)'

   attribute.aList[currentIndex-1][0] = currentTimeStamp
   attribute.aList[currentIndex-1][1] = tradeStats['currentPositionLong']
   attribute.aList[currentIndex-1][2] = tradeStats['currentPositionShort']
   listOfStringsToPrint = [ str(bidQ0AtTimeOfPreviousDataRow) , str(bidP0AtTimeOfPreviousDataRow) , str(askP0AtTimeOfPreviousDataRow) , str(askQ0AtTimeOfPreviousDataRow) , str(ttqAtTimeOfPreviousDataRow) , str(ltpAtTimeOfPreviousDataRow) , str(currentPredictedValueShort) , str(enterTradeShort) , "" , str(currentPredictedValueLong) , str(enterTradeLong) ,"" , str(reasonForTrade['AssumingBuyTradeHappenedShort']),str(reasonForTrade['AssumingBuyTradeHappenedLong']),str(reasonForTrade['AssumingSellTradeHappenedShort']),str(reasonForTrade['AssumingSellTradeHappenedLong']),str(lDummyBidQ0),str(lDummyAskQ0),str(lDummyTTQForBuy),str(lDummyTTQForSell)]
   attribute.aList[currentIndex-1][3] =  ";".join(listOfStringsToPrint) 
   dirName = args.pd.replace('/ro/','/rs/')
   tradeLogMainDirName = dirName+"/t/"
   if not os.path.exists(tradeLogMainDirName):
        os.mkdir(tradeLogMainDirName)
   tradeLogSubDirectoryName =  tradeLogMainDirName + mainExperimentName+"/"
   if not os.path.exists(tradeLogSubDirectoryName):
        os.mkdir(tradeLogSubDirectoryName)
   fileName = tradeLogSubDirectoryName+experimentName+initialFileName+".trade" 
   lHeaderColumnNamesList  = ['TimeStamp','CurrentPositionLong','CurrentPositionShort','BidQ0','BidP0','AskP0','AskQ0','TTQ','LTP','CurPredValueShort','EnterTradeShort','ReasonForTradingOrNotTradingShort','CurPredValueLong','EnterTradeLong','ReasonForTradingOrNotTradingLong','totalBuyTradeShort','totalBuyLong','totalSellShort','totalSellLong','DummyBidQ0','DummyAskQ0','DummyTTQChangeForSell','DummyTTQChangeForBuy']
   attribute.writeToFile(fileName , lHeaderColumnNamesList)

   tradeResultMainDirName = dirName+"/r/"
   if not os.path.exists(tradeResultMainDirName):
        os.mkdir(tradeResultMainDirName)
   tradeResultSubDirectoryName =  tradeResultMainDirName + mainExperimentName+"/"
   if not os.path.exists(tradeResultSubDirectoryName):
        os.mkdir(tradeResultSubDirectoryName)
   fileName = tradeResultSubDirectoryName+experimentName+initialFileName+".result" 
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
   dirName = args.pd.replace('/ro/','/rs/')
   fileName = dirName + "/r/" + mainExperimentName + "/" + experimentName+initialFileName+".result"
   if os.path.isfile(fileName) and args.skipT == "yes":
       print("Trade results file " + fileName + "Already exist. Not regenerating it. If you want to rerun it by making -skipT = no ")
   else: 
       print ("\nRunning the simulated trading program")
       main()



