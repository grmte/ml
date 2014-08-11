#!/usr/bin/python
from __future__ import division
from __future__ import print_function
import os, sys, argparse
from configobj import ConfigObj
import calendar, datetime

parser = argparse.ArgumentParser(description='This program will do trades to measure the quality of the experiment.\n\
 An e.g. command line is tradeE7OnTargetVariable.py -d ob/data/20140207/ -orderQty 500 -startTime 9 -endTime 5', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-orderQty',required=True,help='Order Quantity with which we trade')
parser.add_argument("-skipT",required=False,help="Skip creating trade files if already generated")
parser.add_argument('-d', required=True,help='Directory of the training data file')
parser.add_argument('-startTime', required=True,help='Start Time List')
parser.add_argument('-endTime', required=True,help='End Time List')
parser.add_argument('-tickSize',required=True,help="Nse Currency = 25000 , Future Options = 5")
parser.add_argument('-targetType',required=True,help="1,2,3,4 ")
parser.add_argument('-e',required=True,help="experiment design file to be used")
args = parser.parse_args()

sys.path.append("./src/")
sys.path.append("./ob/generators/")
import dataFile, colNumberOfData, common
import attribute

if args.skipT == None:
    args.skipT = "no"
                    
absPathOfExperimentName = os.path.abspath(args.e)

if 'nsecur' in absPathOfExperimentName:
    pathAfterE = absPathOfExperimentName[absPathOfExperimentName.index("/nsecur/")+8:]
elif 'nsefut' in absPathOfExperimentName:
    pathAfterE = absPathOfExperimentName[absPathOfExperimentName.index("/nsefut/")+8:]
elif 'nseopt' in absPathOfExperimentName:
    pathAfterE = absPathOfExperimentName[absPathOfExperimentName.index("/nseopt/")+8:]
    
if "/" in pathAfterE:
    mainExperimentName = pathAfterE[:pathAfterE.index("/")]
else:
    mainExperimentName = pathAfterE
    
experimentName = os.path.basename(absPathOfExperimentName)
gTickSize = int(args.tickSize)
gMaxQty = int(args.orderQty)

startTimeList = args.startTime.split(";")
endTimeList = args.endTime.split(";")
initialFileName = []
for indexOfCL in range(0,len(startTimeList)):
    lInitialFileName ='DummyTradeEngine-d.' + os.path.basename(os.path.abspath(args.d)) + '-l.'+startTimeList[indexOfCL]+"-"+endTimeList[indexOfCL] + "-tq." + args.orderQty + "-tarType" + args.targetType + "-dte.7" 
    initialFileName.append(lInitialFileName)
    

g_quantity_adjustment_list_for_sell = {}
g_quantity_adjustment_list_for_buy = {}

def functionToReadTargetFileToDictionary(pTargetValuesFile,pTargetValuesDict,pFileHeader):
    lNumberOfLinesInTargetValuesFile = 0
    for line in pTargetValuesFile:
        if pFileHeader == True:
            pFileHeader = False
            continue
        line=line.rstrip('\n')
        splitLine = line.split(';')
        timeStamp = float(splitLine[0])
        try:#TODO: remove this and then run the code to identify errors.
            targetProb = float(splitLine[1])
        except:
            targetProb = 0
        pTargetValuesDict[timeStamp] = targetProb
        lNumberOfLinesInTargetValuesFile += 1
    return lNumberOfLinesInTargetValuesFile

def getTargetValuesIntoDict(pTargetValuesDict):
    # The following will take care if args.e = "ob/e1/" or args.e = "ob/e1"
    dirName = args.d.replace('/ro/','/wf/')
    config = ConfigObj(args.e+"/design.ini")
    target = config["target"]
    lTargetBuyValuesDict = dict()
    targetBuyValuesFileName = dirName+"/t/" + target['newBuy'+args.targetType] + ".target"
    print("Buy Target values file : "+ targetBuyValuesFileName)
    sys.stdout.flush()
    targetBuyValuesFile = open(targetBuyValuesFileName)
    fileHasHeader = True
    numberOfLinesInBuyTargetValuesFile = functionToReadTargetFileToDictionary(targetBuyValuesFile,lTargetBuyValuesDict,fileHasHeader)
    print("Finished reading the buy target values file")    
    print("The number of elements in the buy target values dictionary is : " + str(len(lTargetBuyValuesDict)))
#     if (numberOfLinesInBuyTargetValuesFile != len(lTargetBuyValuesDict)):
#         print("Number of duplicate time stamps rejected in buy target values dictionary = " + str(numberOfLinesInBuyTargetValuesFile - len(lTargetBuyValuesDict)))
#         os._exit(-1)
    sys.stdout.flush()

    lTargetSellValuesDict = dict()
    targetSellValuesFileName = dirName+"/t/" + target['newSell'+args.targetType] + ".target"
    print("Sell Target values file : "+ targetSellValuesFileName)
    sys.stdout.flush()
    targetSellValuesFile = open(targetSellValuesFileName)
    fileHasHeader = True
    numberOfLinesInSellTargetValuesFile = functionToReadTargetFileToDictionary(targetSellValuesFile,lTargetSellValuesDict,fileHasHeader)
    print("Finished reading the sell target values file")    
    print("The number of elements in the sell target values dictionary is : " + str(len(lTargetSellValuesDict)))
#     if (numberOfLinesInSellTargetValuesFile != len(lTargetSellValuesDict)):
#         print("Number of duplicate timestamps rejected in sell target values dictionary = " + str(numberOfLinesInSellTargetValuesFile - len(lTargetSellValuesDict)))
#         os._exit(-1)
    sys.stdout.flush()
#-----------------Getting target values into dictionary -------------------------------------
    for elements in lTargetBuyValuesDict.keys():
        pTargetValuesDict[elements] = {}
        pTargetValuesDict[elements]['buy'] = lTargetBuyValuesDict[elements]
        pTargetValuesDict[elements]['sell'] = lTargetSellValuesDict[elements] 


def checkIfPreviousDecisionToEnterOrExitTradeWasSuccessful(pCurrentDataRow,pTTQAtTimeOfPreviousDataRow,pAskP0AtTimeOfPreviousDataRow,pBidP0AtTimeOfPreviousDataRow,\
                                                           pAskQ0AtTimeOfPreviousDataRow , pBidQ0AtTimeOfPreviousDataRow , pEnterTradeShort, pEnterTradeLong, pTradeStats,pReasonForTrade ,\
                                                           pPrevReasonForTradingOrNotTradingLong, pPrevReasonForTradingOrNotTradingShort ):
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
            elif ("OpenSell(Hitting)" in pPrevReasonForTradingOrNotTradingShort) or ("CloseSell(Hitting)" in pPrevReasonForTradingOrNotTradingLong):
                pReasonForTrade['PrevWasOurOrder'] += 1
                lReasonForTradingOrNotTradingShort = 'TTQChangeBecauseOfOurOrder' 
            else:    
               
                lQtyTraded = min(  pTradeStats['currentPositionShort'] , l_dummy_TTQChange_For_Buy )
                l_dummy_TTQChange_For_Buy -= lQtyTraded
                pTradeStats['totalBuyValueShort'] += lQtyTraded * (pBidP0AtTimeOfPreviousDataRow + gTickSize)
                pTradeStats['currentPositionShort'] -= lQtyTraded
                lReasonForTradingOrNotTradingShort = 'CloseBuy(Standing)'
                pReasonForTrade['CloseBuyTradeHappened'] += lQtyTraded
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
            pReasonForTrade['CloseBuyTradeHappened'] += l_buy_qty
             
            if l_buy_qty > 0:
                lReasonForTradingOrNotTradingShort = 'CloseBuy(Hitting)'
            else :
                lReasonForTradingOrNotTradingShort = "DummyAskQExhuasted"
        
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
            elif ("OpenSell(Hitting)" in pPrevReasonForTradingOrNotTradingShort) or ("CloseSell(Hitting)" in pPrevReasonForTradingOrNotTradingLong):
                pReasonForTrade['PrevWasOurOrder'] += 1
                lReasonForTradingOrNotTradingShort = 'TTQChangeBecauseOfOurOrder' 
            else:

                lQtyToBeTraded = ( gMaxQty - pTradeStats['currentPositionLong'] )
                lQtyForWhichWeTrade = min( lQtyToBeTraded , l_dummy_TTQChange_For_Buy)
                l_dummy_TTQChange_For_Buy -= lQtyForWhichWeTrade
                pTradeStats['totalBuyValueLong'] += lQtyForWhichWeTrade * (pBidP0AtTimeOfPreviousDataRow + gTickSize)
                pTradeStats['currentPositionLong'] += lQtyForWhichWeTrade
                lReasonForTradingOrNotTradingLong = 'OpenBuy(Standing)'
                pReasonForTrade['OpenBuyTradeHappened'] += lQtyForWhichWeTrade
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
                pReasonForTrade['OpenBuyTradeHappened'] += lQtyForWhichWeTrade
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
            elif ("OpenSell(Hitting)" in pPrevReasonForTradingOrNotTradingShort) or ("CloseSell(Hitting)" in pPrevReasonForTradingOrNotTradingLong):
                pReasonForTrade['PrevWasOurOrder'] += 1
                lReasonForTradingOrNotTradingShort = 'TTQChangeBecauseOfOurOrder' 
            else:    

                lQtyTraded = min(  pTradeStats['currentPositionLong'] , l_dummy_TTQChange_For_Sell )
                pTradeStats['totalSellValueLong'] += lQtyTraded * (pAskP0AtTimeOfPreviousDataRow - gTickSize)
                pTradeStats['currentPositionLong'] -= lQtyTraded
                l_dummy_TTQChange_For_Sell -= lQtyTraded
                lReasonForTradingOrNotTradingLong = 'CloseSell(Standing)'
                pReasonForTrade['CloseSellTradeHappened'] += lQtyTraded
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
            
            if lQtyTraded > 0 :
                lReasonForTradingOrNotTradingLong = 'CloseSell(Hitting)'
            else :
                lReasonForTradingOrNotTradingLong = "DummyBidQExhuasted"
            pReasonForTrade['CloseSellTradeHappened'] += lQtyTraded
    
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
            elif ("OpenSell(Hitting)" in pPrevReasonForTradingOrNotTradingShort) or ("CloseSell(Hitting)" in pPrevReasonForTradingOrNotTradingLong):
                pReasonForTrade['PrevWasOurOrder'] += 1
                lReasonForTradingOrNotTradingShort = 'TTQChangeBecauseOfOurOrder' 
            else:

                lQtyToBeTraded = ( gMaxQty - pTradeStats['currentPositionShort'] )
                lQtyForWhichWeTrade = min( lQtyToBeTraded , l_dummy_TTQChange_For_Sell)
                pTradeStats['totalSellValueShort'] += lQtyForWhichWeTrade * (pAskP0AtTimeOfPreviousDataRow - gTickSize)
                pTradeStats['currentPositionShort'] += lQtyForWhichWeTrade
                l_dummy_TTQChange_For_Sell -= lQtyForWhichWeTrade
                lReasonForTradingOrNotTradingShort = 'OpenSell(Standing)'
                pReasonForTrade['OpenSellTradeHappened'] += lQtyForWhichWeTrade
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
                pReasonForTrade['OpenSellTradeHappened'] += lQtyForWhichWeTrade
                l_dummy_BidQ0 -= lQtyForWhichWeTrade
            else:
                lReasonForTradingOrNotTradingShort = 'DummyBidQZero'

    return [ lReasonForTradingOrNotTradingShort , lReasonForTradingOrNotTradingLong , l_dummy_BidQ0 , l_dummy_AskQ0 , l_dummy_TTQChange_For_Buy , l_dummy_TTQChange_For_Sell]

def readOnceAndWrite(pFileName, pIndexOfEntryOrExitCL, targetValuesDict):
   attribute.initList()
   enterTradeShort = 0
   enterTradeLong = 0
   ltpAtTimeOfPreviousDataRow = 0
   ttqAtTimeOfPreviousDataRow = 0
   askP0AtTimeOfPreviousDataRow = 0
   bidP0AtTimeOfPreviousDataRow = 0
   askQ0AtTimeOfPreviousDataRow = 0
   bidQ0AtTimeOfPreviousDataRow = 0
   exchangeTimeStamp = 0 
   currentTimeStamp = 0
   tradeStats = dict()
   tradeStats['totalSellValueShort'] = 0
   tradeStats['totalBuyValueShort'] = 0
   tradeStats['currentPositionShort'] = 0
   tradeStats['totalSellValueLong'] = 0
   tradeStats['totalBuyValueLong'] = 0
   tradeStats['currentPositionLong'] = 0
   noTargetForThisRow = 0
   currentSellTargetValue = 0
   currentBuyTargetValue = 0
   startTime = map(float,startTimeList[pIndexOfEntryOrExitCL].split("h"))
   endTime = map(float,endTimeList[pIndexOfEntryOrExitCL].split("h"))
   print (startTime, endTime)
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
   reasonForTrade['CloseBuyTradeHappened'] = 0
   reasonForTrade['OpenBuyTradeHappened'] = 0
   reasonForTrade['LTPDoesNotEqualAskP0Long'] = 0
   reasonForTrade['LTPDoesNotEqualBidP0Long'] = 0
   reasonForTrade['VolumeDidNotIncreaseDuringSellAttemptShort'] = 0
   reasonForTrade['VolumeDidNotIncreaseDuringSellAttemptLong'] = 0
   reasonForTrade['OpenSellTradeHappened'] = 0
   reasonForTrade['CloseSellTradeHappened'] = 0
   reasonForTrade['PrevWasOurOrder'] = 0
   lReasonForTradingOrNotTradingShort = ""
   lReasonForTradingOrNotTradingLong = ""
   currentIndex = 0
   lDummyBidQ0 = 0
   lDummyAskQ0=0 
   lDummyTTQForBuy =0 
   lDummyTTQForSell = 0
   print("Processing the data file for trades :")
   attribute.initList()
   prevBuyTargetValue = 0
   prevSellTargetValue = 0
   exchangeTimeStamp = 0
   l_exchange_time_stamp_to_print= ""
   for currentDataRow in dataFile.matrix:
    
       l_expiry_wrt_1970 = exchangeTimeStamp + 315513000.0
       
       l_dt = datetime.datetime.fromtimestamp(l_expiry_wrt_1970)
       l_exchange_time_stamp_to_print = str(l_dt.hour) + ":" + str(l_dt.minute) + ":" + str(l_dt.second)
       if (l_dt.hour > startTime[0] or (l_dt.hour == startTime[0] and l_dt.minute >= startTime[1]) ):
           lReturnList = checkIfPreviousDecisionToEnterOrExitTradeWasSuccessful(currentDataRow,ttqAtTimeOfPreviousDataRow,askP0AtTimeOfPreviousDataRow,bidP0AtTimeOfPreviousDataRow,\
                                                                                askQ0AtTimeOfPreviousDataRow , bidQ0AtTimeOfPreviousDataRow , enterTradeShort,enterTradeLong,tradeStats,reasonForTrade,\
                                                                                lReasonForTradingOrNotTradingLong,lReasonForTradingOrNotTradingShort )
    
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
               listOfStringsToPrint = [ str(bidQ0AtTimeOfPreviousDataRow) , str(bidP0AtTimeOfPreviousDataRow) , str(askP0AtTimeOfPreviousDataRow) , \
                                       str(askQ0AtTimeOfPreviousDataRow) , str(ttqAtTimeOfPreviousDataRow) , str(ltpAtTimeOfPreviousDataRow) ,\
                                       str(currentSellTargetValue) , str(enterTradeShort) ,lReasonForTradingOrNotTradingShort , str(currentBuyTargetValue) ,\
                                       str(enterTradeLong) ,lReasonForTradingOrNotTradingLong ,l_exchange_time_stamp_to_print, str(reasonForTrade['CloseBuyTradeHappened']),\
                                       str(reasonForTrade['OpenBuyTradeHappened']),str(reasonForTrade['OpenSellTradeHappened']),\
                                       str(reasonForTrade['CloseSellTradeHappened']),str(lDummyBidQ0),str(lDummyAskQ0),\
                                       str(lDummyTTQForBuy),str(lDummyTTQForSell)]
               attribute.aList[currentIndex-1][3] =  ";".join(listOfStringsToPrint)
               if ( l_dt.hour > endTime[0] or ( l_dt.hour == endTime[0] and l_dt.minute >= endTime[1] )  )and tradeStats['currentPositionShort'] == 0 and tradeStats['currentPositionLong'] == 0 :
                   break
       currentTimeStamp = common.convertTimeStampFromStringToFloat(currentDataRow[colNumberOfData.TimeStamp])

       try:
           currentSellTargetValue = float(targetValuesDict[currentTimeStamp]['sell']) 
           currentBuyTargetValue  = float(targetValuesDict[currentTimeStamp]['buy'])
       except:
           noTargetForThisRow += 1

       #short decisions
       if(currentSellTargetValue == 1):
           enterTradeShort = 1
           numberOfTimesAskedToEnterTradeShort += 1
       elif(currentSellTargetValue == 0 and tradeStats['currentPositionShort'] > 0):
           numberOfTimesAskedToExitTradeShort += 1
           enterTradeShort = -1  # Implies to exit the trade
       else:
           enterTradeShort = 0  # Implies make no change
           
       #long decisions
       if(currentBuyTargetValue == 1):
           enterTradeLong = 1
           numberOfTimesAskedToEnterTradeLong += 1
       elif(currentBuyTargetValue == 0 and tradeStats['currentPositionLong'] > 0):
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
       prevBuyTargetValue = currentBuyTargetValue
       prevSellTargetValue = currentSellTargetValue
       exchangeTimeStamp = float(currentDataRow[colNumberOfData.ExchangeTS])

# Squaring off if some open position there   
   if tradeStats['currentPositionLong'] > 0:
       reasonForTrade['CloseSellTradeHappened'] += tradeStats['currentPositionLong']
       tradeStats['totalSellValueLong'] += tradeStats['currentPositionLong'] * (bidP0AtTimeOfPreviousDataRow)
       tradeStats['currentPositionLong'] = 0
       lReasonForTradingOrNotTradingLong = 'CloseSell(Hitting)'
   if tradeStats['currentPositionShort'] > 0:
       reasonForTrade['CloseBuyTradeHappened'] += tradeStats['currentPositionShort']
       tradeStats['totalBuyValueShort'] += tradeStats['currentPositionShort'] * (askP0AtTimeOfPreviousDataRow)
       tradeStats['currentPositionShort'] = 0
       lReasonForTradingOrNotTradingLong = 'CloseBuy(Hitting)'

   attribute.aList[currentIndex-1][0] = currentTimeStamp
   attribute.aList[currentIndex-1][1] = tradeStats['currentPositionLong']
   attribute.aList[currentIndex-1][2] = tradeStats['currentPositionShort']
   listOfStringsToPrint = [ str(bidQ0AtTimeOfPreviousDataRow) , str(bidP0AtTimeOfPreviousDataRow) , str(askP0AtTimeOfPreviousDataRow) ,\
                            str(askQ0AtTimeOfPreviousDataRow) , str(ttqAtTimeOfPreviousDataRow) , str(ltpAtTimeOfPreviousDataRow) , \
                            str(currentSellTargetValue) , str(enterTradeShort) , "" , str(currentBuyTargetValue) , str(enterTradeLong) ,\
                            "" ,l_exchange_time_stamp_to_print, str(reasonForTrade['CloseBuyTradeHappened']),str(reasonForTrade['OpenBuyTradeHappened']),str(reasonForTrade['OpenSellTradeHappened']),\
                            str(reasonForTrade['CloseSellTradeHappened']),str(lDummyBidQ0),str(lDummyAskQ0),str(lDummyTTQForBuy),str(lDummyTTQForSell)]
   attribute.aList[currentIndex-1][3] =  ";".join(listOfStringsToPrint) 
   
   dirName = args.d.replace('/ro/','/rs/')
   tradeLogMainDirName = dirName+"/t/"
   if not os.path.exists(tradeLogMainDirName):
        os.mkdir(tradeLogMainDirName)
   tradeLogSubDirectoryName =  tradeLogMainDirName + mainExperimentName+"/"
   if not os.path.exists(tradeLogSubDirectoryName):
        os.mkdir(tradeLogSubDirectoryName)

   fileName = tradeLogSubDirectoryName + pFileName + ".targetTrade" 
   lHeaderColumnNamesList  = ['TimeStamp','CurrentPositionLong','CurrentPositionShort','BidQ0','BidP0','AskP0','AskQ0','TTQ','LTP',\
                              'CurTargetValueShort','EnterTradeShort','ReasonForTradingOrNotTradingShort','CurTargetValueLong','EnterTradeLong',\
                              'ReasonForTradingOrNotTradingLong','Exchange_TS','totalBuyShort','totalBuyLong','totalSellShort','totalSellLong','DummyBidQ0',\
                              'DummyAskQ0','DummyTTQChangeForSell','DummyTTQChangeForBuy']
#    attribute.writeToFile(fileName , lHeaderColumnNamesList)

   tradeResultMainDirName = dirName+"/r/"
   if not os.path.exists(tradeResultMainDirName):
        os.mkdir(tradeResultMainDirName)
   tradeResultSubDirectoryName =  tradeResultMainDirName + mainExperimentName+"/"
   if not os.path.exists(tradeResultSubDirectoryName):
        os.mkdir(tradeResultSubDirectoryName)
   fileName = tradeResultSubDirectoryName+pFileName+".targetResult" 
   outputFile = open(fileName,"w")
 
   #changed file write to modify it to Short Long version
   print("Starting to write: "+fileName)
   print("The net results for Short are: " + str(tradeStats['totalSellValueShort'] - tradeStats['totalBuyValueShort']), file = outputFile)
   print("The net results for Long are: " + str(tradeStats['totalSellValueLong'] - tradeStats['totalBuyValueLong']), file = outputFile)
   print("Number of rows for which there is no target: " + str(noTargetForThisRow), file = outputFile)    
   print("Number of times asked to enter trade Short: " + str(numberOfTimesAskedToEnterTradeShort), file = outputFile)    
   print("Number of times asked to enter trade Long: " + str(numberOfTimesAskedToEnterTradeLong), file = outputFile)    
   print("Number of times asked to exit trade Short: " + str(numberOfTimesAskedToExitTradeShort), file = outputFile)
   print("Number of times asked to exit trade Long: " + str(numberOfTimesAskedToExitTradeLong), file = outputFile)
   print("Assumed close buy trade did not happen since volume did not increase: " + str(reasonForTrade['VolumeDidNotIncreaseDuringBuyAttemptShort']), file = outputFile)
   print("Assumed open buy trade did not happen since volume did not increase: " + str(reasonForTrade['VolumeDidNotIncreaseDuringBuyAttemptLong']), file = outputFile)
   print("Assumed close buy trade did not happen since bidP0 not same as LTP: " + str(reasonForTrade['LTPDoesNotEqualBidP0Short']), file = outputFile)
   print("Assumed open buy trade did not happen since bidP0 not same as LTP: " + str(reasonForTrade['LTPDoesNotEqualBidP0Long']), file = outputFile)
   print("Assumed close buy trade happened: " + str(reasonForTrade['CloseBuyTradeHappened']), file = outputFile)
   print("Assumed open buy trade happened: " + str(reasonForTrade['OpenBuyTradeHappened']), file = outputFile)
   print("Assumed open sell trade did not happen since volume did not increase: " + str(reasonForTrade['VolumeDidNotIncreaseDuringSellAttemptShort']), file = outputFile)
   print("Assumed close sell trade did not happen since volume did not increase: " + str(reasonForTrade['VolumeDidNotIncreaseDuringSellAttemptLong']), file = outputFile)
   print("Assumed open sell trade did not happen since bidP0 not same as LTP: " + str(reasonForTrade['LTPDoesNotEqualAskP0Short']), file = outputFile)
   print("Assumed close sell trade did not happen since bidP0 not same as LTP: " + str(reasonForTrade['LTPDoesNotEqualAskP0Long']), file = outputFile)
   print("Assumed open sell trade happened: " + str(reasonForTrade['OpenSellTradeHappened']), file = outputFile)
   print("Assumed close sell trade happened: " + str(reasonForTrade['CloseSellTradeHappened']), file = outputFile)
   print("The total open sell value is: " + str(tradeStats['totalSellValueShort']), file = outputFile)
   print("The total close sell value is: " + str(tradeStats['totalSellValueLong']), file = outputFile)
   print("The total close buy value is: " + str(tradeStats['totalBuyValueShort']), file = outputFile)
   print("The total open buy value is: " + str(tradeStats['totalBuyValueLong']), file = outputFile)

   try:
       averageOpenSellPrice = tradeStats['totalSellValueShort']/reasonForTrade['OpenSellTradeHappened']
       averageCloseBuyPrice = tradeStats['totalBuyValueShort']/reasonForTrade['CloseBuyTradeHappened']
   except:
       averageOpenSellPrice = 0 
       averageCloseBuyPrice = 0
   try:
       averageCloseSellPrice = tradeStats['totalSellValueLong']/reasonForTrade['CloseSellTradeHappened']
       averageOpenBuyPrice = tradeStats['totalBuyValueLong']/reasonForTrade['OpenBuyTradeHappened']
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


def main():
    dataFile.getDataIntoMatrix(args.d)
    targetValuesDict = dict()
    getTargetValuesIntoDict(targetValuesDict)
    lIndexOfEntryOrExitCL = 0
    for lFileName in initialFileName:
        readOnceAndWrite(lFileName, lIndexOfEntryOrExitCL, targetValuesDict)
        lIndexOfEntryOrExitCL = lIndexOfEntryOrExitCL + 1
    
if __name__ == "__main__":
   dirName = args.d.replace('/ro/','/rs/')
   checkAllFilesAreExistOrNot = 'false'

   lWFDirName = args.d.replace('/ro/','/wf/')
   for lFileName in initialFileName:
       fileName = dirName + "/r/" + mainExperimentName + "/" + lFileName+".targetResult"
       if os.path.isfile(fileName) and args.skipT.lower() == "yes":
           print("Trade results file " + fileName + "Already exist. Not regenerating it. If you want to rerun it by making -skipT = no ")
       else: 
           checkAllFilesAreExistOrNot = 'true'
           print("Trade results file " + fileName + " Does not exist.")
    
   if checkAllFilesAreExistOrNot == 'true':
       print ("\nRunning the simulated trading program")
       main()


