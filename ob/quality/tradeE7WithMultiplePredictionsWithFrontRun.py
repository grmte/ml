#!/usr/bin/python
from __future__ import division
from __future__ import print_function
import os, sys, argparse
from configobj import ConfigObj
import pdb
from itertools import islice
from math import exp
parser = argparse.ArgumentParser(description='This program will do trades to measure the quality of the experiment.\n\
 An e.g. command line is tradeE5.py -d ob/data/20140207/ -e ob/e/1 -a logitr -entryCL 0.90 -exitCL .55 -orderQty 500', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-e', required=True,help='Directory of the experiment or sub experiment e/10/s/3c/ABC')
parser.add_argument('-e1', required=True,help='Directory of the experiment Best')
parser.add_argument('-a', required=True,help='Algorithm name')
parser.add_argument('-entryCL', required=True,help='Percentage of the confidence level used to enter the trades')
parser.add_argument('-exitCL', required=True,help='Percentage of the confidence level used to exit the trades')
parser.add_argument('-entryCL2', required=True,help='Percentage of the confidence level used to cancel the opening trades')
parser.add_argument('-exitCL2', required=True,help='Percentage of the confidence level used to cancel the closing trades')
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
args = parser.parse_args()
sys.path.append("./src/")
sys.path.append("./ob/generators/")
import dataFile, colNumberOfData, common
import attribute
attribute.initializeInstDetails(args.iT,args.sP,args.oT)
if args.skipT == None:
    args.skipT = "no"
if args.targetClass == None:
    args.targetClass = "binomial"
if args.wt == None:
    args.wt = "default"
        
absPathOfExperimentName = os.path.abspath(args.e)
absPathOfExperimentNameBest = os.path.abspath(args.e1)
if 'nsecur' in absPathOfExperimentName:
    pathAfterE = absPathOfExperimentName[absPathOfExperimentName.index("/nsecur/")+8:]
    if args.t ==None:
        transactionCost = 0.000015
    else:
        transactionCost = float(args.t)
    currencyDivisor = 10000
elif 'nsefut' in absPathOfExperimentName:
    pathAfterE = absPathOfExperimentName[absPathOfExperimentName.index("/nsefut/")+8:]
    pathAfterEBest = absPathOfExperimentNameBest[absPathOfExperimentNameBest.index("/nsefut/")+8:]
    if args.t ==None:
        transactionCost = 0.00015
    else:
        transactionCost = float(args.t)
    currencyDivisor = 1000
elif 'nseopt' in absPathOfExperimentName:
    pathAfterE = absPathOfExperimentName[absPathOfExperimentName.index("/nseopt/")+8:]
    transactionCost = args.t
    currencyDivisor = 0
    print("Please specify the transaction cost and currency divisor for options and remove os.exit(-1) and rerun it")
    os._exit(-1)
        
if "/" in pathAfterE:
    mainExperimentName = pathAfterE[:pathAfterE.index("/")]
    mainExperimentNameBest = pathAfterEBest[:pathAfterEBest.index("/")]
else:
    mainExperimentName = pathAfterE
    mainExperimentNameBest = pathAfterEBest

experimentName = os.path.basename(absPathOfExperimentName)
experimentNameBest =  os.path.basename(absPathOfExperimentNameBest)
gTickSize = int(args.tickSize)
gMaxQty = int(args.orderQty)

gEntryCLList = args.entryCL.split(";")
gExitCLList = args.exitCL.split(";")
gExitCL2List = args.exitCL2.split(";")
gEntryCL2List = args.entryCL2.split(";")

gStandingAtAskPMinusOneTickInCloseSell = 0
gStandingAtBidPPlusOneTickInCloseBuy = 0
gStandingAtAskPMinusOneTickInOpenSell = 0
gStandingAtBidPPlusOneTickInOpenBuy = 0

gNoOfLineReadPerChunk = 10000

gOpenBuyFillPrice = 0
gOpenSellFillPrice = 0

initialFileName = []
for indexOfCL in range(0,len(gEntryCLList)):
    lInitialFileName = args.a + '-td.' + os.path.basename(os.path.abspath(args.td)) + \
                   '-dt.' + args.dt + '-targetClass.' + args.targetClass + '-f.' + experimentName + "-wt." + args.wt+ attribute.generateExtension() + \
                   '-l.'+gEntryCLList[indexOfCL]+"-"+gExitCLList[indexOfCL] + "-" +gEntryCL2List[indexOfCL]+"-"+gExitCL2List[indexOfCL] + "-tq." + args.orderQty + "-te.7WithMultiPredFrontRun"

    initialFileName.append(lInitialFileName)
    
g_quantity_adjustment_list_for_sell = {}
g_quantity_adjustment_list_for_buy = {}
g_bestqty_list_for_close_sell = {}
g_bestqty_list_for_close_buy = {}
g_bestqty_list_for_open_sell = {}
g_bestqty_list_for_open_buy = {}
class Tick():
    def __init__(self,pCurrentDataRowTimeStamp,pBuyProb1,pSellProb1,pBuyProb2,pSellProb2):
                 
        self.AskP = [0.0,0.0]
        self.AskQ = [0,0]
        self.BidP = [0.0,0.0]
        self.BidQ = [0,0]
        
        self.LTP = 0
        self.TTQ  = 0
        self.TTQChange = 0 
        self.NextLTP = 0
        self.currentTimeStamp = pCurrentDataRowTimeStamp
        self.currentBuyPredictedValue1 = pBuyProb1
        self.currentSellPredictedValue1 = pSellProb1
        self.currentBuyPredictedValue2 = pBuyProb2
        self.currentSellPredictedValue2 = pSellProb2        
        self.OpenBuy = 0
        self.OpenSell = 0
        self.CloseBuy = 0
        self.CloseSell = 0
        self.CloseBuyTradeHappened= 0
        self.OpenBuyTradeHappened = 0
        self.OpenSellTradeHappened = 0
        self.CloseSellTradeHappened= 0
        self.ReasonForTradingOrNotTradingOpenSell = ""
        self.ReasonForTradingOrNotTradingCloseBuy = ""
        self.ReasonForTradingOrNotTradingOpenBuy = ""
        self.ReasonForTradingOrNotTradingCloseSell = ""
                
def getPredictionsIntoObjectList(dataFileObject,buyPredictFileObjectBest,sellPredictFileObjectBest,buyPredictFileObject,sellPredictFileObject):
    global gNoOfLineReadPerChunk,gTickSize
    lObjectList = []
    lCurrentDataRowCount = 0
    lPrevObj = None
    fileHasHeader = 1
    headerSkipped = 0
    featureFileSep = ";"
    dataFileSep = ";"
    predictFileSep = ","
    lListOfBidP = []
    lListOfAskP = []
    l_data_row_list =  list(islice(dataFileObject,gNoOfLineReadPerChunk))
#    import pdb
#    pdb.set_trace()
    while True:
        lDataFileRowsList = list(islice(dataFileObject,gNoOfLineReadPerChunk))
        lBuyPredictedFileRowList = list(islice(buyPredictFileObject,gNoOfLineReadPerChunk))
        lSellPredictedFileRowList = list(islice( sellPredictFileObject,gNoOfLineReadPerChunk ))
        lBuyPredictedFileRowListBest = list(islice(buyPredictFileObjectBest,gNoOfLineReadPerChunk))
        lSellPredictedFileRowListBest = list(islice( sellPredictFileObjectBest,gNoOfLineReadPerChunk ))
        if not lDataFileRowsList :
            print("Finished reading file")
            lObjectList.append(lPrevObj)    
            lPrevObj = None          
            break
        lengthOfDataList = len(lDataFileRowsList)
        lengthOfBuyPredList = len(lBuyPredictedFileRowList)
        lengthOfSellPredList = len(lSellPredictedFileRowList)
        lengthOfBuyPredListBest = len(lBuyPredictedFileRowListBest)
        lengthOfSellPredListBest = len(lSellPredictedFileRowListBest)
        if lengthOfDataList!=lengthOfBuyPredList or lengthOfBuyPredList!=lengthOfSellPredList or lengthOfBuyPredListBest!=lengthOfSellPredListBest or lengthOfBuyPredListBest!=lengthOfSellPredList:
            print("Length of data file and predicted buy and sell values file are not same ", lengthOfDataList,lengthOfBuyPredList,lengthOfSellPredList,lengthOfBuyPredListBest,lengthOfSellPredListBest)
            os._exit(-1)                
        for currentRowIndex in range(lengthOfDataList):
            if(fileHasHeader == 1 and headerSkipped != 1):
                headerSkipped =1
                continue
            lDataRow = lDataFileRowsList[currentRowIndex].rstrip().split(dataFileSep)
            lCurrentDataRowTimeStamp = common.convertTimeStampFromStringToFloat(lDataRow[colNumberOfData.TimeStamp])
            lBuyPredictedRow = lBuyPredictedFileRowList[currentRowIndex].rstrip().split(predictFileSep)
            lBuyPredictedTimeStamp = float(lBuyPredictedRow[1])
            lBuyPredictedValue = float(lBuyPredictedRow[2])
            lSellPredictedRow = lSellPredictedFileRowList[currentRowIndex].rstrip().split(predictFileSep)
            lSellPredictedTimeStamp = float(lSellPredictedRow[1])
            lSellPredictedValue = float(lSellPredictedRow[2])
            
            lBuyPredictedRowBest = lBuyPredictedFileRowListBest[currentRowIndex].rstrip().split(predictFileSep)
            lBuyPredictedTimeStampBest = float(lBuyPredictedRowBest[1])
            lBuyPredictedValueBest = float(lBuyPredictedRowBest[2])
            lSellPredictedRowBest = lSellPredictedFileRowListBest[currentRowIndex].rstrip().split(predictFileSep)
            lSellPredictedTimeStampBest = float(lSellPredictedRowBest[1])
            lSellPredictedValueBest = float(lSellPredictedRowBest[2])
            if( lCurrentDataRowTimeStamp != lBuyPredictedTimeStamp or lBuyPredictedTimeStamp!=lSellPredictedTimeStamp or lBuyPredictedTimeStampBest!=lSellPredictedTimeStampBest or lBuyPredictedTimeStampBest!=lSellPredictedTimeStamp  ):
                lDataRow = lDataFileRowsList[currentRowIndex].rstrip().split(dataFileSep)
                print('Time stamp of data row with predicted value is not matching .\n Data row time stamp :- ' , lCurrentDataRowTimeStamp,'BuyPredicted Time Stamp :- ' , lBuyPredictedTimeStamp\
                      ,"SellPredicted Time Stamp :- ",lSellPredictedTimeStamp)
                os._exit(-1)
            lObj = Tick(lCurrentDataRowTimeStamp,lBuyPredictedValueBest,lSellPredictedValueBest,lBuyPredictedValue,lSellPredictedValue)
            #print(lObj.currentBuyPredictedValue2,lObj.currentSellPredictedValue2)
            if lPrevObj!=None:
                lPrevObj.TTQChange  = lObj.TTQ - lPrevObj.TTQ
                lPrevObj.NextLTP = lObj.LTP
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
    

def checkIfPreviousDecisionToEnterOrExitTradeWasSuccessful(pCurrentObj,pPrevObj , pTradeStats):
    global gTickSize , gMaxQty , g_quantity_adjustment_list_for_sell , g_quantity_adjustment_list_for_buy
#    global gStandingAtAskPMinusOneTickInCloseSell ,gStandingAtBidPPlusOneTickInCloseBuy ,gStandingAtAskPMinusOneTickInOpenSell ,gStandingAtBidPPlusOneTickInOpenBuy, gOpenBuyFillPrice , gOpenSellFillPrice , gPipsTaken
    
    lOpenBuyTradedPrice = 0 
    lOpenBuyTradedQty = 0
    lOpenSellTradedPrice = 0
    lOpenSellTradedQty = 0
    lCloseBuyTradedPrice = 0 
    lCloseBuyTradedQty = 0
    lCloseSellTradedPrice = 0
    lCloseSellTradedQty = 0
    lReasonForTradingOrNotTradingOpenSell = ""
    lReasonForTradingOrNotTradingOpenBuy = ""
    lReasonForTradingOrNotTradingCloseSell = ""
    lReasonForTradingOrNotTradingCloseBuy = ""

    
    if pPrevObj.BidP[0] in g_quantity_adjustment_list_for_sell:
        pPrevObj.BidQ[0] = max( 0 , pPrevObj.BidQ[0] - g_quantity_adjustment_list_for_sell[pPrevObj.BidP[0]])
    else:
        g_quantity_adjustment_list_for_sell = {}

    if pPrevObj.AskP[0] in g_quantity_adjustment_list_for_buy:
        pPrevObj.AskQ[0] = max( 0 ,pPrevObj.AskQ[0] - g_quantity_adjustment_list_for_buy[pPrevObj.AskP[0]])
    else:
        g_quantity_adjustment_list_for_buy = {}    
        
    if(pPrevObj.OpenBuy == 0 and pPrevObj.CloseBuy == 0 and pPrevObj.OpenSell == 0 and pPrevObj.CloseSell == 0):
        return [ pPrevObj.BidQ[0] , pPrevObj.AskQ[0] , 0 , 0 , 0 ,0 ,0, 0,0 ,0 ,0, 0]

#    if(pPrevObj.OpenBuy)

    if(pPrevObj.OpenSell > 0):
        if pTradeStats['openSellPrice'] < pPrevObj.AskP[0] - gTickSize :
            pTradeStats['openSellPrice'] = pPrevObj.AskP[0] - gTickSize
    if(pPrevObj.CloseSell < 0):
        if pTradeStats['closeSellPrice'] < pPrevObj.AskP[0] - gTickSize:
            pTradeStats['closeSellPrice'] = pPrevObj.AskP[0] - gTickSize
    if(pPrevObj.OpenBuy > 0):
        if pTradeStats['openBuyPrice'] > pPrevObj.BidP[0] + gTickSize:
            pTradeStats['openBuyPrice'] = pPrevObj.BidP[0] + gTickSize
    if(pPrevObj.CloseBuy < 0):
        if pTradeStats['closeBuyPrice'] > pPrevObj.BidP[0] + gTickSize:
            pTradeStats['closeBuyPrice'] = pPrevObj.BidP[0] + gTickSize

    currentLTP = pCurrentObj.LTP
    currentTTQ = pCurrentObj.TTQ    

    l_dummy_AskQ0 = pPrevObj.AskQ[0]
    l_dummy_TTQChange_For_Buy = currentTTQ - pPrevObj.TTQ
    lSpread = pPrevObj.AskP[0] - pPrevObj.BidP[0]
    #close buy
    if(pPrevObj.CloseBuy < 0 or pTradeStats['closeBuyFrontP'] <> 0): # Need to buy we come here only if currentPosition is greater than 0 so no need to check again.
        #standing
        if pTradeStats['closeBuyFrontP'] <> 0:
            pTradeStats['closeBuyPrice'] = pTradeStats['closeBuyFrontP']
            pTradeStats['closeBuyQty'] = pTradeStats['closeBuyFrontQ']
            
        if lSpread > gTickSize:
            if(l_dummy_TTQChange_For_Buy<=pTradeStats["closeBuyQty"]):
                lReasonForTradingOrNotTradingCloseBuy = '(Spread>Pip)&&(NextTickTTQDidNotIncrease)'
            elif(currentLTP > pTradeStats['closeBuyPrice']): 
                lReasonForTradingOrNotTradingCloseBuy = '(Spread>Pip)&&(LTP!=Bid)'
            else:
                l_dummy_TTQChange_For_Buy -= pTradeStats["closeBuyQty"]
                lQtyTraded = min(  pTradeStats['currentPositionShort'] , l_dummy_TTQChange_For_Buy )
                l_dummy_TTQChange_For_Buy -= lQtyTraded
                pTradeStats['totalBuyAmountShort'] += lQtyTraded * (pTradeStats['closeBuyPrice'])
                pTradeStats['currentPositionShort'] -= lQtyTraded
                lReasonForTradingOrNotTradingCloseBuy = 'CloseBuy(Standing)'
                pTradeStats['NumberOfCloseBuy'] += lQtyTraded
                lCloseBuyTradedQty = lQtyTraded
                lCloseBuyTradedPrice = pTradeStats['closeBuyPrice']
        #hitting
        elif pPrevObj.AskP[0] <= pTradeStats['closeBuyPrice']:
            l_buy_qty = min( pTradeStats['currentPositionShort'], l_dummy_AskQ0)
            if pPrevObj.AskP[0] in g_quantity_adjustment_list_for_buy:
                    g_quantity_adjustment_list_for_buy[pPrevObj.AskP[0]] += l_buy_qty
            else:  
                    g_quantity_adjustment_list_for_buy = {} 
                    g_quantity_adjustment_list_for_buy[pPrevObj.AskP[0]] = l_buy_qty
            l_dummy_AskQ0 -= l_buy_qty
            pTradeStats['totalBuyAmountShort'] += l_buy_qty * (pTradeStats['closeBuyPrice'])
            pTradeStats['currentPositionShort'] -= l_buy_qty
            pTradeStats['NumberOfCloseBuy'] += l_buy_qty
            lCloseBuyTradedQty = l_buy_qty
            lCloseBuyTradedPrice = pTradeStats['closeBuyPrice']
             
            if l_buy_qty > 0:
                lReasonForTradingOrNotTradingCloseBuy = 'CloseBuy(Hitting)'
            else :
                lReasonForTradingOrNotTradingCloseBuy = "DummyAskQExhuasted"
                
        if pTradeStats['closeBuyFrontP'] <> 0:
            pTradeStats['closeBuyPrice'] = 0
            pTradeStats['closeBuyQty'] = 0
        
    
#     if(pPrevObj.CloseBuy < 0 ): # Need to buy we come here only if currentPosition is greater than 0 so no need to check again.
#         lCloseBuyTradedPrice = 0
#         lCloseBuyTradedQty = 0
#         lQtyForWhichFillsCanBeGiven = pTradeStats['currentPositionShort']
#         lOpenOrCloseSide = 'Close'
#         lPriceAtWhichOrderIsToBeKept = 0
#         if pPrevObj.CloseBuy == -2 :  
#             lPriceAtWhichOrderIsToBeKept = pPrevObj.BidP[1] + ( 1 * gTickSize) 
#         elif pPrevObj.CloseBuy == -1:
#             lPriceAtWhichOrderIsToBeKept = pPrevObj.BidP[0] + ( 1 * gTickSize) 
#         if  ( lPriceAtWhichOrderIsToBeKept == pPrevObj.BidP[0] + ( 1 * gTickSize) ) or pPrevObj.CloseBuy == -1:
#             g_bestqty_list_for_close_buy = {}
#             l_dummy_TTQChange_For_Buy, l_dummy_AskQ0 , lReasonForTradingOrNotTradingCloseBuy, lCloseBuyTradedQty,lCloseBuyTradedPrice = fillForStandingAtBidPlus1Pip(pPrevObj, l_dummy_AskQ0,spreadAtTimeOfPreviousDataRow,\
#                                                                                                                              currentLTP, l_dummy_TTQChange_For_Buy , lQtyForWhichFillsCanBeGiven,lOpenOrCloseSide)
#             gStandingAtBidPPlusOneTickInCloseBuy  = pPrevObj.BidP[0] + gTickSize 
#         else:  #Standing at Bid
#             l_dummy_TTQChange_For_Buy, lReasonForTradingOrNotTradingCloseBuy, lCloseBuyTradedQty,lCloseBuyTradedPrice = fillForStandingAtBidForCloseBuy(pPrevObj, currentLTP, l_dummy_TTQChange_For_Buy , lQtyForWhichFillsCanBeGiven , lOpenOrCloseSide , lPriceAtWhichOrderIsToBeKept)
#             gStandingAtBidPPlusOneTickInCloseBuy = 0
#         
#         pTradeStats['totalBuyAmountShort'] += lCloseBuyTradedQty * lCloseBuyTradedPrice
#         pTradeStats['currentPositionShort'] -= lCloseBuyTradedQty
#         pTradeStats['NumberOfCloseBuy'] += lCloseBuyTradedQty
#     else:
#         gStandingAtBidPPlusOneTickInCloseBuy  = 0
    if(pPrevObj.OpenBuy > 0 and ( gMaxQty - pTradeStats['currentPositionLong'] ) > 0): # Need to buy
        #standing
        if pTradeStats['openBuyFrontP'] <> 0:
            pTradeStats['openBuyPrice'] = pTradeStats['openBuyFrontP']
            pTradeStats['openBuyQty'] = pTradeStats['openBuyFrontQ']
        
        if lSpread > gTickSize:
            if(l_dummy_TTQChange_For_Buy <= pTradeStats["openBuyQty"] ):
                lReasonForTradingOrNotTradingOpenBuy = '(Spread>Pip)&&(NextTickTTQDidNotIncrease)'
            elif(currentLTP > pTradeStats['openBuyPrice']):
                lReasonForTradingOrNotTradingOpenBuy = '(Spread>Pip)&&(LTPDoesNotEqualBidP0Long)'
            else:
                l_dummy_TTQChange_For_Buy -= pTradeStats["openBuyQty"]
                lQtyToBeTraded = ( gMaxQty - pTradeStats['currentPositionLong'] )
                lQtyForWhichWeTrade = min( lQtyToBeTraded , l_dummy_TTQChange_For_Buy)
                l_dummy_TTQChange_For_Buy -= lQtyForWhichWeTrade
                pTradeStats['totalBuyAmountLong'] += lQtyForWhichWeTrade * (pTradeStats['openBuyPrice'])
                pTradeStats['currentPositionLong'] += lQtyForWhichWeTrade
                lReasonForTradingOrNotTradingOpenBuy = 'OpenBuy(Standing)'
                pTradeStats['NumberOfOpenBuy'] += lQtyForWhichWeTrade
                lOpenBuyTradedQty = lQtyForWhichWeTrade
                lOpenBuyTradedPrice = pTradeStats['openBuyPrice']
        #hitting
        elif pPrevObj.AskP[0] <= pTradeStats['openBuyPrice'] :
            if l_dummy_AskQ0 > 0 :

                lQtyToBeTraded = ( gMaxQty - pTradeStats['currentPositionLong'] )
                lQtyForWhichWeTrade = min( lQtyToBeTraded , l_dummy_AskQ0 )
                if pPrevObj.AskP[0] in g_quantity_adjustment_list_for_buy:
                    g_quantity_adjustment_list_for_buy[pPrevObj.AskP[0]] += lQtyForWhichWeTrade
                else:
                    g_quantity_adjustment_list_for_buy = {}
                    g_quantity_adjustment_list_for_buy[pPrevObj.AskP[0]] = lQtyForWhichWeTrade
                pTradeStats['totalBuyAmountLong'] += lQtyForWhichWeTrade * (pTradeStats['openBuyPrice'])
                pTradeStats['currentPositionLong'] += lQtyForWhichWeTrade
                pTradeStats['NumberOfOpenBuy'] += lQtyForWhichWeTrade
                l_dummy_AskQ0 -= lQtyForWhichWeTrade
                lReasonForTradingOrNotTradingOpenBuy = 'OpenBuy(Hitting)'
                lOpenBuyTradedQty = lQtyForWhichWeTrade
                lOpenBuyTradedPrice = pTradeStats['openBuyPrice']
            else:
                lReasonForTradingOrNotTradingOpenBuy = "DummyAskQ0Exhausted"

        if pTradeStats['openBuyFrontP'] <> 0:
            pTradeStats['openBuyPrice'] = 0
            pTradeStats['openBuyQty'] = 0
    
    #open buy
#     if(pPrevObj.OpenBuy > 0 and ( gMaxQty - pTradeStats['currentPositionLong'] ) > 0):
#         lOpenBuyTradedPrice = 0
#         lOpenBuyTradedQty = 0
#         lQtyForWhichFillsCanBeGiven = gMaxQty - pTradeStats['currentPositionLong'] 
#         lOpenOrCloseSide = 'Open'
#         lPriceAtWhichOrderIsToBeKept = 0
#         if pPrevObj.OpenBuy == 2:
#             lPriceAtWhichOrderIsToBeKept = pPrevObj.BidP[1] + ( 1 * gTickSize) 
#         elif pPrevObj.OpenBuy == 1:
#             lPriceAtWhichOrderIsToBeKept = pPrevObj.BidP[0] + ( 1 * gTickSize) 
#         if  ( lPriceAtWhichOrderIsToBeKept == pPrevObj.BidP[0] + ( 1 * gTickSize) ) or pPrevObj.OpenBuy == 1:
#             g_bestqty_list_for_open_buy = {}
#             l_dummy_TTQChange_For_Buy, l_dummy_AskQ0 , lReasonForTradingOrNotTradingOpenBuy, lOpenBuyTradedQty,lOpenBuyTradedPrice = fillForStandingAtBidPlus1Pip(pPrevObj, l_dummy_AskQ0,spreadAtTimeOfPreviousDataRow,\
#                                                                                                                      currentLTP, l_dummy_TTQChange_For_Buy , lQtyForWhichFillsCanBeGiven,lOpenOrCloseSide)
#             gStandingAtBidPPlusOneTickInOpenBuy  = pPrevObj.BidP[0] + gTickSize 
#         else:  #Standing at Bid
#             l_dummy_TTQChange_For_Buy, lReasonForTradingOrNotTradingOpenBuy, lOpenBuyTradedQty,lOpenBuyTradedPrice = fillForStandingAtBidForOpenBuy(pPrevObj, currentLTP, l_dummy_TTQChange_For_Buy , lQtyForWhichFillsCanBeGiven , lOpenOrCloseSide , lPriceAtWhichOrderIsToBeKept)
#             gStandingAtBidPPlusOneTickInOpenBuy = 0
#                         
#         pTradeStats['totalBuyAmountLong'] += lOpenBuyTradedQty * lOpenBuyTradedPrice
#         pTradeStats['currentPositionLong'] += lOpenBuyTradedQty
#         pTradeStats['NumberOfOpenBuy'] += lOpenBuyTradedQty
#     else:
#         gStandingAtBidPPlusOneTickInOpenBuy = 0
#     
    l_dummy_BidQ0 = pPrevObj.BidQ[0]
    l_dummy_TTQChange_For_Sell = currentTTQ - pPrevObj.TTQ

    if(pPrevObj.CloseSell < 0): # Need to sell we come here only if currentPosition is greater than 0 so no need to check again.
        #standing
        if pTradeStats['closeSellFrontP'] <> 0:
            pTradeStats['closeSellPrice'] = pTradeStats['closeSellFrontP']
            pTradeStats['closeSellQty'] = pTradeStats['closeSellFrontQ']
            
        if lSpread > gTickSize:        
            if(l_dummy_TTQChange_For_Sell <= pTradeStats["closeSellQty"] ):
                lReasonForTradingOrNotTradingCloseSell = '(Spread>Pip)&&(NextTickTTQDidNotIncrease)'
            elif(currentLTP < pTradeStats['closeSellPrice']): 
                lReasonForTradingOrNotTradingCloseSell = '(Spread>Pip)&&(NextTickLTP!=Ask)'
            else:
                l_dummy_TTQChange_For_Sell -= pTradeStats["closeSellQty"]
                lQtyTraded = min(  pTradeStats['currentPositionLong'] , l_dummy_TTQChange_For_Sell )
                pTradeStats['totalSellAmountLong'] += lQtyTraded * (pTradeStats['closeSellPrice'])
                pTradeStats['currentPositionLong'] -= lQtyTraded
                l_dummy_TTQChange_For_Sell -= lQtyTraded
                lReasonForTradingOrNotTradingCloseSell = 'CloseSell(Standing)'
                pTradeStats['NumberOfCloseSell'] += lQtyTraded
                lCloseSellTradedPrice = pTradeStats['closeSellPrice']
                lCloseSellTradedQty = lQtyTraded
        #hitting
        elif pPrevObj.BidP[0] >= pTradeStats['closeSellPrice']:
            lQtyTraded = min( pTradeStats['currentPositionLong'] , l_dummy_BidQ0 )
            if pPrevObj.BidP[0] in g_quantity_adjustment_list_for_sell:
                g_quantity_adjustment_list_for_sell[pPrevObj.BidP[0]] += lQtyTraded
            else:
                g_quantity_adjustment_list_for_sell = {}
                g_quantity_adjustment_list_for_sell[pPrevObj.BidP[0]] = lQtyTraded
            pTradeStats['totalSellAmountLong'] += lQtyTraded * (pTradeStats['closeSellPrice'])
            pTradeStats['currentPositionLong'] -= lQtyTraded
            l_dummy_BidQ0 -= lQtyTraded
            
            if lQtyTraded > 0 :
                lReasonForTradingOrNotTradingCloseSell = 'CloseSell(Hitting)'
                lCloseSellTradedPrice = pTradeStats['closeSellPrice']
                lCloseSellTradedQty = lQtyTraded
            else :
                lReasonForTradingOrNotTradingCloseSell = "DummyBidQExhuasted"
            pTradeStats['NumberOfCloseSell'] += lQtyTraded

        if pTradeStats['closeSellFrontP'] <> 0:
            pTradeStats['closeSellPrice'] = 0
            pTradeStats['closeSellQty'] = 0
#     
#     #Close Sell
#     if(pPrevObj.CloseSell < 0):
#         lCloseSellTradedPrice = 0
#         lCloseSellTradedQty = 0
#         lQtyForWhichFillsCanBeGiven = pTradeStats['currentPositionLong'] 
#         lOpenOrCloseSide = 'Close'         
#         lPriceAtWhichOrderIsToBeKept = 0 
#         if pPrevObj.CloseSell == -2: 
#             lPriceAtWhichOrderIsToBeKept =  pPrevObj.AskP[1] - ( 1 * gTickSize) 
#         else:
#             lPriceAtWhichOrderIsToBeKept =  pPrevObj.AskP[0] - ( 1 * gTickSize) 
#         if  ( lPriceAtWhichOrderIsToBeKept == pPrevObj.AskP[0] - ( 1 * gTickSize) ) or pPrevObj.CloseSell == -1:
#             g_bestqty_list_for_close_sell = {} #Standing at Ask +1 
#             l_dummy_TTQChange_For_Sell,l_dummy_BidQ0,lReasonForTradingOrNotTradingCloseSell,lCloseSellTradedQty,lCloseSellTradedPrice = fillForStandingAtAskMinus1Pip(pPrevObj, l_dummy_BidQ0,spreadAtTimeOfPreviousDataRow,\
#                                                                                                                              currentLTP, l_dummy_TTQChange_For_Sell , lQtyForWhichFillsCanBeGiven,lOpenOrCloseSide)
#             gStandingAtAskPMinusOneTickInCloseSell = pPrevObj.AskP[0] - gTickSize
#         else: #Standing at Ask
#             l_dummy_TTQChange_For_Sell,lReasonForTradingOrNotTradingCloseSell,lCloseSellTradedQty,lCloseSellTradedPrice = fillForStandingAtAskForCloseSell(pPrevObj, currentLTP, l_dummy_TTQChange_For_Sell , lQtyForWhichFillsCanBeGiven , lOpenOrCloseSide , lPriceAtWhichOrderIsToBeKept)
#             gStandingAtAskPMinusOneTickInCloseSell = 0
#              
#         pTradeStats['totalSellAmountLong'] += lCloseSellTradedQty * lCloseSellTradedPrice
#         pTradeStats['currentPositionLong'] -= lCloseSellTradedQty
#         pTradeStats['NumberOfCloseSell'] += lCloseSellTradedQty
#     else:
#         gStandingAtAskPMinusOneTickInCloseSell = 0
    
    if(pPrevObj.OpenSell > 0 and  ( gMaxQty - pTradeStats['currentPositionShort'] ) > 0 ): # Need to sell
        #standing
        if pTradeStats['openSellFrontP'] <> 0:
            pTradeStats['openSellPrice'] = pTradeStats['openSellFrontP']
            pTradeStats['openSellQty'] = pTradeStats['openSellFrontQ']
            
        if lSpread > gTickSize:        
            if(l_dummy_TTQChange_For_Sell <= pTradeStats["openSellQty"]):
                lReasonForTradingOrNotTradingOpenSell = '(Spread>Pip)&&(NextTickTTQDidNotIncrease)'
            elif(currentLTP < pTradeStats['openSellPrice']):
                lReasonForTradingOrNotTradingOpenSell = '(Spread>Pip)&&(NextTickLTP!=Ask)'
            else:
                l_dummy_TTQChange_For_Sell -= pTradeStats["openSellQty"]
                lQtyToBeTraded = ( gMaxQty - pTradeStats['currentPositionShort'] )
                lQtyForWhichWeTrade = min( lQtyToBeTraded , l_dummy_TTQChange_For_Sell)
                pTradeStats['totalSellAmountShort'] += lQtyForWhichWeTrade * (pTradeStats['openSellPrice'])
                pTradeStats['currentPositionShort'] += lQtyForWhichWeTrade
                l_dummy_TTQChange_For_Sell -= lQtyForWhichWeTrade
                lReasonForTradingOrNotTradingOpenSell = 'OpenSell(Standing)'
                pTradeStats['NumberOfOpenSell'] += lQtyForWhichWeTrade
                lOpenSellTradedPrice = pTradeStats['openSellPrice']
                lOpenSellTradedQty = lQtyForWhichWeTrade
        #hitting
        elif pPrevObj.BidP[0] >= pTradeStats['openSellPrice']:
            if l_dummy_BidQ0 > 0 :

                lQtyToBeTraded = ( gMaxQty - pTradeStats['currentPositionShort'] )
                lQtyForWhichWeTrade = min( lQtyToBeTraded , l_dummy_BidQ0 )
                if pPrevObj.BidP[0] in g_quantity_adjustment_list_for_sell:
                    g_quantity_adjustment_list_for_sell[pPrevObj.BidP[0]] += lQtyForWhichWeTrade
                else:
                    g_quantity_adjustment_list_for_sell = {}
                    g_quantity_adjustment_list_for_sell[pPrevObj.BidP[0]] = lQtyForWhichWeTrade
                pTradeStats['totalSellAmountShort'] += lQtyForWhichWeTrade * (pTradeStats['openSellPrice'])
                pTradeStats['currentPositionShort'] += lQtyForWhichWeTrade
                lReasonForTradingOrNotTradingOpenSell = 'OpenSell(Hitting)'
                pTradeStats['NumberOfOpenSell'] += lQtyForWhichWeTrade
                l_dummy_BidQ0 -= lQtyForWhichWeTrade
                lOpenSellTradedPrice = pTradeStats['openSellPrice']
                lOpenSellTradedQty = lQtyForWhichWeTrade
            else:
                lReasonForTradingOrNotTradingOpenSell = 'DummyBidQZero'
                
        if pTradeStats['openSellFrontP'] <> 0:
            pTradeStats['openSellPrice'] = 0
            pTradeStats['openSellQty'] = 0


#     #Open Sell
#     if pPrevObj.OpenSell > 0 and (gMaxQty - pTradeStats['currentPositionShort'] ) > 0 :
#         lOpenSellTradedPrice = 0
#         lOpenSellTradedQty = 0
#         lQtyForWhichFillsCanBeGiven = ( gMaxQty - pTradeStats['currentPositionShort'] )
#         lOpenOrCloseSide = 'Open'
#         lPriceAtWhichOrderIsToBeKept = 0 
#         if pPrevObj.OpenSell == 2: 
#             lPriceAtWhichOrderIsToBeKept =  pPrevObj.AskP[1] - ( 1 * gTickSize) 
#         else:
#             lPriceAtWhichOrderIsToBeKept =  pPrevObj.AskP[0] - ( 1 * gTickSize) 
#                     
#         if  ( lPriceAtWhichOrderIsToBeKept == pPrevObj.AskP[0] - ( 1 * gTickSize) ) or pPrevObj.OpenSell == 1: 
#             g_bestqty_list_for_open_sell = {} #Standing at Ask +1 
#             l_dummy_TTQChange_For_Sell,l_dummy_BidQ0,lReasonForTradingOrNotTradingOpenSell,lOpenSellTradedQty,lOpenSellTradedPrice = fillForStandingAtAskMinus1Pip(pPrevObj, l_dummy_BidQ0,spreadAtTimeOfPreviousDataRow,\
#                                                                                                         currentLTP, l_dummy_TTQChange_For_Sell , lQtyForWhichFillsCanBeGiven,lOpenOrCloseSide)
#             gStandingAtAskPMinusOneTickInOpenSell = pPrevObj.AskP[0] - gTickSize
#         else:
#             l_dummy_TTQChange_For_Sell,lReasonForTradingOrNotTradingOpenSell,lOpenSellTradedQty,lOpenSellTradedPrice = fillForStandingAtAskForOpenSell(pPrevObj, currentLTP, l_dummy_TTQChange_For_Sell , lQtyForWhichFillsCanBeGiven , lOpenOrCloseSide , lPriceAtWhichOrderIsToBeKept)
#             gStandingAtAskPMinusOneTickInOpenSell = 0            
#         pTradeStats['totalSellAmountShort'] += lOpenSellTradedQty * lOpenSellTradedPrice
#         pTradeStats['currentPositionShort'] += lOpenSellTradedQty
#         pTradeStats['NumberOfOpenSell'] += lOpenSellTradedQty
#     else:
#         gStandingAtAskPMinusOneTickInOpenSell = 0 
#                                       
    pPrevObj.ReasonForTradingOrNotTradingOpenSell = lReasonForTradingOrNotTradingOpenSell
    pPrevObj.ReasonForTradingOrNotTradingOpenBuy = lReasonForTradingOrNotTradingOpenBuy
    pPrevObj.ReasonForTradingOrNotTradingCloseSell = lReasonForTradingOrNotTradingCloseSell
    pPrevObj.ReasonForTradingOrNotTradingCloseBuy = lReasonForTradingOrNotTradingCloseBuy
    return [  l_dummy_BidQ0 , l_dummy_AskQ0 , l_dummy_TTQChange_For_Buy , l_dummy_TTQChange_For_Sell , lCloseBuyTradedPrice , lCloseBuyTradedQty,lCloseSellTradedPrice,lCloseSellTradedQty,\
            lOpenBuyTradedPrice , lOpenBuyTradedQty,lOpenSellTradedPrice,lOpenSellTradedQty ]

def update_obj_list(pCurrentDataRow,l_obj):
    #print(l_obj.currentBuyPredictedValue2,l_obj.currentSellPredictedValue2)
    if 'nsefut' not in args.e:
        l_obj.AskP[0]  = float(pCurrentDataRow[colNumberOfData.AskP0])
        l_obj.BidP[0]  = float(pCurrentDataRow[colNumberOfData.BidP0])
        l_obj.AskQ[0] = int(pCurrentDataRow[colNumberOfData.AskQ0])
        l_obj.BidQ[0] = int(pCurrentDataRow[colNumberOfData.BidQ0])
        l_obj.AskP[1] = float(pCurrentDataRow[colNumberOfData.AskP1])
        l_obj.BidP[1] = float(pCurrentDataRow[colNumberOfData.BidP1])
        l_obj.AskQ[1] = int(pCurrentDataRow[colNumberOfData.AskQ1])
        l_obj.BidQ[1] = int(pCurrentDataRow[colNumberOfData.BidQ1])
        l_obj.AskP[2]  = float(pCurrentDataRow[colNumberOfData.AskP2])
        l_obj.BidP[2]  = float(pCurrentDataRow[colNumberOfData.BidP2])
        l_obj.AskQ[2] = int(pCurrentDataRow[colNumberOfData.AskQ2])
        l_obj.BidQ[2] = int(pCurrentDataRow[colNumberOfData.BidQ2])
        l_obj.AskP[3] = float(pCurrentDataRow[colNumberOfData.AskP3])
        l_obj.BidP[3] = float(pCurrentDataRow[colNumberOfData.BidP3])
        l_obj.AskQ[3] = int(pCurrentDataRow[colNumberOfData.AskQ3])
        l_obj.BidQ[3] = int(pCurrentDataRow[colNumberOfData.BidQ3])
        l_obj.AskP[4] = float(pCurrentDataRow[colNumberOfData.AskP4])
        l_obj.BidP[4] = float(pCurrentDataRow[colNumberOfData.BidP4])
        l_obj.AskQ[4] = int(pCurrentDataRow[colNumberOfData.AskQ4])
        l_obj.BidQ[4] = int(pCurrentDataRow[colNumberOfData.BidQ4])
        
    else:
        l_obj.AskP[0]  = float(pCurrentDataRow[colNumberOfData.BestAskP])
        l_obj.BidP[0]  = float(pCurrentDataRow[colNumberOfData.BestBidP])
        l_obj.AskQ[0] = int(pCurrentDataRow[colNumberOfData.BestAskQ])
        l_obj.BidQ[0] = int(pCurrentDataRow[colNumberOfData.BestBidQ])
        l_obj.AskP[1] = float(pCurrentDataRow[colNumberOfData.BestAskP1])
        l_obj.BidP[1] = float(pCurrentDataRow[colNumberOfData.BestBidP1])
        l_obj.AskQ[1] = int(pCurrentDataRow[colNumberOfData.BestAskQ1])
        l_obj.BidQ[1] = int(pCurrentDataRow[colNumberOfData.BestBidQ1])
        l_obj.BandAskP = map(float, [pCurrentDataRow[colNumberOfData.AskP0], pCurrentDataRow[colNumberOfData.AskP1], pCurrentDataRow[colNumberOfData.AskP2],
                                     pCurrentDataRow[colNumberOfData.AskP3], pCurrentDataRow[colNumberOfData.AskP4]])
        l_obj.BandAskQ = map(float, [pCurrentDataRow[colNumberOfData.AskQ0], pCurrentDataRow[colNumberOfData.AskQ1], pCurrentDataRow[colNumberOfData.AskQ2],
                                     pCurrentDataRow[colNumberOfData.AskQ3], pCurrentDataRow[colNumberOfData.AskQ4]])
        l_obj.BandBidP = map(float, [pCurrentDataRow[colNumberOfData.BidP0], pCurrentDataRow[colNumberOfData.BidP1], pCurrentDataRow[colNumberOfData.BidP2],
                                     pCurrentDataRow[colNumberOfData.BidP3], pCurrentDataRow[colNumberOfData.BidP4]])
        l_obj.BandBidQ = map(float, [pCurrentDataRow[colNumberOfData.BidQ0], pCurrentDataRow[colNumberOfData.BidQ1], pCurrentDataRow[colNumberOfData.BidQ2],
                                     pCurrentDataRow[colNumberOfData.BidQ3], pCurrentDataRow[colNumberOfData.BidQ4]])

    l_obj.currentTimeStamp = common.convertTimeStampFromStringToFloat(pCurrentDataRow[colNumberOfData.TimeStamp])
    l_obj.LTP = float(pCurrentDataRow[colNumberOfData.LTP])
    l_obj.TTQ = float(pCurrentDataRow[colNumberOfData.TTQ])
    l_obj.MsgCode = pCurrentDataRow[colNumberOfData.MsgCode]
    l_obj.OrderType = pCurrentDataRow[colNumberOfData.OrderType]
    l_obj.NewP = float(pCurrentDataRow[colNumberOfData.NewP])
    l_obj.NewQ = float(pCurrentDataRow[colNumberOfData.NewQ])
    if(l_obj.MsgCode == "M"):
        l_obj.OldP = float(pCurrentDataRow[colNumberOfData.OldP])
        l_obj.OldQ = float(pCurrentDataRow[colNumberOfData.OldQ])
    return l_obj
    
def readOnceAndWrite(pFileName, entryCL , exitCL , entryCL2, exitCL2, predictedValuesList):
    global transactionCost , currencyDivisor, gMaxQty
    attribute.initList()
    tradeStats = dict()
    tradeStats['totalSellAmountShort'] = 0
    tradeStats['totalBuyAmountShort'] = 0
    tradeStats['totalSellAmountLong'] = 0
    tradeStats['totalBuyAmountLong'] = 0
    tradeStats['NumberOfOpenBuy'] = 0
    tradeStats['NumberOfCloseSell'] = 0
    tradeStats['NumberOfOpenSell'] = 0
    tradeStats['NumberOfCloseBuy'] = 0
    tradeStats['currentPositionShort'] = 0
    tradeStats['currentPositionLong'] = 0
    tradeStats['openBuyPrice'] = 0
    tradeStats['openSellPrice'] = 0
    tradeStats['closeBuyPrice'] = 0
    tradeStats['closeSellPrice'] = 0
    tradeStats['openSellQty'] = 0
    tradeStats['closeSellQty'] = 0
    tradeStats['openBuyQty'] = 0
    tradeStats['closeBuyQty'] = 0
    tradeStats['openSellFrontP'] = 0
    tradeStats['closeSellFrontP'] = 0
    tradeStats['openBuyFrontP'] = 0
    tradeStats['closeBuyFrontP'] = 0
    tradeStats['openSellFrontQ'] = 0
    tradeStats['closeSellFrontQ'] = 0
    tradeStats['openBuyFrontQ'] = 0
    tradeStats['closeBuyFrontQ'] = 0
    lActualProfitShort = 0
    lActualProfitLong = 0
    lMTMGrossProfitLong = 0
    lMTMGrossProfitShort = 0
    
    currentIndex = 0
    l_previous_obj = None
    l_obj= None
    print("Processing the data file for trades :")
    attribute.initList()
    print("EntryLevels",entryCL , exitCL)
    
    lOpenSell = 0
    lOpenBuy = 0
    lCloseSell = 0
    lCloseBuy = 0
    lMaxDepthLevel = 2
    lCancelCLOpen = [entryCL2] * lMaxDepthLevel
    lCancelCLClose = [exitCL2] * lMaxDepthLevel
    
    for currentDataRow,pObj in zip(dataFile.matrix[10000:],predictedValuesList):
        
        l_obj = update_obj_list(currentDataRow,pObj)
        if(l_previous_obj != None):
            lPrevShortPos, lPrevLongPos = tradeStats["currentPositionShort"], tradeStats["currentPositionLong"]
            lReturnList = checkIfPreviousDecisionToEnterOrExitTradeWasSuccessful( l_obj , l_previous_obj , tradeStats )
            lDummyBidQ0 = lReturnList[0]
            lDummyAskQ0 = lReturnList[1]
            lDummyTTQForBuy = lReturnList[2]
            lDummyTTQForSell = lReturnList[3]

            lCloseBuyTradedPrice = lReturnList[4]
            lCloseBuyTradedQty = lReturnList[5]
            lCloseSellTradedPrice = lReturnList[6]
            lCloseSellTradedQty = lReturnList[7]
            lOpenBuyTradedPrice = lReturnList[8]
            lOpenBuyTradedQty = lReturnList[9]
            lOpenSellTradedPrice = lReturnList[10]
            lOpenSellTradedQty = lReturnList[11]
            
            lActualProfitLong += lCloseSellTradedPrice * lCloseSellTradedQty - lOpenBuyTradedPrice * lOpenBuyTradedPrice
            lActualProfitShort += lOpenSellTradedPrice * lOpenSellTradedQty - lCloseBuyTradedPrice * lCloseBuyTradedPrice
            lMTMGrossProfitShort -= tradeStats['currentPositionShort'] * l_obj.AskP[0]
            lMTMGrossProfitLong += tradeStats['currentPositionLong'] * l_obj.BidP[0]
            
            if currentIndex > 0:
                if(g_bestqty_list_for_close_buy != {}):
                    l_best_bidq_for_close = g_bestqty_list_for_close_buy['qty']
                    l_best_bidp_for_close = g_bestqty_list_for_close_buy['price']
                else:
                    l_best_bidq_for_close = 0
                    l_best_bidp_for_close = 0
                if(g_bestqty_list_for_close_sell != {}):
                    l_best_askq_for_close = g_bestqty_list_for_close_sell['qty']
                    l_best_askp_for_close = g_bestqty_list_for_close_sell['price'] 
                else:
                    l_best_askq_for_close = 0
                    l_best_askp_for_close = 0
                if(g_bestqty_list_for_open_buy != {}):
                    l_best_bidq_for_open = g_bestqty_list_for_open_buy['qty']
                    l_best_bidp_for_open = g_bestqty_list_for_open_buy['price']
                else:
                    l_best_bidq_for_open = 0
                    l_best_bidp_for_open = 0
                if(g_bestqty_list_for_open_sell != {}):
                    l_best_askq_for_open = g_bestqty_list_for_open_sell['qty']
                    l_best_askp_for_open = g_bestqty_list_for_open_sell['price'] 
                else:
                    l_best_askq_for_open = 0
                    l_best_askp_for_open = 0
                attribute.aList[currentIndex-1][0] = l_obj.currentTimeStamp
                attribute.aList[currentIndex-1][1] = tradeStats['currentPositionLong']
                attribute.aList[currentIndex-1][2] = tradeStats['currentPositionShort']
                listOfStringsToPrint = [ str(l_previous_obj.BidQ[0]) , str(l_previous_obj.BidP[0]),str(l_previous_obj.BidQ[1]) , str(l_previous_obj.BidP[1]),\
                                           str(l_previous_obj.AskQ[0]) , str(l_previous_obj.AskP[0]) , str(l_previous_obj.AskQ[1]) , str(l_previous_obj.AskP[1]) ,\
                                          str(l_previous_obj.TTQ) , str(l_previous_obj.LTP) ,\
                                          str(l_previous_obj.currentBuyPredictedValue1) , str(l_previous_obj.currentSellPredictedValue1),str(l_previous_obj.currentBuyPredictedValue2) , str(l_previous_obj.currentSellPredictedValue2) , \
                                          str(l_previous_obj.OpenBuy) ,l_previous_obj.ReasonForTradingOrNotTradingOpenBuy ,str(l_previous_obj.CloseBuy) ,l_previous_obj.ReasonForTradingOrNotTradingCloseBuy , \
                                         str(l_previous_obj.OpenSell) ,l_previous_obj.ReasonForTradingOrNotTradingOpenSell ,str(l_previous_obj.CloseSell) ,l_previous_obj.ReasonForTradingOrNotTradingCloseSell  , \
                                         str(tradeStats['NumberOfOpenBuy']),str(tradeStats['NumberOfCloseBuy']),str(tradeStats['NumberOfOpenSell']),\
                                         str(tradeStats['NumberOfCloseSell']),str(lDummyBidQ0),str(lDummyAskQ0),\
                                         str(lDummyTTQForBuy),str(lDummyTTQForSell),str(l_best_bidq_for_close),str(l_best_bidp_for_close),str(l_best_askp_for_close),str(l_best_askq_for_close) ,\
                                         str(l_best_bidq_for_open),str(l_best_bidp_for_open),str(l_best_askp_for_open),str(l_best_askq_for_open) ,\
                                         str(lCloseBuyTradedPrice), str(lCloseBuyTradedQty), str(lCloseSellTradedPrice),str(lCloseSellTradedQty),\
                                         str(lOpenBuyTradedPrice), str(lOpenBuyTradedQty), str(lOpenSellTradedPrice),str(lOpenSellTradedQty)]
                attribute.aList[currentIndex-1][3] =  ";".join(listOfStringsToPrint)
                currentTimeStamp = common.convertTimeStampFromStringToFloat(currentDataRow[colNumberOfData.TimeStamp])
            
#            if currentIndex == 2321 or currentIndex == 2387:
#                import pdb
#                pdb.set_trace()
            l_obj.OpenSell = 0
            l_obj.CloseBuy= 0
            l_obj.OpenBuy  = 0
            l_obj.CloseSell = 0
            
            lPrevOpenBuyPrice = tradeStats['openBuyPrice']
            lPrevOpenSellPrice = tradeStats['openSellPrice']
            lPrevCloseBuyPrice = tradeStats['closeBuyPrice']
            lPrevCloseSellPrice = tradeStats['closeSellPrice']

            lCurrentSellPredictedValue = [l_obj.currentSellPredictedValue1, l_obj.currentSellPredictedValue2]
            lCurrentBuyPredictedValue = [l_obj.currentBuyPredictedValue1, l_obj.currentBuyPredictedValue2]
            
            lLevelDecisionListOS = [ (lCurrentSellPredictedValue[i] > entryCL) for i in xrange(lMaxDepthLevel)]
            lLevelDecisionListCS = [ (lCurrentSellPredictedValue[i] > exitCL) for i in xrange(lMaxDepthLevel)]
            lLevelDecisionListOB = [ (lCurrentBuyPredictedValue[i] > entryCL) for i in xrange(lMaxDepthLevel)]
            lLevelDecisionListCB = [ (lCurrentBuyPredictedValue[i] > exitCL) for i in xrange(lMaxDepthLevel)]
            
            #Open Sell and Close Buy
            if (sum(lLevelDecisionListOS) > 0 and tradeStats['currentPositionLong'] == 0 and tradeStats['currentPositionShort'] < gMaxQty):
                lOpenSell = lLevelDecisionListOS.index(1) + 1
                l_obj.OpenSell = lOpenSell
                tradeStats["openSellPrice"] = l_obj.AskP[lOpenSell-1] - gTickSize
                tradeStats['openSellFrontP'] = 0
                tradeStats['openSellFrontQ'] = 0
            
            if tradeStats["openSellPrice"] in l_obj.AskP:
                if (tradeStats["openSellQty"] == 0 and lPrevOpenSellPrice <> tradeStats['openSellPrice']) or tradeStats["openSellQty"] > l_obj.AskQ[ l_obj.AskP.index(tradeStats["openSellPrice"])]:
                    tradeStats["openSellQty"] = l_obj.AskQ[ l_obj.AskP.index(tradeStats["openSellPrice"])]
            else:
                tradeStats["openSellQty"] = 0
                
            if (lOpenSell > 0):
                i = 0
                while (i < lMaxDepthLevel and tradeStats["openSellPrice"] + gTickSize > l_obj.AskP[i]):
                    i += 1
                lOpenSell = min(i + 1, lMaxDepthLevel)
                
            if(lOpenSell > 0 and lCurrentSellPredictedValue[lOpenSell-1] < lCancelCLOpen[lOpenSell-1]) or tradeStats['currentPositionShort'] == gMaxQty:
                lOpenSell = 0
                
            if (sum(lLevelDecisionListCB) > 0 and tradeStats['currentPositionShort'] > 0 and lOpenSell == 0):
                lCloseBuy = -lLevelDecisionListCB.index(1) - 1
                l_obj.CloseBuy = lCloseBuy
                tradeStats["closeBuyPrice"] = l_obj.BidP[-lCloseBuy-1] + gTickSize
                tradeStats['closeBuyFrontP'] = 0
                tradeStats['closeBuyFrontQ'] = 0

            if tradeStats["closeBuyPrice"] in l_obj.BidP:
                if (tradeStats["closeBuyQty"] == 0 and lPrevCloseBuyPrice <> tradeStats['closeBuyPrice']) or tradeStats["closeBuyQty"] > l_obj.BidQ[ l_obj.BidP.index(tradeStats["closeBuyPrice"])]:
                    tradeStats["closeBuyQty"] = l_obj.BidQ[ l_obj.BidP.index(tradeStats["closeBuyPrice"])]
            else:
                tradeStats["closeBuyQty"] = 0

            if (lCloseBuy < 0):
                i = 0
                while (i < lMaxDepthLevel and tradeStats["closeBuyPrice"] - gTickSize < l_obj.BidP[i]):
                    i += 1
                lCloseBuy = max(-i - 1, -lMaxDepthLevel)
                
            if(lCloseBuy < 0 and lCurrentBuyPredictedValue[-lCloseBuy-1] < lCancelCLClose[-lCloseBuy-1]) or tradeStats['currentPositionShort'] == 0:
                lCloseBuy = 0
                
            #Open Buy and Close Sell
            if (sum(lLevelDecisionListOB) > 0 and tradeStats['currentPositionShort'] == 0 and tradeStats['currentPositionLong'] < gMaxQty):
                lOpenBuy = lLevelDecisionListOB.index(1) + 1
                l_obj.OpenBuy = lOpenBuy
                tradeStats["openBuyPrice"] = l_obj.BidP[lOpenBuy-1] + gTickSize
                tradeStats['openBuyFrontP'] = 0
                tradeStats['openBuyFrontQ'] = 0

            if tradeStats["openBuyPrice"] in l_obj.BidP:
                if (tradeStats["openBuyQty"] == 0 and lPrevOpenBuyPrice <> tradeStats['openBuyPrice']) or tradeStats["openBuyQty"] > l_obj.BidQ[ l_obj.BidP.index(tradeStats["openBuyPrice"])]:
                    tradeStats["openBuyQty"] = l_obj.BidQ[ l_obj.BidP.index(tradeStats["openBuyPrice"])]
            else:
                tradeStats["openBuyQty"] = 0
                    
            if (lOpenBuy > 0):
                i = 0
                while (i < lMaxDepthLevel and tradeStats["openBuyPrice"] - gTickSize < l_obj.BidP[i]):
                    i += 1
                lOpenBuy = min(i + 1, lMaxDepthLevel)

            if(lOpenBuy > 0 and lCurrentBuyPredictedValue[lOpenBuy-1] < lCancelCLOpen[lOpenBuy-1]) or tradeStats['currentPositionLong'] == gMaxQty:
                lOpenBuy = 0
                
            if (sum(lLevelDecisionListCS) > 0 and tradeStats['currentPositionLong'] > 0 and lOpenBuy == 0):
                lCloseSell = -lLevelDecisionListCS.index(1) - 1
                l_obj.CloseSell = lCloseSell
                tradeStats["closeSellPrice"] = l_obj.AskP[-lCloseSell-1] - gTickSize
                tradeStats['closeSellFrontP'] = 0
                tradeStats['closeSellFrontQ'] = 0

            if tradeStats["closeSellPrice"] in l_obj.AskP:
                if (tradeStats["closeSellQty"] == 0 and lPrevCloseSellPrice <> tradeStats['closeSellPrice']) or tradeStats["closeSellQty"] > l_obj.AskQ[ l_obj.AskP.index(tradeStats["closeSellPrice"])]:
                    tradeStats["closeSellQty"] = l_obj.AskQ[ l_obj.AskP.index(tradeStats["closeSellPrice"])]
            else:
                tradeStats["closeSellQty"] = 0
                
            if (lCloseSell < 0):
                i = 0
                while (i < lMaxDepthLevel and tradeStats["closeSellPrice"] + gTickSize > l_obj.AskP[i]):
                    i += 1
                lCloseSell = max(-i - 1, -lMaxDepthLevel)

            if(lCloseSell < 0 and lCurrentSellPredictedValue[-lCloseSell-1] < lCancelCLClose[-lCloseSell-1]) or tradeStats['currentPositionLong'] == 0:
                lCloseSell = 0
                
                
            if lOpenSell == 0 and tradeStats['currentPositionShort'] == 0 and tradeStats['openSellFrontP'] == 0:
                tradeStats['openSellFrontP'] = l_obj.BandAskP[1] + gTickSize
                tradeStats['openSellFrontQ'] = l_obj.AskQ[l_obj.AskP.index(tradeStats['openSellFrontP'])] if tradeStats['openSellFrontP'] in l_obj.AskP else 0
                
            elif lOpenSell == 0 and tradeStats['currentPositionShort'] == 0 and tradeStats['openSellFrontP'] <= l_obj.BandAskP[0]:
                if lCurrentSellPredictedValue[1] < lCancelCLOpen[1]:
                    tradeStats['openSellFrontP'] = l_obj.BandAskP[1] + gTickSize
                    tradeStats['openSellFrontQ'] = l_obj.AskQ[l_obj.AskP.index(tradeStats['openSellFrontP'])] if tradeStats['openSellFrontP'] in l_obj.AskP else 0
            
            elif lOpenSell == 0 and tradeStats['currentPositionShort'] == 0:
                if tradeStats['openSellFrontP'] in l_obj.AskP:
                    tradeStats['openSellFrontQ'] = min(l_obj.AskQ[l_obj.AskP.index(tradeStats['openSellFrontP'])], tradeStats['openSellFrontQ'])
                
            if lOpenBuy == 0 and tradeStats['currentPositionLong'] == 0 and tradeStats['openBuyFrontP'] == 0:
                tradeStats['openBuyFrontP'] = l_obj.BandBidP[1] - gTickSize
                tradeStats['openBuyFrontQ'] = l_obj.BidQ[l_obj.BidP.index(tradeStats['openBuyFrontP'])] if tradeStats['openBuyFrontP'] in l_obj.BidP else 0
                
            elif lOpenBuy == 0 and tradeStats['currentPositionLong'] == 0 and tradeStats['openBuyFrontP'] >= l_obj.BandBidP[0]:
                if lCurrentBuyPredictedValue[1] < lCancelCLOpen[1]:
                    tradeStats['openBuyFrontP'] = l_obj.BandBidP[1] - gTickSize
                    tradeStats['openBuyFrontQ'] = l_obj.BidQ[l_obj.BidP.index(tradeStats['openBuyFrontP'])] if tradeStats['openBuyFrontP'] in l_obj.BidP else 0
            
            elif lOpenBuy == 0 and tradeStats['currentPositionLong'] == 0:
                if tradeStats['openBuyFrontP'] in l_obj.BidP:
                    tradeStats['openBuyFrontQ'] = min(l_obj.BidQ[l_obj.BidP.index(tradeStats['openBuyFrontP'])], tradeStats['openBuyFrontQ'])
                
            if lCloseSell == 0 and tradeStats['currentPositionLong'] == gMaxQty and tradeStats['closeSellFrontP'] == 0:
                tradeStats['closeSellFrontP'] = l_obj.BandAskP[1] + gTickSize
                tradeStats['closeSellFrontQ'] = l_obj.AskQ[l_obj.AskP.index(tradeStats['closeSellFrontP'])] if tradeStats['closeSellFrontP'] in l_obj.AskP else 0
                
            elif lCloseSell == 0 and tradeStats['currentPositionLong'] == gMaxQty and tradeStats['closeSellFrontP'] <= l_obj.BandAskP[0]:
                if lCurrentSellPredictedValue[1] < lCancelCLClose[1]:
                    tradeStats['closeSellFrontP'] = l_obj.BandAskP[1] + gTickSize
                    tradeStats['closeSellFrontQ'] = l_obj.AskQ[l_obj.AskP.index(tradeStats['closeSellFrontP'])] if tradeStats['closeSellFrontP'] in l_obj.AskP else 0
            
            elif lCloseSell == 0 and tradeStats['currentPositionLong'] == gMaxQty:
                if tradeStats['closeSellFrontP'] in l_obj.AskP:
                    tradeStats['closeSellFrontQ'] = min(l_obj.AskQ[l_obj.AskP.index(tradeStats['closeSellFrontP'])], tradeStats['closeSellFrontQ'])
                
            if lCloseBuy == 0 and tradeStats['currentPositionShort'] == gMaxQty and tradeStats['closeBuyFrontP'] == 0:
                tradeStats['closeBuyFrontP'] = l_obj.BandBidP[1] - gTickSize
                tradeStats['closeBuyFrontQ'] = l_obj.BidQ[l_obj.BidP.index(tradeStats['closeBuyFrontP'])] if tradeStats['closeBuyFrontP'] in l_obj.BidP else 0
                
            elif lOpenBuy == 0 and tradeStats['currentPositionShort'] == gMaxQty and tradeStats['closeBuyFrontP'] >= l_obj.BandBidP[0]:
                if lCurrentBuyPredictedValue[1] < lCancelCLClose[1]:
                    tradeStats['closeBuyFrontP'] = l_obj.BandBidP[1] - gTickSize
                    tradeStats['closeBuyFrontQ'] = l_obj.BidQ[l_obj.BidP.index(tradeStats['closeBuyFrontP'])] if tradeStats['closeBuyFrontP'] in l_obj.BidP else 0
            
            elif lOpenBuy == 0 and tradeStats['currentPositionShort'] == gMaxQty:
                if tradeStats['closeBuyFrontP'] in l_obj.BidP:
                    tradeStats['closeBuyFrontQ'] = min(l_obj.BidQ[l_obj.BidP.index(tradeStats['closeBuyFrontP'])], tradeStats['closeBuyFrontQ'])


            l_obj.OpenSell = lOpenSell
            if lOpenSell == 0:
                tradeStats["openSellPrice"] = 0
                tradeStats["openSellQty"] = 0
            l_obj.CloseSell = lCloseSell
            if lCloseSell == 0:
                tradeStats["closeSellPrice"] = 0
                tradeStats["closeSellQty"] = 0
            l_obj.OpenBuy = lOpenBuy
            if lOpenBuy == 0:
                tradeStats["openBuyPrice"] = 0
                tradeStats["openBuyQty"] = 0
            l_obj.CloseBuy = lCloseBuy
            if lCloseBuy == 0:
                tradeStats["closeBuyPrice"] = 0
                tradeStats["closeBuyQty"] = 0
        
        l_previous_obj = l_obj
        currentIndex = currentIndex + 1

# Squaring off if some open position there   
    if tradeStats['currentPositionLong'] > 0:
        tradeStats['NumberOfCloseSell'] += tradeStats['currentPositionLong']
        tradeStats['totalSellAmountLong'] += tradeStats['currentPositionLong'] * (l_previous_obj.BidP[0])
        tradeStats['currentPositionLong'] = 0
        l_obj.ReasonForTradingOrNotTradingCloseSell = 'CloseSell(Hitting)'
    if tradeStats['currentPositionShort'] > 0:
        tradeStats['NumberOfCloseBuy'] += tradeStats['currentPositionShort']
        tradeStats['totalBuyAmountShort'] += tradeStats['currentPositionShort'] * (l_previous_obj.AskP[0])
        tradeStats['currentPositionShort'] = 0
        l_obj.ReasonForTradingOrNotTradingCloseBuy = 'CloseBuy(Hitting)'
    
#     attribute.aList[currentIndex-1][0] = currentTimeStamp
#     attribute.aList[currentIndex-1][1] = tradeStats['currentPositionLong']
#     attribute.aList[currentIndex-1][2] = tradeStats['currentPositionShort']
#     listOfStringsToPrint = [  str(l_previous_obj.BidQ[0]) , str(l_previous_obj.BidP[0]),str(l_previous_obj.BidQ[1]) , str(l_previous_obj.BidP[1]),\
#                                          str(l_previous_obj.AskQ[0]) , str(l_previous_obj.AskP[0]) , str(l_previous_obj.AskQ[1]) , str(l_previous_obj.AskP[1]) ,\
#                                          str(l_previous_obj.TTQ) , str(l_previous_obj.LTP) ,str(l_previous_obj.fA),str(l_previous_obj.fB),str(l_previous_obj.fC),\
#                                          str(l_previous_obj.fD),str(l_previous_obj.fE),str(l_previous_obj.fA1),str(l_previous_obj.fB1),str(l_previous_obj.fC1),str(l_previous_obj.fD1),str(l_previous_obj.fE1),\
#                                          str(l_previous_obj.currentBuyPredictedValue1) , str(l_previous_obj.currentSellPredictedValue1),str(l_previous_obj.currentBuyPredictedValue2) , str(l_previous_obj.currentSellPredictedValue2) , \
#                                          str(l_previous_obj.OpenBuy) ,l_previous_obj.ReasonForTradingOrNotTradingOpenBuy ,str(l_previous_obj.CloseBuy) ,l_previous_obj.ReasonForTradingOrNotTradingCloseBuy , \
#                                         str(l_previous_obj.OpenSell) ,l_previous_obj.ReasonForTradingOrNotTradingOpenSell ,str(l_previous_obj.CloseSell) ,l_previous_obj.ReasonForTradingOrNotTradingCloseSell  , \
#                                         str(tradeStats['NumberOfCloseBuy']),str(tradeStats['NumberOfOpenBuy']),\
#                                         str(tradeStats['NumberOfCloseBuy']),str(tradeStats['NumberOfOpenSell']),\
#                                         str(tradeStats['NumberOfCloseSell']),str(lDummyBidQ0),str(lDummyAskQ0),\
#                                         str(lDummyTTQForBuy),str(lDummyTTQForSell),str(l_best_bidq),str(l_best_bidp),str(l_best_askp), str(l_best_askq) , "0;0;0;0"]
#     attribute.aList[currentIndex-1][3] =  ";".join(listOfStringsToPrint) 
    
    dirName = args.pd.replace('/ro/','/rs/')
    tradeLogMainDirName = dirName+"/t/"
    if not os.path.exists(tradeLogMainDirName):
        os.mkdir(tradeLogMainDirName)
    tradeLogSubDirectoryName = tradeLogMainDirName + mainExperimentName+"/"
    if not os.path.exists(tradeLogSubDirectoryName):
        os.mkdir(tradeLogSubDirectoryName)
    
    fileName = tradeLogSubDirectoryName + pFileName + ".trade" 
    lHeaderColumnNamesList  = ['TimeStamp','CurrentPositionLong','CurrentPositionShort','BidQ0;BidP0;BidQ1;BidP1','AskQ0;AskP0;AskQ1;AskP1','TTQ','LTP',\
                               'CurBuyPredValue5Level','CurrentSellPredValue5Level','CurBuyPredValue6Level','CurrentSellPredValue6Level',\
                               'EnterTradeOpenBuy','ReasonForTradingOrNotTradingOpenBuy','EnterTradeCloseBuy','ReasonForTradingOrNotTradingCloseBuy','EnterTradeOpenSell','ReasonForTradingOrNotTradingOpenSell','EnterTradeCloseSell','ReasonForTradingOrNotTradingCloseSel'                                ,'NumberOfOpenBuy','NumOfCloseBuy','NumberOfOpenSell','NumberOfCloseSell','DummyBidQ0','DummyAskQ0','DummyTTQChangeForSell','DummyTTQChangeForBuy' \
                               ,'BestBidQClose','BestBidPClose','BestAskPClose','BestAskQClose','BestBidQOpen','BestBidPOpen','BestAskPOpen','BestAskQOpen','CloseBuyTradedPrcie','CloseBuyTradedQty','CloseSellTradedPrice','CloseSellTradedQty',
                               'OpenBuyTradedPrcie','OpenBuyTradedQty','OpenSellTradedPrice','OpenSellTradedQty']
    
    attribute.writeToFile(fileName , lHeaderColumnNamesList)

    
    tradeResultMainDirName = dirName+"/r/"
    if not os.path.exists(tradeResultMainDirName):
        os.mkdir(tradeResultMainDirName)
    tradeResultSubDirectoryName =  tradeResultMainDirName + mainExperimentName+"/"
    if not os.path.exists(tradeResultSubDirectoryName):
        os.mkdir(tradeResultSubDirectoryName)
    fileName = tradeResultSubDirectoryName+pFileName+".result" 
    outputFile = open(fileName,"w")
    gross_short_profit = tradeStats['totalSellAmountShort'] - tradeStats['totalBuyAmountShort']
    gross_long_profit = tradeStats['totalSellAmountLong'] - tradeStats['totalBuyAmountLong']
    gross_profit = gross_short_profit + gross_long_profit
    net_short_profit = gross_short_profit - ( transactionCost * ( tradeStats['totalSellAmountShort'] + tradeStats['totalBuyAmountShort'] ) ) 
    net_long_profit = gross_long_profit - ( transactionCost * (tradeStats['totalSellAmountLong'] + tradeStats['totalBuyAmountLong'] ) )
    net_profit = net_short_profit + net_long_profit
    
    gross_short_profit_in_dollars = gross_profit / (currencyDivisor * 60)
    net_profit_in_dollars = net_profit / (currencyDivisor * 60 )
    #changed file write to modify it to Short Long version
    print("Starting to write: "+pFileName)
    print("The gross results for Short are: %.6f" %gross_short_profit, file = outputFile)
    print("The gross results for Long are: %.6f" %gross_long_profit, file = outputFile)
    print("Number of rows for which there is no prediction: " + str(0), file = outputFile)    
    print("Number of times asked to enter trade Short: " + str(0), file = outputFile)    
    print("Number of times asked to enter trade Long: " + str(0), file = outputFile)    
    print("Number of times asked to exit trade Short: " + str(0), file = outputFile)
    print("Number of times asked to exit trade Long: " + str(0), file = outputFile)
    print("The net results for Short are: %.6f" %net_short_profit, file = outputFile)
    print("The net results for Long are: %.6f" %net_long_profit, file = outputFile)
    print("Gross Results in Dollars: %.6f" %gross_short_profit_in_dollars, file = outputFile)
    print("Net Results in Dollars: %.6f" %net_profit_in_dollars, file = outputFile)
    print("Number of times Close buy trade happened: " + str(tradeStats['NumberOfCloseBuy']), file = outputFile)
    print("Number of times open buy trade happened: " + str(tradeStats['NumberOfOpenBuy']), file = outputFile)
    print("Assumed open sell trade did not happen since volume did not increase: " + str(0), file = outputFile)
    print("Assumed close sell trade did not happen since volume did not increase: " + str(0), file = outputFile)
    print("Assumed open sell trade did not happen since bidP0 not same as LTP: " + str(0), file = outputFile)
    print("Assumed close sell trade did not happen since bidP0 not same as LTP: " + str(0), file = outputFile)
    print("Number of Open sell trade happened: " + str(tradeStats['NumberOfOpenSell']), file = outputFile)
    print("Number of Close sell trade happened: " + str(tradeStats['NumberOfCloseSell']), file = outputFile)
    print("The total open sell value is: " + str(tradeStats['totalSellAmountShort']), file = outputFile)
    print("The total close sell value is: " + str(tradeStats['totalSellAmountLong']), file = outputFile)
    print("The total close buy value is: " + str(tradeStats['totalBuyAmountShort']), file = outputFile)
    print("The total open buy value is: " + str(tradeStats['totalBuyAmountLong']), file = outputFile)

    try:
        averageOpenSellPrice = tradeStats['totalSellAmountShort']/tradeStats['NumberOfOpenSell'] 
        averageCloseBuyPrice = tradeStats['totalBuyAmountShort']/tradeStats['NumberOfCloseBuy'] 
    except:
        averageOpenSellPrice = 0 
        averageCloseBuyPrice = 0
    try:
        averageCloseSellPrice = tradeStats['totalSellAmountLong']/tradeStats['NumberOfCloseSell'] 
        averageOpenBuyPrice = tradeStats['totalBuyAmountLong']/tradeStats['NumberOfOpenBuy'] 
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
    dataFile.getDataIntoMatrix(args.pd)
    dataFileName = dataFile.getFileNameFromCommandLineParam(args.pd,5)
    print("dataFileName ",dataFileName)
    lIndexOfEntryOrExitCL = 0
    lWFDirName = args.pd.replace('/ro/','/wf/')
    predictedBuyValuesFileName = lWFDirName+"/p/"+mainExperimentName+"/"+args.a + 'buy' + '-td.' + os.path.basename(os.path.abspath(args.td)) + '-dt.' + \
    args.dt + '-targetClass.' + args.targetClass + '-f.' + experimentName + "-wt." + args.wt+ attribute.generateExtension() + ".predictions"
      
    predictedSellValuesFileName = lWFDirName+"/p/"+mainExperimentName+"/"+args.a + 'sell' + '-td.' + os.path.basename(os.path.abspath(args.td)) + '-dt.' +\
    args.dt + '-targetClass.' + args.targetClass + '-f.' + experimentName + "-wt." + args.wt+ attribute.generateExtension() + ".predictions"

    predictedBuyValuesFileNameBest = lWFDirName+"/p/"+mainExperimentNameBest+"/"+args.a + 'buy' + '-td.' + os.path.basename(os.path.abspath(args.td)) + '-dt.' + \
    args.dt + '-targetClass.' + args.targetClass + '-f.' + experimentNameBest + "-wt." + args.wt+ attribute.generateExtension() + ".predictions"
      
    predictedSellValuesFileNameBest = lWFDirName+"/p/"+mainExperimentNameBest+"/"+args.a + 'sell' + '-td.' + os.path.basename(os.path.abspath(args.td)) + '-dt.' +\
    args.dt + '-targetClass.' + args.targetClass + '-f.' + experimentNameBest + "-wt." + args.wt+ attribute.generateExtension() + ".predictions"
    print("prediction files",predictedBuyValuesFileName,predictedSellValuesFileName,predictedBuyValuesFileNameBest,predictedSellValuesFileNameBest)

    dataFileObject =  open(dataFileName,"r")
    buyPredictFileObject = open(predictedBuyValuesFileName,"r")
    sellPredictFileObject = open(predictedSellValuesFileName,"r")
    buyPredictFileObjectBest = open(predictedBuyValuesFileNameBest,"r")
    sellPredictFileObjectBest = open(predictedSellValuesFileNameBest,"r")
    lListOfAllPredcitionValues = getPredictionsIntoObjectList(dataFileObject,buyPredictFileObjectBest,sellPredictFileObjectBest,buyPredictFileObject,sellPredictFileObject)
    for lFileName in initialFileName:
        entryCL = float("." + gEntryCLList[lIndexOfEntryOrExitCL] )
        exitCL = float("." + gExitCLList[lIndexOfEntryOrExitCL] )
        entryCL2 = float("." + gEntryCL2List[lIndexOfEntryOrExitCL] )
        exitCL2 = float("." + gExitCL2List[lIndexOfEntryOrExitCL] )
        
        print("Entry"+str(entryCL)+"Exit"+str(exitCL))
        fileName = dirName + "/r/" + mainExperimentName + "/" + lFileName+".result"
        if os.path.isfile(fileName) and args.skipT.lower() == "yes":
            print("\nskipping as it is already done\n")
            continue
        readOnceAndWrite(lFileName,entryCL,exitCL,entryCL2,exitCL2, lListOfAllPredcitionValues)
        lIndexOfEntryOrExitCL = lIndexOfEntryOrExitCL + 1
      
if __name__ == "__main__":

    dirName = args.pd.replace('/ro/','/rs/')
    checkAllFilesAreExistOrNot = 'false'
      
    lWFDirName = args.pd.replace('/ro/','/wf/')
    predictedBuyValuesFileName = lWFDirName+"/p/"+mainExperimentName+"/"+args.a + 'buy' + '-td.' + os.path.basename(os.path.abspath(args.td)) + '-dt.' + \
    args.dt + '-targetClass.' + args.targetClass + '-f.' + experimentName + "-wt." + args.wt+ attribute.generateExtension() + ".predictions"
      
    predictedSellValuesFileName = lWFDirName+"/p/"+mainExperimentName+"/"+args.a + 'sell' + '-td.' + os.path.basename(os.path.abspath(args.td)) + '-dt.' +\
    args.dt + '-targetClass.' + args.targetClass + '-f.' + experimentName + "-wt." + args.wt+ attribute.generateExtension() + ".predictions"

    predictedBuyValuesFileNameBest = lWFDirName+"/p/"+mainExperimentNameBest+"/"+args.a + 'buy' + '-td.' + os.path.basename(os.path.abspath(args.td)) + '-dt.' + \
    args.dt + '-targetClass.' + args.targetClass + '-f.' + experimentNameBest + "-wt." + args.wt+ attribute.generateExtension() + ".predictions"
      
    predictedSellValuesFileNameBest = lWFDirName+"/p/"+mainExperimentNameBest+"/"+args.a + 'sell' + '-td.' + os.path.basename(os.path.abspath(args.td)) + '-dt.' +\
    args.dt + '-targetClass.' + args.targetClass + '-f.' + experimentNameBest + "-wt." + args.wt+ attribute.generateExtension() + ".predictions"
      
    if (1):
        for lFileName in initialFileName:
            fileName = dirName + "/r/" + mainExperimentName + "/" + lFileName+".result"
            if os.path.isfile(fileName) and args.skipT.lower() == "yes":
                print("Trade results file " + fileName + "Already exist. Not regenerating it. If you want to rerun it by making -skipT = no ")
            else: 
                checkAllFilesAreExistOrNot = 'true'
                print("Trade results file " + fileName + " Does not exist.")
           
        if checkAllFilesAreExistOrNot == 'true':
            print ("\nRunning the simulated trading program")
            main()
    else:
        print("File not found = " , predictedBuyValuesFileName )
        print ("Predcition files not yet generated")


