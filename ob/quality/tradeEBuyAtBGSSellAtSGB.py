#!/usr/bin/python
from __future__ import division
from __future__ import print_function
import os, sys, argparse
from configobj import ConfigObj
from itertools import islice
from datetime import datetime
parser = argparse.ArgumentParser(description='This program will do trades to measure the quality of the experiment.\n\
 An e.g. command line is tradeE5.py -d ob/data/20140207/ -e ob/e/1 -a logitr -entryCL 0.90 -exitCL .55 -orderQty 500', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-e', required=True,help='Directory of the experiment or sub experiment e/10/s/3c/ABC')
parser.add_argument('-a', required=True,help='Algorithm name')
parser.add_argument('-entryCL', required=True,help='Percentage of the confidence level used to enter the trades')
parser.add_argument('-exitCL', required=True,help='Percentage of the confidence level used to exit the trades')
parser.add_argument('-orderQty',required=True,help='Order Quantity with which we trade')
parser.add_argument("-skipT",required=False,help="Skip creating trade files if already generated")
parser.add_argument('-td', required=True,help='Directory of the training data file')
parser.add_argument('-pd', required=True,help='Directory of the prediction data file')
parser.add_argument('-dt',required=True,help="Number of days it was trained")  
parser.add_argument('-targetClass',required=False,help="For which model was used ; binomial(target takes only true and false) / multinomial (target values takes more than 2 values)")
parser.add_argument('-tickSize',required=True,help="Nse Currency = 25000 , Future Options = 5")
parser.add_argument('-wt',required=False,help="default/exp , weight type to be given to different days")
parser.add_argument('-iT',required=False,help='Instrument name')
parser.add_argument('-sP',required=False,help='Strike price of instrument')
parser.add_argument('-oT',required=False,help='Options Type')
parser.add_argument('-t',required=False,help='Transaction Cost')
parser.add_argument('-double',required=False,help='Double training of in model')
args = parser.parse_args()

sys.path.append("./src/")
sys.path.append("./ob/generators/")
import dataFile, colNumberOfData, common
import attribute
attribute.initializeInstDetails(args.iT,args.sP,args.oT)
if args.skipT == None:
    args.skipT = "no"
# if args.pT == None:
#     args.pT = "no"
if args.targetClass == None:
    args.targetClass = "binomial"
if args.wt == None:
    args.wt = "default"
                    
absPathOfExperimentName = os.path.abspath(args.e)

if 'nsecur' in absPathOfExperimentName:
    pathAfterE = absPathOfExperimentName[absPathOfExperimentName.index("/nsecur/")+8:]
    if args.t ==None:
        transactionCost = 0.000015
        currencyDivisor = 10000
elif 'nsefut' in absPathOfExperimentName:
    pathAfterE = absPathOfExperimentName[absPathOfExperimentName.index("/nsefut/")+8:]
    if args.t == None:
        transactionCost = 0.00015
        currencyDivisor = 100
elif 'nseopt' in absPathOfExperimentName:
    pathAfterE = absPathOfExperimentName[absPathOfExperimentName.index("/nseopt/")+8:]
    transactionCost = args.t
    currencyDivisor = 0
    print("Please specify the transaction cost and currency divisor for options and remove os.exit(-1) and rerun it")
    os._exit(-1)
if "/" in pathAfterE:
    mainExperimentName = pathAfterE[:pathAfterE.index("/")]
else:
    mainExperimentName = pathAfterE
    
experimentName = os.path.basename(absPathOfExperimentName)
gTickSize = int(args.tickSize)
gMaxQty = int(args.orderQty)
gNoOfLineReadPerChunk = 10000
g_quantity_adjustment_list_for_sell = {}
g_quantity_adjustment_list_for_buy = {}

class Tick():
    def __init__(self,pCurrentDataRowTimeStamp,pAskP,pBidP,pAskQ,pBidQ,pLTP,pTTQ,pBuyPredictedValue,pSellPredictedValue):
        self.AskP = pAskP
        self.AskQ = pAskQ
        self.BidP = pBidP
        self.BidQ = pBidQ
        self.LTP = pLTP
        self.TTQ  = pTTQ
        self.TTQChange = 0 
        self.NextLTP = 0
        self.currentTimeStamp = pCurrentDataRowTimeStamp
        self.currentBuyPredictedValue = pBuyPredictedValue
        self.currentSellPredictedValue = pSellPredictedValue
        self.bidPChangedInBetweenLastTickAndCurrentTick = 0
        self.askPChangedInBetweenLastTickAndCurrentTick = 0

def getDataFileAndPredictionsIntoObjectList(dataFileObject,buyPredictFileObject,sellPredictFileObject):
    global gNoOfLineReadPerChunk,gTickSize
    lObjectList = []
    lCurrentDataRowCount = 0
    lPrevObj = None
    fileHasHeader = 1
    headerSkipped = 0
    dataFileSep = ";"
    predictFileSep = ","
    lListOfBidP = []
    lListOfAskP = []
    l_data_row_list =  list(islice(dataFileObject,10000))
    while True:
        lDataFileRowsList = list(islice(dataFileObject,gNoOfLineReadPerChunk))
        lBuyPredictedFileRowList = list(islice(buyPredictFileObject,gNoOfLineReadPerChunk))
        lSellPredictedFileRowList = list(islice( sellPredictFileObject,gNoOfLineReadPerChunk ))
        if not lDataFileRowsList :
            print("Finished reading file")
            lObjectList.append(lPrevObj)    
            lPrevObj = None          
            break
        lengthOfDataList = len(lDataFileRowsList)
        lengthOfBuyPredList = len(lBuyPredictedFileRowList)
        lengthOfSellPredList = len(lSellPredictedFileRowList)
        if lengthOfDataList!=lengthOfBuyPredList or lengthOfBuyPredList!=lengthOfSellPredList:
            print("Length of data file and predicted buy and sell values file are not same ")
            os._exit(-1)
        for currentRowIndex in range(lengthOfDataList):
            if(fileHasHeader == 1 and headerSkipped != 1):
                headerSkipped =1
                continue
            lDataRow = lDataFileRowsList[currentRowIndex].rstrip().split(dataFileSep)
            if((args.e).find("nsefut") >= 0):
                lAskP = float(lDataRow[colNumberOfData.BestAskP])
                lBidP = float(lDataRow[colNumberOfData.BestBidP])
                lAskQ = int(lDataRow[colNumberOfData.BestAskQ])
                lBidQ = int(lDataRow[colNumberOfData.BestBidQ])
            else:
                lAskP = float(lDataRow[colNumberOfData.AskP0])
                lBidP = float(lDataRow[colNumberOfData.BidP0])
                lAskQ = int(lDataRow[colNumberOfData.AskQ0])
                lBidQ = int(lDataRow[colNumberOfData.BidQ0])
            lTTQ = int(lDataRow[colNumberOfData.TTQ])
            lLTP = float(lDataRow[colNumberOfData.LTP]) 
            lCurrentDataRowTimeStamp = common.convertTimeStampFromStringToFloat(lDataRow[colNumberOfData.TimeStamp])
            lBuyPredictedRow = lBuyPredictedFileRowList[currentRowIndex].rstrip().split(predictFileSep)
            lBuyPredictedTimeStamp = float(lBuyPredictedRow[1])
            lBuyPredictedValue = float(lBuyPredictedRow[2])
            lSellPredictedRow = lSellPredictedFileRowList[currentRowIndex].rstrip().split(predictFileSep)
            lSellPredictedTimeStamp = float(lSellPredictedRow[1])
            lSellPredictedValue = float(lSellPredictedRow[2])
            
            if( lCurrentDataRowTimeStamp != lBuyPredictedTimeStamp or lBuyPredictedTimeStamp!=lSellPredictedTimeStamp):
                lDataRow = lDataFileRowsList[currentRowIndex].rstrip().split(dataFileSep)
                print('Time stamp of data row with predicted value is not matching .\n Data row time stamp :- ' , lCurrentDataRowTimeStamp,'BuyPredicted Time Stamp :- ' , lBuyPredictedTimeStamp\
                      ,"SellPredicted Time Stamp :- ",lSellPredictedTimeStamp)
                os._exit(-1)
            else:
                lObj = Tick(lCurrentDataRowTimeStamp,lAskP,lBidP,lAskQ,lBidQ,lLTP,lTTQ,lBuyPredictedValue,lSellPredictedValue)
                if lPrevObj!=None:
                    lPrevObj.TTQChange  = lObj.TTQ - lPrevObj.TTQ
                    lPrevObj.NextLTP = lObj.LTP
                    if ( lPrevObj.AskP -lPrevObj.BidP > gTickSize ) and ( lPrevObj.TTQChange == 0 ):
                        if lPrevObj.BidP not in lListOfBidP:
                            lListOfBidP.append(lPrevObj.BidP)
                        if lPrevObj.AskP not in lListOfAskP:
                            lListOfAskP.append(lPrevObj.AskP)
                        pass
                    else:
                        if len(lListOfBidP) > 1:
                            lPrevObj.bidPChangedInBetweenLastTickAndCurrentTick = 1
                        if len(lListOfAskP) > 1:
                            lPrevObj.askPChangedInBetweenLastTickAndCurrentTick = 1
                        lObjectList.append(lPrevObj)  
                        lListOfBidP = [lPrevObj.BidP]
                        lListOfAskP = [lPrevObj.AskP]
                lPrevObj = lObj
            if lCurrentDataRowCount%50000 ==0:
                print("Completed reading ",lCurrentDataRowCount)
            lCurrentDataRowCount = lCurrentDataRowCount + 1 
    return lObjectList

def checkIfDecisionToEnterOrExitTradeIsSuccessful(pObject, pEnterTradeShort, pEnterTradeLong, pTradeStats,pReasonForTrade ,pPrevReasonForTradingOrNotTradingLong, pPrevReasonForTradingOrNotTradingShort ):
    global gTickSize , gMaxQty , g_quantity_adjustment_list_for_sell , g_quantity_adjustment_list_for_buy
    global transactionCost , currencyDivisor 
    lSpread = pObject.AskP - pObject.BidP
    lReasonForTradingOrNotTradingShort = ""
    lReasonForTradingOrNotTradingLong = ""

    if pObject.BidP in g_quantity_adjustment_list_for_sell and pObject.bidPChangedInBetweenLastTickAndCurrentTick==0:
        l_dummy_BidQ0 = max( 0 , pObject.BidQ - g_quantity_adjustment_list_for_sell[pObject.BidP])
    else:
        g_quantity_adjustment_list_for_sell = {}
        l_dummy_BidQ0 =  pObject.BidQ

    if pObject.AskP in g_quantity_adjustment_list_for_buy and pObject.askPChangedInBetweenLastTickAndCurrentTick==0:
        l_dummy_AskQ0 = max( 0 ,pObject.AskQ - g_quantity_adjustment_list_for_buy[pObject.AskP])
    else:
        g_quantity_adjustment_list_for_buy = {}    
        l_dummy_AskQ0 = pObject.AskQ
        
    if(pEnterTradeShort == 0 and pEnterTradeLong == 0):
        return lReasonForTradingOrNotTradingShort , lReasonForTradingOrNotTradingLong ,0 , 0 , 0 , 0

    l_dummy_TTQChange_For_Buy = pObject.TTQChange
    #close buy
    if(pEnterTradeShort == -1): # Need to buy we come here only if currentPosition is greater than 0 so no need to check again.
        #standing
        if lSpread > gTickSize:        
            if(l_dummy_TTQChange_For_Buy<=0):
                pReasonForTrade['VolumeDidNotIncreaseDuringBuyAttemptShort'] += 1
                lReasonForTradingOrNotTradingShort = '(Spread>Pip)&&(NextTickTTQDidNotIncrease)'
            elif(pObject.NextLTP != pObject.BidP): 
                pReasonForTrade['LTPDoesNotEqualBidP0Short'] += 1
                lReasonForTradingOrNotTradingShort = '(Spread>Pip)&&(LTP!=Bid)'
            else:    
               
                lQtyTraded = min(  pTradeStats['currentPositionShort'] , l_dummy_TTQChange_For_Buy )
                l_dummy_TTQChange_For_Buy -= lQtyTraded
                pTradeStats['totalBuyValueShort'] += lQtyTraded * (pObject.BidP + gTickSize)
                pTradeStats['currentPositionShort'] -= lQtyTraded
                lReasonForTradingOrNotTradingShort = 'CloseBuy(Standing)'
                pReasonForTrade['CloseBuyTradeHappened'] += lQtyTraded
        #hitting
        else:

            l_buy_qty = min( pTradeStats['currentPositionShort'], l_dummy_AskQ0)
            if pObject.AskP in g_quantity_adjustment_list_for_buy:
                    g_quantity_adjustment_list_for_buy[pObject.AskP] += l_buy_qty
            else:  
                    g_quantity_adjustment_list_for_buy = {} 
                    g_quantity_adjustment_list_for_buy[pObject.AskP] = l_buy_qty
            l_dummy_AskQ0 -= l_buy_qty
            pTradeStats['totalBuyValueShort'] += l_buy_qty * (pObject.AskP)
            pTradeStats['currentPositionShort'] -= l_buy_qty
            pReasonForTrade['CloseBuyTradeHappened'] += l_buy_qty
             
            if l_buy_qty > 0:
                lReasonForTradingOrNotTradingShort = 'CloseBuy(Hitting)'
            else :
                lReasonForTradingOrNotTradingShort = "DummyAskQExhuasted"
        
    #open buy
    if(pEnterTradeLong == 1 and ( gMaxQty - pTradeStats['currentPositionLong'] ) > 0): # Need to buy
        #standing
        if lSpread > gTickSize:        
            if(l_dummy_TTQChange_For_Buy <= 0 ):
                pReasonForTrade['VolumeDidNotIncreaseDuringBuyAttemptLong'] += 1
                lReasonForTradingOrNotTradingLong = '(Spread>Pip)&&(NextTickTTQDidNotIncrease)'
            elif(pObject.NextLTP != pObject.BidP):
                pReasonForTrade['LTPDoesNotEqualBidP0Long'] += 1
                lReasonForTradingOrNotTradingLong = '(Spread>Pip)&&(LTPDoesNotEqualBidP0Long)'
            else:

                lQtyToBeTraded = ( gMaxQty - pTradeStats['currentPositionLong'] )
                lQtyForWhichWeTrade = min( lQtyToBeTraded , l_dummy_TTQChange_For_Buy)
                l_dummy_TTQChange_For_Buy -= lQtyForWhichWeTrade
                pTradeStats['totalBuyValueLong'] += lQtyForWhichWeTrade * (pObject.BidP + gTickSize)
                pTradeStats['currentPositionLong'] += lQtyForWhichWeTrade
                lReasonForTradingOrNotTradingLong = 'OpenBuy(Standing)'
                pReasonForTrade['OpenBuyTradeHappened'] += lQtyForWhichWeTrade
        #hitting
        else:
            if l_dummy_AskQ0 > 0 :

                lQtyToBeTraded = ( gMaxQty - pTradeStats['currentPositionLong'] )
                lQtyForWhichWeTrade = min( lQtyToBeTraded , l_dummy_AskQ0 )
                if pObject.AskP in g_quantity_adjustment_list_for_buy:
                    g_quantity_adjustment_list_for_buy[pObject.AskP] += lQtyForWhichWeTrade
                else:
                    g_quantity_adjustment_list_for_buy = {}
                    g_quantity_adjustment_list_for_buy[pObject.AskP] = lQtyForWhichWeTrade
                pTradeStats['totalBuyValueLong'] += lQtyForWhichWeTrade * (pObject.AskP)
                pTradeStats['currentPositionLong'] += lQtyForWhichWeTrade
                pReasonForTrade['OpenBuyTradeHappened'] += lQtyForWhichWeTrade
                l_dummy_AskQ0 -= lQtyForWhichWeTrade
                lReasonForTradingOrNotTradingLong = 'OpenBuy(Hitting)'
            else:
                lReasonForTradingOrNotTradingLong = "DummyAskQ0Exhausted"

    l_dummy_TTQChange_For_Sell = pObject.TTQChange
    #close sell
    if(pEnterTradeLong == -1): # Need to sell we come here only if currentPosition is greater than 0 so no need to check again.
        #standing
        if lSpread > gTickSize:        
            if(l_dummy_TTQChange_For_Sell <= 0 ):
                pReasonForTrade['VolumeDidNotIncreaseDuringSellAttemptLong'] += 1
                lReasonForTradingOrNotTradingLong = '(Spread>Pip)&&(NextTickTTQDidNotIncrease)'
            elif(pObject.NextLTP != pObject.AskP): 
                pReasonForTrade['LTPDoesNotEqualAskP0Long'] += 1
                lReasonForTradingOrNotTradingLong = '(Spread>Pip)&&(NextTickLTP!=Ask)'
            else:    

                lQtyTraded = min(  pTradeStats['currentPositionLong'] , l_dummy_TTQChange_For_Sell )
                pTradeStats['totalSellValueLong'] += lQtyTraded * (pObject.AskP - gTickSize)
                pTradeStats['currentPositionLong'] -= lQtyTraded
                l_dummy_TTQChange_For_Sell -= lQtyTraded
                lReasonForTradingOrNotTradingLong = 'CloseSell(Standing)'
                pReasonForTrade['CloseSellTradeHappened'] += lQtyTraded
        #hitting
        else:

            lQtyTraded = min( pTradeStats['currentPositionLong'] , l_dummy_BidQ0 )
            if pObject.BidP in g_quantity_adjustment_list_for_sell:
                g_quantity_adjustment_list_for_sell[pObject.BidP] += lQtyTraded
            else:
                g_quantity_adjustment_list_for_sell = {}
                g_quantity_adjustment_list_for_sell[pObject.BidP] = lQtyTraded
            pTradeStats['totalSellValueLong'] += lQtyTraded * (pObject.BidP)
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
        if lSpread > gTickSize:        
            if(l_dummy_TTQChange_For_Sell <= 0):
                pReasonForTrade['VolumeDidNotIncreaseDuringSellAttemptShort'] += 1
                lReasonForTradingOrNotTradingShort = '(Spread>Pip)&&(NextTickTTQDidNotIncrease)'
            elif(pObject.NextLTP != pObject.AskP):
                pReasonForTrade['LTPDoesNotEqualAskP0Short'] += 1
                lReasonForTradingOrNotTradingShort = '(Spread>Pip)&&(NextTickLTP!=Ask)'
            else:

                lQtyToBeTraded = ( gMaxQty - pTradeStats['currentPositionShort'] )
                lQtyForWhichWeTrade = min( lQtyToBeTraded , l_dummy_TTQChange_For_Sell)
                pTradeStats['totalSellValueShort'] += lQtyForWhichWeTrade * (pObject.AskP - gTickSize)
                pTradeStats['currentPositionShort'] += lQtyForWhichWeTrade
                l_dummy_TTQChange_For_Sell -= lQtyForWhichWeTrade
                lReasonForTradingOrNotTradingShort = 'OpenSell(Standing)'
                pReasonForTrade['OpenSellTradeHappened'] += lQtyForWhichWeTrade
        #hitting
        else:
            if l_dummy_BidQ0 > 0 :

                lQtyToBeTraded = ( gMaxQty - pTradeStats['currentPositionShort'] )
                lQtyForWhichWeTrade = min( lQtyToBeTraded , l_dummy_BidQ0 )
                if pObject.BidP in g_quantity_adjustment_list_for_sell:
                    g_quantity_adjustment_list_for_sell[pObject.BidP] += lQtyForWhichWeTrade
                else:
                    g_quantity_adjustment_list_for_sell = {}
                    g_quantity_adjustment_list_for_sell[pObject.BidP] = lQtyForWhichWeTrade
                pTradeStats['totalSellValueShort'] += lQtyForWhichWeTrade * (pObject.BidP)
                pTradeStats['currentPositionShort'] += lQtyForWhichWeTrade
                lReasonForTradingOrNotTradingShort = 'OpenSell(Hitting)'
                pReasonForTrade['OpenSellTradeHappened'] += lQtyForWhichWeTrade
                l_dummy_BidQ0 -= lQtyForWhichWeTrade
            else:
                lReasonForTradingOrNotTradingShort = 'DummyBidQZero'
    return lReasonForTradingOrNotTradingShort, lReasonForTradingOrNotTradingLong,l_dummy_BidQ0 , l_dummy_AskQ0 , l_dummy_TTQChange_For_Buy , l_dummy_TTQChange_For_Sell

def doTrade(pFileName, pEntryCL, pExitCL, pObjectList):
    enterTradeShort = 0
    enterTradeLong = 0
    tradeStats = dict()
    tradeStats['totalSellValueShort'] = 0
    tradeStats['totalBuyValueShort'] = 0
    tradeStats['currentPositionShort'] = 0
    tradeStats['totalSellValueLong'] = 0
    tradeStats['totalBuyValueLong'] = 0
    tradeStats['currentPositionLong'] = 0
    print (pEntryCL, pExitCL)
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
    print("Processing the data file for trades :")
    if args.pT.lower()=="yes":
        attribute.aList =  [[0 for x in xrange(4)] for x in xrange(len(pObjectList))]
    for lObject in pObjectList[:-1]:
         
        #short decisions
        if(lObject.currentSellPredictedValue > lObject.currentBuyPredictedValue):
            enterTradeShort = 1
            numberOfTimesAskedToEnterTradeShort += 1
        elif(lObject.currentBuyPredictedValue > lObject.currentSellPredictedValue and tradeStats['currentPositionShort'] > 0):
            numberOfTimesAskedToExitTradeShort += 1
            enterTradeShort = -1  # Implies to exit the trade
        else:
            enterTradeShort = 0  # Implies make no change
            
        #long decisions
        if(lObject.currentBuyPredictedValue > lObject.currentSellPredictedValue):
            enterTradeLong = 1
            numberOfTimesAskedToEnterTradeLong += 1
        elif(lObject.currentSellPredictedValue > lObject.currentBuyPredictedValue and tradeStats['currentPositionLong'] > 0):
            numberOfTimesAskedToExitTradeLong += 1
            enterTradeLong = -1  # Implies to exit the trade
        else:
            enterTradeLong = 0  # Implies make no change
        
        lReasonForTradingOrNotTradingShort, lReasonForTradingOrNotTradingLong, lDummyBidQ0 , lDummyAskQ0 , lDummyTTQForBuy , lDummyTTQForSell= checkIfDecisionToEnterOrExitTradeIsSuccessful(lObject, enterTradeShort,enterTradeLong,tradeStats,reasonForTrade,lReasonForTradingOrNotTradingLong,lReasonForTradingOrNotTradingShort )
        if args.pT.lower()=="yes":
            attribute.aList[currentIndex][0] = lObject.currentTimeStamp
            attribute.aList[currentIndex][1] = tradeStats['currentPositionLong']
            attribute.aList[currentIndex][2] = tradeStats['currentPositionShort']
            listOfStringsToPrint = [ str(lObject.BidQ) , str(lObject.BidP) , str(lObject.AskP) , \
                                    str(lObject.AskQ) , str(lObject.TTQ) , str(lObject.NextLTP) ,\
                                    str(lObject.currentSellPredictedValue) , str(enterTradeShort) ,lReasonForTradingOrNotTradingShort , str(lObject.currentBuyPredictedValue) ,\
                                    str(enterTradeLong) ,lReasonForTradingOrNotTradingLong , str(reasonForTrade['CloseBuyTradeHappened']),\
                                    str(reasonForTrade['OpenBuyTradeHappened']),str(reasonForTrade['OpenSellTradeHappened']),\
                                    str(reasonForTrade['CloseSellTradeHappened']),str(lDummyBidQ0),str(lDummyAskQ0),\
                                    str(lDummyTTQForBuy),str(lDummyTTQForSell)]
            attribute.aList[currentIndex][3] =  ";".join(listOfStringsToPrint)    
        currentIndex = currentIndex + 1
    
    lObject = pObjectList[-1]
    # Squaring off if some open position there   
    if tradeStats['currentPositionLong'] > 0:
        reasonForTrade['CloseSellTradeHappened'] += tradeStats['currentPositionLong']
        tradeStats['totalSellValueLong'] += tradeStats['currentPositionLong'] * (lObject.BidP)
        tradeStats['currentPositionLong'] = 0
        lReasonForTradingOrNotTradingLong = 'CloseSell(Hitting)'
    if tradeStats['currentPositionShort'] > 0:
        reasonForTrade['CloseBuyTradeHappened'] += tradeStats['currentPositionShort']
        tradeStats['totalBuyValueShort'] += tradeStats['currentPositionShort'] * (lObject.AskP)
        tradeStats['currentPositionShort'] = 0
        lReasonForTradingOrNotTradingLong = 'CloseBuy(Hitting)'

    dirName = args.pd.replace('/ro/','/rs/')
    
    if args.pT.lower()=="yes":
        attribute.aList[currentIndex][0] = lObject.currentTimeStamp
        attribute.aList[currentIndex][1] = tradeStats['currentPositionLong']
        attribute.aList[currentIndex][2] = tradeStats['currentPositionShort']
        listOfStringsToPrint = [ str(lObject.BidQ) , str(lObject.BidP) , str(lObject.AskP) , \
                                str(lObject.AskQ) , str(lObject.TTQ) , str(lObject.NextLTP) ,\
                                str(lObject.currentSellPredictedValue) , str(enterTradeShort) ,lReasonForTradingOrNotTradingShort , str(lObject.currentBuyPredictedValue) ,\
                                str(enterTradeLong) ,lReasonForTradingOrNotTradingLong , str(reasonForTrade['CloseBuyTradeHappened']),\
                                str(reasonForTrade['OpenBuyTradeHappened']),str(reasonForTrade['OpenSellTradeHappened']),\
                                str(reasonForTrade['CloseSellTradeHappened']),str(lDummyBidQ0),str(lDummyAskQ0),\
                                str(lDummyTTQForBuy),str(lDummyTTQForSell)]
        attribute.aList[currentIndex][3] =  ";".join(listOfStringsToPrint)        
     
        tradeLogMainDirName = dirName+"/t/"
        if not os.path.exists(tradeLogMainDirName):
            os.mkdir(tradeLogMainDirName)
        tradeLogSubDirectoryName =  tradeLogMainDirName + mainExperimentName+"/"
        if not os.path.exists(tradeLogSubDirectoryName):
            os.mkdir(tradeLogSubDirectoryName)
         
        fileName = pFileName.replace(".result",".trade").replace("/r/","/t/") 
        lHeaderColumnNamesList  = ['TimeStamp','CurrentPositionLong','CurrentPositionShort','BidQ0','BidP0','AskP0','AskQ0','TTQ','LTP','CurPredValueShort','EnterTradeShort','ReasonForTradingOrNotTradingShort','CurPredValueLong','EnterTradeLong','ReasonForTradingOrNotTradingLong','totalBuyTradeShort','totalBuyLong','totalSellShort','totalSellLong','DummyBidQ0','DummyAskQ0','DummyTTQChangeForSell','DummyTTQChangeForBuy']
        attribute.writeToFile(fileName , lHeaderColumnNamesList)
        
    tradeResultMainDirName = dirName+"/r/"
    if not os.path.exists(tradeResultMainDirName):
        os.mkdir(tradeResultMainDirName)
    tradeResultSubDirectoryName =  tradeResultMainDirName + mainExperimentName+"/"
    if not os.path.exists(tradeResultSubDirectoryName):
        os.mkdir(tradeResultSubDirectoryName)
    outputFile = open(pFileName,"w")
    
    gross_short_profit = tradeStats['totalSellValueShort'] - tradeStats['totalBuyValueShort']
    gross_long_profit = tradeStats['totalSellValueLong'] - tradeStats['totalBuyValueLong']
    gross_profit = gross_short_profit + gross_long_profit
    net_short_profit = gross_short_profit - ( transactionCost * ( tradeStats['totalSellValueShort'] +  tradeStats['totalBuyValueShort'] ) ) 
    net_long_profit = gross_long_profit - ( transactionCost * ( tradeStats['totalSellValueLong'] +  tradeStats['totalBuyValueLong'] ) )
    net_profit = net_short_profit + net_long_profit
    
    gross_short_profit_in_dollars = gross_profit / (currencyDivisor * 60)
    net_profit_in_dollars = net_profit / (currencyDivisor * 60 )
    #changed file write to modify it to Short Long version
    print("Starting to write: "+pFileName)
    print("The gross results for Short are: %.6f" %gross_short_profit, file = outputFile)
    print("The gross results for Long are: %.6f" %gross_long_profit, file = outputFile)
    print("Number of rows for which there is no prediction: " + str(0), file = outputFile)    
    print("Number of times asked to enter trade Short: " + str(numberOfTimesAskedToEnterTradeShort), file = outputFile)    
    print("Number of times asked to enter trade Long: " + str(numberOfTimesAskedToEnterTradeLong), file = outputFile)    
    print("Number of times asked to exit trade Short: " + str(numberOfTimesAskedToExitTradeShort), file = outputFile)
    print("Number of times asked to exit trade Long: " + str(numberOfTimesAskedToExitTradeLong), file = outputFile)
    print("The net results for Short are: %.6f" %net_short_profit, file = outputFile)
    print("The net results for Long are: %.6f" %net_long_profit, file = outputFile)
    print("Gross Results in Dollars: %.6f" %gross_short_profit_in_dollars, file = outputFile)
    print("Net Results in Dollars: %.6f" %net_profit_in_dollars, file = outputFile)
    print("Number of times Close buy trade happened: " + str(reasonForTrade['CloseBuyTradeHappened']), file = outputFile)
    print("Number of times open buy trade happened: " + str(reasonForTrade['OpenBuyTradeHappened']), file = outputFile)
    print("Assumed open sell trade did not happen since volume did not increase: " + str(reasonForTrade['VolumeDidNotIncreaseDuringSellAttemptShort']), file = outputFile)
    print("Assumed close sell trade did not happen since volume did not increase: " + str(reasonForTrade['VolumeDidNotIncreaseDuringSellAttemptLong']), file = outputFile)
    print("Assumed open sell trade did not happen since bidP0 not same as LTP: " + str(reasonForTrade['LTPDoesNotEqualAskP0Short']), file = outputFile)
    print("Assumed close sell trade did not happen since bidP0 not same as LTP: " + str(reasonForTrade['LTPDoesNotEqualAskP0Long']), file = outputFile)
    print("Number of Open sell trade happened: " + str(reasonForTrade['OpenSellTradeHappened']), file = outputFile)
    print("Number of Close sell trade happened: " + str(reasonForTrade['CloseSellTradeHappened']), file = outputFile)
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


if __name__ == "__main__":
    tStart = datetime.now()
    dirName = args.pd.replace('/ro/','/rs/')
    checkAllFilesAreExistOrNot = 'false'
    
    lWFDirName = args.pd.replace('/ro/','/wf/')
    if args.double:
        predictedBuyValuesFileName = lWFDirName+"/p/"+mainExperimentName+"/"+args.a + 'buy' + '-td.' + os.path.basename(os.path.abspath(args.td)) + '-dt.' + \
        args.dt + '-targetClass.' + args.targetClass + '-f.' + experimentName + "-wt." + args.wt+ attribute.generateExtension() + "double.predictions"
        
        predictedSellValuesFileName = lWFDirName+"/p/"+mainExperimentName+"/"+args.a + 'sell' + '-td.' + os.path.basename(os.path.abspath(args.td)) + '-dt.' +\
        args.dt + '-targetClass.' + args.targetClass + '-f.' + experimentName + "-wt." + args.wt+ attribute.generateExtension() + "double.predictions"
    else:
        predictedBuyValuesFileName = lWFDirName+"/p/"+mainExperimentName+"/"+args.a + 'buy' + '-td.' + os.path.basename(os.path.abspath(args.td)) + '-dt.' + \
        args.dt + '-targetClass.' + args.targetClass + '-f.' + experimentName + "-wt." + args.wt+ attribute.generateExtension() + ".predictions"
        
        predictedSellValuesFileName = lWFDirName+"/p/"+mainExperimentName+"/"+args.a + 'sell' + '-td.' + os.path.basename(os.path.abspath(args.td)) + '-dt.' +\
        args.dt + '-targetClass.' + args.targetClass + '-f.' + experimentName + "-wt." + args.wt+ attribute.generateExtension() + ".predictions"        

    lEntryClList = args.entryCL.split(";")
    lExitClList = args.exitCL.split(";")
    if len(lEntryClList)!= len(lExitClList):
        print("Len of entry and exit list does match. Entry List length = " , len(lEntryClList) , " and ExitCL List length = " , len(lExitClList))
        os._exit(-1)
    lengthOfList = len(lEntryClList)
    
    lMinOfExitCl = 9999.000
    fileNameList = []
    finalEntryClList = []
    finalExitClList = []
    lengthOfFinalList = 0
    for indexOfCL in range(lengthOfList):
        if args.double:
            lInitialFileName = args.a + '-td.' + os.path.basename(os.path.abspath(args.td)) + \
                           '-dt.' + args.dt + '-targetClass.' + args.targetClass + '-f.' + experimentName + "-wt." + args.wt+ attribute.generateExtension() + \
                           '-l.'+lEntryClList[indexOfCL]+"-"+lExitClList[indexOfCL] + "-tq." + args.orderQty + "-te.7double" 
        else:
            lInitialFileName = args.a + '-td.' + os.path.basename(os.path.abspath(args.td)) + \
                           '-dt.' + args.dt + '-targetClass.' + args.targetClass + '-f.' + experimentName + "-wt." + args.wt+ attribute.generateExtension() + \
                           '-l.'+lEntryClList[indexOfCL]+"-"+lExitClList[indexOfCL] + "-tq." + args.orderQty + "-te.7" 
        fileName = dirName + "/r/" + mainExperimentName + "/" + lInitialFileName+".result"
        if os.path.isfile(fileName) and args.skipT.lower() == "yes":
            print("Trade results file " + fileName + "Already exist. Not regenerating it. If you want to rerun it by making -skipT = no ")
        else: 
            checkAllFilesAreExistOrNot = 'true'
            print("Trade results file " + fileName + " Does not exist.")
            fileNameList.append(fileName)
            lEntryCL = float("." + lEntryClList[indexOfCL])
            lExitCL = float("." + lExitClList[indexOfCL])
            if lExitCL < lMinOfExitCl :
                lMinOfExitCl = lExitCL
            finalEntryClList.append(lEntryCL)
            finalExitClList.append(lExitCL)
            lengthOfFinalList = lengthOfFinalList + 1

    print("Number of File to be run for ",lengthOfFinalList)
    if checkAllFilesAreExistOrNot == 'true':
        if os.path.isfile(predictedBuyValuesFileName) and os.path.isfile(predictedSellValuesFileName):
            print ("\nRunning the simulated trading program")
            g_quantity_adjustment_list_for_sell = {}
            g_quantity_adjustment_list_for_buy = {}

            dataFileName = dataFile.getFileNameFromCommandLineParam(args.pd)
            
            dataFileObject =  open(dataFileName,"r")
            buyPredictFileObject = open(predictedBuyValuesFileName,"r")
            sellPredictFileObject = open(predictedSellValuesFileName,"r")
            
            print("Data file Used :- " ,dataFileName)
            print("Buy Predict file Used :- ",predictedBuyValuesFileName)
            print("Sell Predict file used :- ", predictedSellValuesFileName)
            lObjectList = getDataFileAndPredictionsIntoObjectList(dataFileObject,buyPredictFileObject,sellPredictFileObject,lMinOfExitCl)
            
            print("Length of list formed " , len(lObjectList) , " Min of predictions taken :- ", lMinOfExitCl)
            tEnd = datetime.now()
            print("Time taken to read data and prediction file is " + str(tEnd - tStart))
            
            for lIndexOfFiles in range(lengthOfFinalList):
                doTrade(fileNameList[lIndexOfFiles], finalEntryClList[lIndexOfFiles], finalExitClList[lIndexOfFiles], lObjectList)
#                 if args.pT.lower() == "yes":
#                     print("Need to print logs")
            
            tEnd = datetime.now()
            print("Time taken to for complete run " + str(tEnd - tStart))
        else:
            print (predictedBuyValuesFileName,predictedSellValuesFileName)
            print ("Prediction files not yet generated")


