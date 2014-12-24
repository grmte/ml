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

if 'nsecur' in absPathOfExperimentName:
    pathAfterE = absPathOfExperimentName[absPathOfExperimentName.index("/nsecur/")+8:]
    if args.t ==None:
        transactionCost = 0.000015
    else:
        transactionCost = float(args.t)
    currencyDivisor = 10000
elif 'nsefut' in absPathOfExperimentName:
    pathAfterE = absPathOfExperimentName[absPathOfExperimentName.index("/nsefut/")+8:]
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
else:
    mainExperimentName = pathAfterE

experimentName = os.path.basename(absPathOfExperimentName)
gTickSize = int(args.tickSize)
gMaxQty = int(args.orderQty)

gEntryCLList = args.entryCL.split(";")
gExitCLList = args.exitCL.split(";")

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
                   '-l.'+gEntryCLList[indexOfCL]+"-"+gExitCLList[indexOfCL]  + "-tq." + args.orderQty + "-te.7With2Prob"

    initialFileName.append(lInitialFileName)
    
g_quantity_adjustment_list_for_sell = {}
g_quantity_adjustment_list_for_buy = {}
g_bestqty_list_for_close_sell = {}
g_bestqty_list_for_close_buy = {}
g_bestqty_list_for_open_sell = {}
g_bestqty_list_for_open_buy = {}
class Tick():
    def __init__(self,pCurrentDataRowTimeStamp,pBuyProb1,pSellProb1,pBuyProb2,pSellProb2,
                 lFeatureA,lFeatureB,lFeatureC,lFeatureD,lFeatureE,lFeatureA6,lFeatureB6,lFeatureC6,lFeatureD6,lFeatureE6):#pBuyPredictedValue,pSellPredictedValue):
        self.AskP = [0.0,0.0]
        self.AskQ = [0,0]
        self.BidP = [0.0,0.0]
        self.BidQ = [0,0]

        self.fA = lFeatureA
        self.fB = lFeatureB
        self.fC = lFeatureC
        self.fD = lFeatureD
        self.fE = lFeatureE
        
        self.fA1 = lFeatureA6
        self.fB1 = lFeatureB6
        self.fC1 = lFeatureC6
        self.fD1 = lFeatureD6
        self.fE1 = lFeatureE6
        
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
                
def getPredictionsIntoObjectList(fA5 , fB5 , fC5 , fD5 , fE5 , fA6 , fB6 , fC6 , fD6 , fE6):
    global gNoOfLineReadPerChunk,gTickSize
    lObjectList = []
    lCurrentDataRowCount = 0
    lPrevObj = None
    fileHasHeader = 1
    headerSkipped = 0
    featureFileSep = ";"
    lListOfBidP = []
    lListOfAskP = []
    lFeatureAFileRowListFor5Level = list(islice(fA5,10000))
    lFeatureBFileRowListFor5Level = list(islice( fB5,10000 ))
    lFeatureCFileRowListFor5Level = list(islice(fC5,10000))
    lFeatureDFileRowListFor5Level = list(islice( fD5,10000 ))
    lFeatureEFileRowListFor5Level = list(islice(fE5,10000))
    
    lFeatureAFileRowListFor6Level = list(islice( fA6,10000 ))
    lFeatureBFileRowListFor6Level = list(islice(fB6,10000))
    lFeatureCFileRowListFor6Level = list(islice( fC6,10000 ))
    lFeatureDFileRowListFor6Level = list(islice(fD6,10000))
    lFeatureEFileRowListFor6Level = list(islice( fE6,10000 ))
    while True:
        lFeatureAFileRowListFor5Level = list(islice(fA5,gNoOfLineReadPerChunk))
        lFeatureBFileRowListFor5Level = list(islice( fB5,gNoOfLineReadPerChunk ))
        lFeatureCFileRowListFor5Level = list(islice(fC5,gNoOfLineReadPerChunk))
        lFeatureDFileRowListFor5Level = list(islice( fD5,gNoOfLineReadPerChunk ))
        lFeatureEFileRowListFor5Level = list(islice(fE5,gNoOfLineReadPerChunk))
        
        lFeatureAFileRowListFor6Level = list(islice( fA6,gNoOfLineReadPerChunk ))
        lFeatureBFileRowListFor6Level = list(islice(fB6,gNoOfLineReadPerChunk))
        lFeatureCFileRowListFor6Level = list(islice( fC6,gNoOfLineReadPerChunk ))
        lFeatureDFileRowListFor6Level = list(islice(fD6,gNoOfLineReadPerChunk))
        lFeatureEFileRowListFor6Level = list(islice( fE6,gNoOfLineReadPerChunk ))
        
        if not lFeatureAFileRowListFor5Level :
            print("Finished reading file")
            lObjectList.append(lPrevObj)    
            lPrevObj = None          
            break
        lengthOfDataList = len(lFeatureAFileRowListFor5Level)
        lengthOfFeatureAListFor5Level = len(lFeatureAFileRowListFor5Level)
        lengthOfFeatureBListFor5Level = len(lFeatureBFileRowListFor5Level)
        
        if lengthOfDataList!=lengthOfFeatureAListFor5Level or lengthOfFeatureAListFor5Level!=lengthOfFeatureBListFor5Level:
            print("Length of data file and predicted buy and sell values file are not same ")
            os._exit(-1)
        for currentRowIndex in range(lengthOfDataList):
            if(fileHasHeader == 1 and headerSkipped != 1):
                headerSkipped = 1 
                continue

            lFeatureARow = lFeatureAFileRowListFor5Level[currentRowIndex].rstrip().split(featureFileSep)
            lFeatureATimeStamp = float(lFeatureARow[0])
            lFeatureA = float(lFeatureARow[1])
            
            lFeatureBRow = lFeatureBFileRowListFor5Level[currentRowIndex].rstrip().split(featureFileSep)
            lFeatureBTimeStamp = float(lFeatureBRow[0])
            lFeatureB = float(lFeatureBRow[1])

            lFeatureCRow = lFeatureCFileRowListFor5Level[currentRowIndex].rstrip().split(featureFileSep)
            lFeatureCTimeStamp = float(lFeatureCRow[0])
            lFeatureC = float(lFeatureCRow[1])
            
            lFeatureDRow = lFeatureDFileRowListFor5Level[currentRowIndex].rstrip().split(featureFileSep)
            lFeatureD = float(lFeatureDRow[1])
            
            lFeatureERow = lFeatureEFileRowListFor5Level[currentRowIndex].rstrip().split(featureFileSep)
            lFeatureE = float(lFeatureERow[1])
            
            lFeatureA6Row = lFeatureAFileRowListFor6Level[currentRowIndex].rstrip().split(featureFileSep)
            lFeatureA6 = float(lFeatureA6Row[1])
            
            lFeatureB6Row = lFeatureBFileRowListFor6Level[currentRowIndex].rstrip().split(featureFileSep)
            lFeatureB6 = float(lFeatureB6Row[1])

            lFeatureC6Row = lFeatureCFileRowListFor6Level[currentRowIndex].rstrip().split(featureFileSep)
            lFeatureC6 = float(lFeatureC6Row[1])
            
            lFeatureD6Row = lFeatureDFileRowListFor6Level[currentRowIndex].rstrip().split(featureFileSep)
            lFeatureD6 = float(lFeatureD6Row[1])
            
            lFeatureE6Row = lFeatureEFileRowListFor6Level[currentRowIndex].rstrip().split(featureFileSep)
            lFeatureE6 = float(lFeatureE6Row[1])
                        
            l_buy_SOP_of_alphas_for_5_level = exp ( ((813.280878130412 * lFeatureA ) + ( -546.820253147887 * lFeatureB) + ( -498.096438026184 * lFeatureC) + ( -1008.9535016807 * lFeatureD) + 1237.93033895547) )
            l_sell_SOP_of_alphas_for_5_level = exp( (( 366.62364204055 * lFeatureA  ) + ( -881.958964774577 * lFeatureB ) + ( 619.51957804397 * lFeatureC ) + ( 1003.99686893559 * lFeatureE ) - 1110.76386909796) )

            l_buy_SOP_of_alphas_for_6_level = exp ( ((813.280878130412 * lFeatureA6 ) + ( -546.820253147887 * lFeatureB6) + ( -498.096438026184 * lFeatureC6) + ( -1008.9535016807 * lFeatureD6) + 1237.93033895547) )
            l_sell_SOP_of_alphas_for_6_level = exp( (( 366.62364204055 * lFeatureA6  ) + ( -881.958964774577 * lFeatureB6 ) + ( 619.51957804397 * lFeatureC6 ) + ( 1003.99686893559* lFeatureE6 ) - 1110.76386909796) )            
            
            lBuyPredictedValueFor5Levels = l_buy_SOP_of_alphas_for_5_level / ( 1 + l_buy_SOP_of_alphas_for_5_level )
            lSellPredictedValueFor5Levels = l_sell_SOP_of_alphas_for_5_level / ( 1 + l_sell_SOP_of_alphas_for_5_level )
            
            lBuyPredictedValueFor6Levels = l_buy_SOP_of_alphas_for_6_level / ( 1 + l_buy_SOP_of_alphas_for_6_level )
            lSellPredictedValueFor6Levels = l_sell_SOP_of_alphas_for_6_level / ( 1 + l_sell_SOP_of_alphas_for_6_level )
                        
            if lFeatureCTimeStamp != lFeatureATimeStamp or lFeatureATimeStamp!=lFeatureBTimeStamp:
                print('Time stamp of data row with predicted value is not matching .\n Data row time stamp :- ' , lFeatureCTimeStamp,'BuyPredicted Time Stamp :- ' , lFeatureATimeStamp\
                      ,"SellPredicted Time Stamp :- ",lFeatureBTimeStamp)
                os._exit(-1)
            else:
                lObj = Tick(lFeatureCTimeStamp,lBuyPredictedValueFor5Levels,lSellPredictedValueFor5Levels,lBuyPredictedValueFor6Levels,lSellPredictedValueFor6Levels,
                            lFeatureA,lFeatureB,lFeatureC,lFeatureD,lFeatureE,lFeatureA6,lFeatureB6,lFeatureC6,lFeatureD6,lFeatureE6)
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
    
def fillsForHittingAtAsk(pPrevObj, p_dummy_AskQ0 , pQtyForWhichFillCanBeGiven, pOpenOrCloseSide):
    global g_quantity_adjustment_list_for_buy , gOpenBuyFillPrice
    lTradedPrice = 0
    lTradedQty = 0
    lReasonForTradingOrNotTrading = ''
    l_buy_qty = min(pQtyForWhichFillCanBeGiven, p_dummy_AskQ0)
    if pPrevObj.AskP[0] in g_quantity_adjustment_list_for_buy:
        g_quantity_adjustment_list_for_buy[pPrevObj.AskP[0]] += l_buy_qty
    else:
        g_quantity_adjustment_list_for_buy = {}
        g_quantity_adjustment_list_for_buy[pPrevObj.AskP[0]] = l_buy_qty
    
    
    if l_buy_qty > 0:
        lTradedPrice = pPrevObj.AskP[0]
        if pOpenOrCloseSide == "Open":
            gOpenBuyFillPrice = lTradedPrice
        lTradedQty = l_buy_qty
        p_dummy_AskQ0 -= l_buy_qty
        lReasonForTradingOrNotTrading = pOpenOrCloseSide + 'Buy(Hitting)'
    else:
        lReasonForTradingOrNotTrading = "DummyAskQExhuasted"
    return p_dummy_AskQ0, lReasonForTradingOrNotTrading, lTradedQty, lTradedPrice

def fillsForHittingAtBid(pPrevObj, p_dummy_BidQ0, pQtyForWhichFillCanBeGiven, pOpenOrCloseSide ):
    global g_quantity_adjustment_list_for_sell , gOpenSellFillPrice
    lTradedPrice = 0
    lTradedQty = 0
    lReasonForTradingOrNotTrading = ''
    lQtyForWhichWeTrade = min(pQtyForWhichFillCanBeGiven, p_dummy_BidQ0)
    if pPrevObj.BidP[0] in g_quantity_adjustment_list_for_sell:
        g_quantity_adjustment_list_for_sell[pPrevObj.BidP[0]] += lQtyForWhichWeTrade
    else:
        g_quantity_adjustment_list_for_sell = {}
        g_quantity_adjustment_list_for_sell[pPrevObj.BidP[0]] = lQtyForWhichWeTrade
    
    if p_dummy_BidQ0 > 0:
        lTradedPrice = pPrevObj.BidP[0]
        if pOpenOrCloseSide == "Open":
            gOpenSellFillPrice = lTradedPrice
        lTradedQty = lQtyForWhichWeTrade
        p_dummy_BidQ0 -= lQtyForWhichWeTrade
        lReasonForTradingOrNotTrading = pOpenOrCloseSide + 'Sell(Hitting)'
    else:
        lReasonForTradingOrNotTrading = "DummyBidQExhuasted"
    return p_dummy_BidQ0 , lReasonForTradingOrNotTrading, lTradedQty, lTradedPrice

def fillForStandingAtBidPlus1Pip(pPrevObj, p_dummy_AskQ0, spreadAtTimeOfPreviousDataRow, currentLTP, l_dummy_TTQChange_For_Buy, pQtyForWhichFillCanBeGiven , pOpenOrCloseSide):
    global gTickSize , gMaxQty , g_quantity_adjustment_list_for_sell , g_quantity_adjustment_list_for_buy , g_bestqty_list_for_close_sell, g_bestqty_list_for_close_buy , gOpenBuyFillPrice
    lTradedPrice = 0
    lTradedQty = 0
    lReasonForTradingOrNotTrading = ''
    #standing 
    if spreadAtTimeOfPreviousDataRow > gTickSize:
        if (l_dummy_TTQChange_For_Buy <= 0):
            lReasonForTradingOrNotTrading = '(Spread>Pip)&&(NextTickTTQDidNotIncrease)'
        elif (currentLTP != pPrevObj.BidP[0]):
            lReasonForTradingOrNotTrading = '(Spread>Pip)&&(LTP!=Bid)'
        elif ("OpenSell(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingOpenSell) or ("CloseSell(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingCloseSell)\
            or("OpenBuy(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingOpenBuy) or ("CloseBuy(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingCloseBuy):
            lReasonForTradingOrNotTrading = 'TTQChangeBecauseOfOurOrder'
        else:
            
            lTradedQty = min(pQtyForWhichFillCanBeGiven,l_dummy_TTQChange_For_Buy)
            l_dummy_TTQChange_For_Buy -= lTradedQty
            lTradedPrice = (pPrevObj.BidP[0] + gTickSize)
            if pOpenOrCloseSide == "Open":
                gOpenBuyFillPrice = lTradedPrice
            lReasonForTradingOrNotTrading = pOpenOrCloseSide + 'Buy(Standing)'
    #hitting
    else:
        p_dummy_AskQ0, lReasonForTradingOrNotTrading, lTradedQty, lTradedPrice = fillsForHittingAtAsk(pPrevObj, p_dummy_AskQ0 ,pQtyForWhichFillCanBeGiven, pOpenOrCloseSide)
    return l_dummy_TTQChange_For_Buy, p_dummy_AskQ0 , lReasonForTradingOrNotTrading, lTradedQty , lTradedPrice

def fillForStandingAtAskMinus1Pip(pPrevObj, p_dummy_BidQ0, spreadAtTimeOfPreviousDataRow, currentLTP, l_dummy_TTQChange_For_Sell, pQtyForWhichFillCanBeGiven , pOpenOrCloseSide):
    global gTickSize , gMaxQty , g_quantity_adjustment_list_for_sell , g_quantity_adjustment_list_for_buy , g_bestqty_list_for_close_sell, g_bestqty_list_for_close_buy , gOpenSellFillPrice 
    lTradedPrice = 0
    lTradedQty = 0
    lReasonForTradingOrNotTrading = ''
    #standing
    if spreadAtTimeOfPreviousDataRow > gTickSize:
        if (l_dummy_TTQChange_For_Sell <= 0):
            lReasonForTradingOrNotTrading = '(Spread>Pip)&&(NextTickTTQDidNotIncrease)'
        elif (currentLTP != pPrevObj.AskP[0]):
            lReasonForTradingOrNotTrading = '(Spread>Pip)&&(NextTickLTP!=Ask)'
        elif ("OpenSell(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingOpenSell) or ("CloseSell(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingCloseSell)\
            or("OpenBuy(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingOpenBuy) or ("CloseBuy(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingCloseBuy):
            lReasonForTradingOrNotTrading = 'TTQChangeBecauseOfOurOrder'
        else:
            
            lQtyForWhichWeTrade = min(pQtyForWhichFillCanBeGiven, l_dummy_TTQChange_For_Sell)
            lTradedPrice = pPrevObj.AskP[0] - gTickSize
            if pOpenOrCloseSide == "Open":
                gOpenSellFillPrice = lTradedPrice
            lTradedQty = lQtyForWhichWeTrade
            l_dummy_TTQChange_For_Sell -= lQtyForWhichWeTrade
            lReasonForTradingOrNotTrading = pOpenOrCloseSide + 'Sell(Standing)'
    #hitting
    else: 
        p_dummy_BidQ0,lReasonForTradingOrNotTrading,lTradedQty,lTradedPrice = fillsForHittingAtBid(pPrevObj, p_dummy_BidQ0, pQtyForWhichFillCanBeGiven, pOpenOrCloseSide)
    return l_dummy_TTQChange_For_Sell , p_dummy_BidQ0 , lReasonForTradingOrNotTrading , lTradedQty , lTradedPrice

def fillForStandingAtBidForCloseBuy(pPrevObj, currentLTP, l_dummy_TTQChange_For_Buy , pQtyForWhichFillCanBeGiven, pOpenOrCloseSide , pPriceAtWhichOrderIsToBeKept):
    global g_bestqty_list_for_close_buy ,gStandingAtAskPMinusOneTickInCloseSell ,gStandingAtBidPPlusOneTickInCloseBuy
    lTradedPrice = 0
    lTradedQty = 0
    lReasonForTradingOrNotTrading = ''
    if (g_bestqty_list_for_close_buy != {} and pPriceAtWhichOrderIsToBeKept != g_bestqty_list_for_close_buy['price']) or (g_bestqty_list_for_close_buy == {}):
        g_bestqty_list_for_close_buy = {} 
        g_bestqty_list_for_close_buy['price'] = pPriceAtWhichOrderIsToBeKept
        l_qty = 0
        if g_bestqty_list_for_close_buy['price'] == gStandingAtBidPPlusOneTickInCloseBuy:
            l_qty = 0
        else:
            try:
                indexAtWhichPriceIsFound = pPrevObj.BidP.index(pPriceAtWhichOrderIsToBeKept)
                l_qty = pPrevObj.BidQ[ indexAtWhichPriceIsFound ]
            except:
                l_qty = 0
            
        g_bestqty_list_for_close_buy['qty'] = l_qty
        lReasonForTradingOrNotTrading = 'AtBestBidStartingToStand'
    else:
        if (l_dummy_TTQChange_For_Buy <= 0):
            lReasonForTradingOrNotTrading = 'AtBestBid(NoTTQChange)'
        elif ("OpenSell(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingOpenSell) or ("CloseSell(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingCloseSell)\
            or("OpenBuy(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingOpenBuy) or ("CloseBuy(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingCloseBuy):
            lReasonForTradingOrNotTrading = 'AtBestBid(TTQDidntIncreaseBySufficientAmount_'
        elif (l_dummy_TTQChange_For_Buy > 0 ):
            if (currentLTP == g_bestqty_list_for_close_buy['price']):
                if (g_bestqty_list_for_close_buy['qty'] > l_dummy_TTQChange_For_Buy):
                    l_qty_for_buy_fill_possible = 0
                    g_bestqty_list_for_close_buy['qty'] = g_bestqty_list_for_close_buy['qty'] - l_dummy_TTQChange_For_Buy
                else:
                    l_qty_for_buy_fill_possible = l_dummy_TTQChange_For_Buy - g_bestqty_list_for_close_buy['qty']
                    g_bestqty_list_for_close_buy['qty'] = 0
                    
                if (l_qty_for_buy_fill_possible > 0):
                    lQtyForWhichWeTrade = min(pQtyForWhichFillCanBeGiven, l_qty_for_buy_fill_possible)
                    l_dummy_TTQChange_For_Buy -= lQtyForWhichWeTrade
                    lTradedPrice = g_bestqty_list_for_close_buy['price']
                    lTradedQty = lQtyForWhichWeTrade
                    lReasonForTradingOrNotTrading = pOpenOrCloseSide + 'BuyBest(Standing)'
                else:
                    lReasonForTradingOrNotTrading = 'AtBestBid(NextTickTTQDidNotIncrease)'
            elif (currentLTP < g_bestqty_list_for_close_buy['price']):
                lQtyForWhichWeTrade = min(l_dummy_TTQChange_For_Buy,pQtyForWhichFillCanBeGiven)
                l_dummy_TTQChange_For_Buy -= lQtyForWhichWeTrade
                lTradedPrice = g_bestqty_list_for_close_buy['price']
                lTradedQty = lQtyForWhichWeTrade
                lReasonForTradingOrNotTrading = pOpenOrCloseSide + 'BuyBest(Standing)' 
                if lQtyForWhichWeTrade >= g_bestqty_list_for_close_buy['qty']:
                    g_bestqty_list_for_close_buy = {}
                else:
                    g_bestqty_list_for_close_buy['qty']-=lQtyForWhichWeTrade
            else:
                lReasonForTradingOrNotTrading = 'AtBestBid(NoTTQChangeNoLTPLessThanOurPrice)'
                       
    return l_dummy_TTQChange_For_Buy, lReasonForTradingOrNotTrading, lTradedQty , lTradedPrice 

def fillForStandingAtBidForOpenBuy(pPrevObj, currentLTP, l_dummy_TTQChange_For_Buy , pQtyForWhichFillCanBeGiven, pOpenOrCloseSide , pPriceAtWhichOrderIsToBeKept):
    global g_bestqty_list_for_open_buy ,gStandingAtBidPPlusOneTickInOpenBuy
    lTradedPrice = 0
    lTradedQty = 0
    lReasonForTradingOrNotTrading = ''
    if (g_bestqty_list_for_open_buy != {} and pPriceAtWhichOrderIsToBeKept != g_bestqty_list_for_open_buy['price']) or (g_bestqty_list_for_open_buy == {}):
        g_bestqty_list_for_open_buy = {} 
        g_bestqty_list_for_open_buy['price'] = pPriceAtWhichOrderIsToBeKept
        l_qty = 0
        if g_bestqty_list_for_open_buy['price'] == gStandingAtBidPPlusOneTickInOpenBuy:
            l_qty = 0
        else:
            try:
                indexAtWhichPriceIsFound = pPrevObj.BidP.index(pPriceAtWhichOrderIsToBeKept)
                l_qty = pPrevObj.BidQ[ indexAtWhichPriceIsFound ]
            except:
                l_qty = 0
            
        g_bestqty_list_for_open_buy['qty'] = l_qty
        lReasonForTradingOrNotTrading = 'AtBestBidStartingToStand'
    else:
        if (l_dummy_TTQChange_For_Buy <= 0):
            lReasonForTradingOrNotTrading = 'AtBestBid(NoTTQChange)'
        elif ("OpenSell(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingOpenSell) or ("CloseSell(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingCloseSell)\
            or("OpenBuy(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingOpenBuy) or ("CloseBuy(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingCloseBuy):
            lReasonForTradingOrNotTrading = 'AtBestBid(TTQDidntIncreaseBySufficientAmount_'
        elif (l_dummy_TTQChange_For_Buy > 0 ):
            if (currentLTP == g_bestqty_list_for_open_buy['price']):
                if (g_bestqty_list_for_open_buy['qty'] > l_dummy_TTQChange_For_Buy):
                    l_qty_for_buy_fill_possible = 0
                    g_bestqty_list_for_open_buy['qty'] = g_bestqty_list_for_open_buy['qty'] - l_dummy_TTQChange_For_Buy
                else:
                    l_qty_for_buy_fill_possible = l_dummy_TTQChange_For_Buy - g_bestqty_list_for_open_buy['qty']
                    g_bestqty_list_for_open_buy['qty'] = 0
                    
                if (l_qty_for_buy_fill_possible > 0):
                    lQtyForWhichWeTrade = min(pQtyForWhichFillCanBeGiven, l_qty_for_buy_fill_possible)
                    l_dummy_TTQChange_For_Buy -= lQtyForWhichWeTrade
                    lTradedPrice = g_bestqty_list_for_open_buy['price']
                    lTradedQty = lQtyForWhichWeTrade
                    lReasonForTradingOrNotTrading = pOpenOrCloseSide + 'BuyBest(Standing)'
                else:
                    lReasonForTradingOrNotTrading = 'AtBestBid(NextTickTTQDidNotIncrease)'
            elif (currentLTP < g_bestqty_list_for_open_buy['price']):
                lQtyForWhichWeTrade = min(l_dummy_TTQChange_For_Buy,pQtyForWhichFillCanBeGiven)
                l_dummy_TTQChange_For_Buy -= lQtyForWhichWeTrade
                lTradedPrice = g_bestqty_list_for_open_buy['price']
                lTradedQty = lQtyForWhichWeTrade
                lReasonForTradingOrNotTrading = pOpenOrCloseSide + 'BuyBest(Standing)' 
                if lQtyForWhichWeTrade >= g_bestqty_list_for_open_buy['qty']:
                    g_bestqty_list_for_open_buy = {}
                else:
                    g_bestqty_list_for_open_buy['qty']-=lQtyForWhichWeTrade
            else:
                lReasonForTradingOrNotTrading = 'AtBestBid(NoTTQChangeNoLTPLessThanOurPrice)'
                       
    return l_dummy_TTQChange_For_Buy, lReasonForTradingOrNotTrading, lTradedQty , lTradedPrice 

def fillForStandingAtAskForCloseSell(pPrevObj, currentLTP, l_dummy_TTQChange_For_Sell , pQtyForWhichFillCanBeGiven, pOpenOrCloseSide , pPriceAtWhichOrderIsToBeKept):
    global g_bestqty_list_for_close_sell , gStandingAtAskPMinusOneTickInCloseSell ,gStandingAtBidPPlusOneTickInCloseBuy
    lTradedPrice = 0
    lTradedQty = 0
    lReasonForTradingOrNotTrading = ''
    if (g_bestqty_list_for_close_sell != {} and pPriceAtWhichOrderIsToBeKept != g_bestqty_list_for_close_sell['price']) or (g_bestqty_list_for_close_sell == {}):
        g_bestqty_list_for_close_sell = {} 
        g_bestqty_list_for_close_sell['price'] = pPriceAtWhichOrderIsToBeKept
        l_qty = 0
        if g_bestqty_list_for_close_sell['price'] == gStandingAtAskPMinusOneTickInCloseSell:
            l_qty = 0
        else:
            try:
                indexAtWhichPriceIsFound = pPrevObj.AskP.index(pPriceAtWhichOrderIsToBeKept)
                l_qty = pPrevObj.AskQ[ indexAtWhichPriceIsFound ]
            except:
                l_qty = 0
        g_bestqty_list_for_close_sell['qty'] = l_qty
        lReasonForTradingOrNotTrading = 'AtBestAskStartingToStand'
    else:
        if (l_dummy_TTQChange_For_Sell <= 0):
            lReasonForTradingOrNotTrading = 'AtBestAsk(NoTTQChange)'
        elif ("OpenSell(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingOpenSell) or ("CloseSell(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingCloseSell)\
            or("OpenBuy(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingOpenBuy) or ("CloseBuy(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingCloseBuy):
            lReasonForTradingOrNotTrading = 'AtBestAskTTQChangeBecauseOfOurOrder'
        elif (l_dummy_TTQChange_For_Sell > 0 ):
            if (currentLTP == g_bestqty_list_for_close_sell['price']):
                if (g_bestqty_list_for_close_sell['qty'] > l_dummy_TTQChange_For_Sell):
                    l_qty_for_sell_fill_possible = 0
                    g_bestqty_list_for_close_sell['qty'] = g_bestqty_list_for_close_sell['qty'] - l_dummy_TTQChange_For_Sell
                else:
                    l_qty_for_sell_fill_possible = l_dummy_TTQChange_For_Sell - g_bestqty_list_for_close_sell['qty']
                    g_bestqty_list_for_close_sell['qty'] = 0
                    
                if (l_qty_for_sell_fill_possible > 0):
                    lQtyForWhichWeTrade = min(pQtyForWhichFillCanBeGiven, l_qty_for_sell_fill_possible)
                    l_dummy_TTQChange_For_Sell -= lQtyForWhichWeTrade
                    lTradedPrice = g_bestqty_list_for_close_sell['price']
                    lTradedQty = lQtyForWhichWeTrade
                    lReasonForTradingOrNotTrading = pOpenOrCloseSide + 'SellBest(Standing)'
                else:
                    lReasonForTradingOrNotTrading = 'AtBestAsk(TTQDidntIncreaseBySufficientAmount)'
            elif (currentLTP > g_bestqty_list_for_close_sell['price']):
                lQtyForWhichWeTrade = min(l_dummy_TTQChange_For_Sell,pQtyForWhichFillCanBeGiven)
                l_dummy_TTQChange_For_Sell -= lQtyForWhichWeTrade
                lTradedPrice = g_bestqty_list_for_close_sell['price']
                lTradedQty = lQtyForWhichWeTrade
                lReasonForTradingOrNotTrading = pOpenOrCloseSide + 'SellBest(Standing)' 
                if lQtyForWhichWeTrade >= g_bestqty_list_for_close_sell['qty']:
                    g_bestqty_list_for_close_sell = {}
                else:
                    g_bestqty_list_for_close_sell['qty'] -= lQtyForWhichWeTrade
            else:
                lReasonForTradingOrNotTrading = 'AtBestAsk(NoTTQChangeNoLTPLessThanOurPrice)'
                       
    return l_dummy_TTQChange_For_Sell, lReasonForTradingOrNotTrading, lTradedQty , lTradedPrice 

def fillForStandingAtAskForOpenSell(pPrevObj, currentLTP, l_dummy_TTQChange_For_Sell , pQtyForWhichFillCanBeGiven, pOpenOrCloseSide , pPriceAtWhichOrderIsToBeKept):
    global g_bestqty_list_for_open_sell , gStandingAtAskPMinusOneTickInOpenSell
    lTradedPrice = 0
    lTradedQty = 0
    lReasonForTradingOrNotTrading = ''
    if (g_bestqty_list_for_open_sell != {} and pPriceAtWhichOrderIsToBeKept != g_bestqty_list_for_open_sell['price']) or (g_bestqty_list_for_open_sell == {}):
        g_bestqty_list_for_open_sell = {} 
        g_bestqty_list_for_open_sell['price'] = pPriceAtWhichOrderIsToBeKept
        l_qty = 0
        if g_bestqty_list_for_open_sell['price'] == gStandingAtAskPMinusOneTickInOpenSell:
            l_qty = 0
        else:
            try:
                indexAtWhichPriceIsFound = pPrevObj.AskP.index(pPriceAtWhichOrderIsToBeKept)
                l_qty = pPrevObj.AskQ[ indexAtWhichPriceIsFound ]
            except:
                l_qty = 0
        g_bestqty_list_for_open_sell['qty'] = l_qty
        lReasonForTradingOrNotTrading = 'AtBestAskStartingToStand'
    else:
        if (l_dummy_TTQChange_For_Sell <= 0):
            lReasonForTradingOrNotTrading = 'AtBestAsk(NoTTQChange)'
        elif ("OpenSell(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingOpenSell) or ("CloseSell(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingCloseSell)\
            or("OpenBuy(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingOpenBuy) or ("CloseBuy(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingCloseBuy):
            lReasonForTradingOrNotTrading = 'AtBestAskTTQChangeBecauseOfOurOrder'
        elif (l_dummy_TTQChange_For_Sell > 0 ):
            if (currentLTP == g_bestqty_list_for_open_sell['price']):
                if (g_bestqty_list_for_open_sell['qty'] > l_dummy_TTQChange_For_Sell):
                    l_qty_for_sell_fill_possible = 0
                    g_bestqty_list_for_open_sell['qty'] = g_bestqty_list_for_open_sell['qty'] - l_dummy_TTQChange_For_Sell
                else:
                    l_qty_for_sell_fill_possible = l_dummy_TTQChange_For_Sell - g_bestqty_list_for_open_sell['qty']
                    g_bestqty_list_for_open_sell['qty'] = 0
                    
                if (l_qty_for_sell_fill_possible > 0):
                    lQtyForWhichWeTrade = min(pQtyForWhichFillCanBeGiven, l_qty_for_sell_fill_possible)
                    l_dummy_TTQChange_For_Sell -= lQtyForWhichWeTrade
                    lTradedPrice = g_bestqty_list_for_open_sell['price']
                    lTradedQty = lQtyForWhichWeTrade
                    lReasonForTradingOrNotTrading = pOpenOrCloseSide + 'SellBest(Standing)'
                else:
                    lReasonForTradingOrNotTrading = 'AtBestAsk(TTQDidntIncreaseBySufficientAmount)'
            elif (currentLTP > g_bestqty_list_for_open_sell['price']):
                lQtyForWhichWeTrade = min(l_dummy_TTQChange_For_Sell,pQtyForWhichFillCanBeGiven)
                l_dummy_TTQChange_For_Sell -= lQtyForWhichWeTrade
                lTradedPrice = g_bestqty_list_for_open_sell['price']
                lTradedQty = lQtyForWhichWeTrade
                lReasonForTradingOrNotTrading = pOpenOrCloseSide + 'SellBest(Standing)' 
                if lQtyForWhichWeTrade>=g_bestqty_list_for_open_sell['qty']:
                    g_bestqty_list_for_open_sell = {}
                else:
                    g_bestqty_list_for_open_sell['qty'] = g_bestqty_list_for_open_sell['qty'] - lQtyForWhichWeTrade
            else:
                lReasonForTradingOrNotTrading = 'AtBestAsk(NoTTQChangeNoLTPLessThanOurPrice)'
                       
    return l_dummy_TTQChange_For_Sell, lReasonForTradingOrNotTrading, lTradedQty , lTradedPrice 

def checkIfPreviousDecisionToEnterOrExitTradeWasSuccessful(pCurrentObj,pPrevObj , pTradeStats):
    global gTickSize , gMaxQty , g_quantity_adjustment_list_for_sell , g_quantity_adjustment_list_for_buy , g_bestqty_list_for_close_sell, g_bestqty_list_for_close_buy ,g_bestqty_list_for_open_sell, g_bestqty_list_for_open_buy
    global gStandingAtAskPMinusOneTickInCloseSell ,gStandingAtBidPPlusOneTickInCloseBuy ,gStandingAtAskPMinusOneTickInOpenSell ,gStandingAtBidPPlusOneTickInOpenBuy, gOpenBuyFillPrice , gOpenSellFillPrice , gPipsTaken

    lOpenBuyTradedPrice = 0 
    lOpenBuyTradedQty = 0
    lOpenSellTradedPrice = 0
    lOpenSellTradedQty = 0
    lCloseBuyTradedPrice = 0 
    lCloseBuyTradedQty = 0
    lCloseSellTradedPrice = 0
    lCloseSellTradedQty = 0
    spreadAtTimeOfPreviousDataRow = pPrevObj.AskP[0] - pPrevObj.BidP[0]
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
        g_bestqty_list_for_close_buy = {}
        g_bestqty_list_for_close_sell = {}
        if pPrevObj.CloseBuy == 0:
            gStandingAtBidPPlusOneTickInCloseBuy  = 0
        if pPrevObj.CloseSell == 0:
            gStandingAtAskPMinusOneTickInCloseSell = 0
        g_bestqty_list_for_open_buy = {}
        g_bestqty_list_for_open_sell = {}
        if pPrevObj.OpenBuy == 0:
            gStandingAtBidPPlusOneTickInOpenBuy  = 0
        if pPrevObj.OpenSell == 0:
            gStandingAtAskPMinusOneTickInOpenSell = 0
        return [ pPrevObj.BidQ[0] , pPrevObj.AskQ[0] , 0 , 0 , 0 ,0 ,0, 0,0 ,0 ,0, 0]


    currentLTP = pCurrentObj.LTP
    currentTTQ = pCurrentObj.TTQ    

    l_dummy_AskQ0 = pPrevObj.AskQ[0]
    l_dummy_TTQChange_For_Buy = currentTTQ - pPrevObj.TTQ
    #close buy
    if(pPrevObj.CloseBuy < 0 ): # Need to buy we come here only if currentPosition is greater than 0 so no need to check again.
        lCloseBuyTradedPrice = 0
        lCloseBuyTradedQty = 0
        lQtyForWhichFillsCanBeGiven = pTradeStats['currentPositionShort']
        lOpenOrCloseSide = 'Close'
        lPriceAtWhichOrderIsToBeKept = 0
        if pPrevObj.CloseBuy == -2 :  
            lPriceAtWhichOrderIsToBeKept = pPrevObj.BidP[1] + ( 1 * gTickSize) 
        elif pPrevObj.CloseBuy == -1:
            lPriceAtWhichOrderIsToBeKept = pPrevObj.BidP[0] + ( 1 * gTickSize) 
        if  ( lPriceAtWhichOrderIsToBeKept == pPrevObj.BidP[0] + ( 1 * gTickSize) ) or pPrevObj.CloseBuy == -1:
            g_bestqty_list_for_close_buy = {}
            l_dummy_TTQChange_For_Buy, l_dummy_AskQ0 , lReasonForTradingOrNotTradingCloseBuy, lCloseBuyTradedQty,lCloseBuyTradedPrice = fillForStandingAtBidPlus1Pip(pPrevObj, l_dummy_AskQ0,spreadAtTimeOfPreviousDataRow,\
                                                                                                                             currentLTP, l_dummy_TTQChange_For_Buy , lQtyForWhichFillsCanBeGiven,lOpenOrCloseSide)
            gStandingAtBidPPlusOneTickInCloseBuy  = pPrevObj.BidP[0] + gTickSize 
        else:  #Standing at Bid
            l_dummy_TTQChange_For_Buy, lReasonForTradingOrNotTradingCloseBuy, lCloseBuyTradedQty,lCloseBuyTradedPrice = fillForStandingAtBidForCloseBuy(pPrevObj, currentLTP, l_dummy_TTQChange_For_Buy , lQtyForWhichFillsCanBeGiven , lOpenOrCloseSide , lPriceAtWhichOrderIsToBeKept)
            gStandingAtBidPPlusOneTickInCloseBuy = 0
        
        pTradeStats['totalBuyAmountShort'] += lCloseBuyTradedQty * lCloseBuyTradedPrice
        pTradeStats['currentPositionShort'] -= lCloseBuyTradedQty
        pTradeStats['NumberOfCloseBuy'] += lCloseBuyTradedQty
    else:
        gStandingAtBidPPlusOneTickInCloseBuy  = 0
    #open buy
    if(pPrevObj.OpenBuy > 0 and ( gMaxQty - pTradeStats['currentPositionLong'] ) > 0):
        lOpenBuyTradedPrice = 0
        lOpenBuyTradedQty = 0
        lQtyForWhichFillsCanBeGiven = gMaxQty - pTradeStats['currentPositionLong'] 
        lOpenOrCloseSide = 'Open'
        lPriceAtWhichOrderIsToBeKept = 0
        if pPrevObj.OpenBuy == 2:
            lPriceAtWhichOrderIsToBeKept = pPrevObj.BidP[1] + ( 1 * gTickSize) 
        elif pPrevObj.OpenBuy == 1:
            lPriceAtWhichOrderIsToBeKept = pPrevObj.BidP[0] + ( 1 * gTickSize) 
        if  ( lPriceAtWhichOrderIsToBeKept == pPrevObj.BidP[0] + ( 1 * gTickSize) ) or pPrevObj.OpenBuy == 1:
            g_bestqty_list_for_open_buy = {}
            l_dummy_TTQChange_For_Buy, l_dummy_AskQ0 , lReasonForTradingOrNotTradingOpenBuy, lOpenBuyTradedQty,lOpenBuyTradedPrice = fillForStandingAtBidPlus1Pip(pPrevObj, l_dummy_AskQ0,spreadAtTimeOfPreviousDataRow,\
                                                                                                                     currentLTP, l_dummy_TTQChange_For_Buy , lQtyForWhichFillsCanBeGiven,lOpenOrCloseSide)
            gStandingAtBidPPlusOneTickInOpenBuy  = pPrevObj.BidP[0] + gTickSize 
        else:  #Standing at Bid
            l_dummy_TTQChange_For_Buy, lReasonForTradingOrNotTradingOpenBuy, lOpenBuyTradedQty,lOpenBuyTradedPrice = fillForStandingAtBidForOpenBuy(pPrevObj, currentLTP, l_dummy_TTQChange_For_Buy , lQtyForWhichFillsCanBeGiven , lOpenOrCloseSide , lPriceAtWhichOrderIsToBeKept)
            gStandingAtBidPPlusOneTickInOpenBuy = 0
                        
        pTradeStats['totalBuyAmountLong'] += lOpenBuyTradedQty * lOpenBuyTradedPrice
        pTradeStats['currentPositionLong'] += lOpenBuyTradedQty
        pTradeStats['NumberOfOpenBuy'] += lOpenBuyTradedQty
    else:
        gStandingAtBidPPlusOneTickInOpenBuy = 0
    
    l_dummy_BidQ0 = pPrevObj.BidQ[0]
    l_dummy_TTQChange_For_Sell = currentTTQ - pPrevObj.TTQ
    #Close Sell
    if(pPrevObj.CloseSell < 0):
        lCloseSellTradedPrice = 0
        lCloseSellTradedQty = 0
        lQtyForWhichFillsCanBeGiven = pTradeStats['currentPositionLong'] 
        lOpenOrCloseSide = 'Close'         
        lPriceAtWhichOrderIsToBeKept = 0 
        if pPrevObj.CloseSell == -2: 
            lPriceAtWhichOrderIsToBeKept =  pPrevObj.AskP[1] - ( 1 * gTickSize) 
        else:
            lPriceAtWhichOrderIsToBeKept =  pPrevObj.AskP[0] - ( 1 * gTickSize) 
        if  ( lPriceAtWhichOrderIsToBeKept == pPrevObj.AskP[0] - ( 1 * gTickSize) ) or pPrevObj.CloseSell == -1:
            g_bestqty_list_for_close_sell = {} #Standing at Ask +1 
            l_dummy_TTQChange_For_Sell,l_dummy_BidQ0,lReasonForTradingOrNotTradingCloseSell,lCloseSellTradedQty,lCloseSellTradedPrice = fillForStandingAtAskMinus1Pip(pPrevObj, l_dummy_BidQ0,spreadAtTimeOfPreviousDataRow,\
                                                                                                                             currentLTP, l_dummy_TTQChange_For_Sell , lQtyForWhichFillsCanBeGiven,lOpenOrCloseSide)
            gStandingAtAskPMinusOneTickInCloseSell = pPrevObj.AskP[0] - gTickSize
        else: #Standing at Ask
            l_dummy_TTQChange_For_Sell,lReasonForTradingOrNotTradingCloseSell,lCloseSellTradedQty,lCloseSellTradedPrice = fillForStandingAtAskForCloseSell(pPrevObj, currentLTP, l_dummy_TTQChange_For_Sell , lQtyForWhichFillsCanBeGiven , lOpenOrCloseSide , lPriceAtWhichOrderIsToBeKept)
            gStandingAtAskPMinusOneTickInCloseSell = 0
            
        pTradeStats['totalSellAmountLong'] += lCloseSellTradedQty * lCloseSellTradedPrice
        pTradeStats['currentPositionLong'] -= lCloseSellTradedQty
        pTradeStats['NumberOfCloseSell'] += lCloseSellTradedQty
    else:
        gStandingAtAskPMinusOneTickInCloseSell = 0
    
    #Open Sell
    if pPrevObj.OpenSell > 0 and (gMaxQty - pTradeStats['currentPositionShort'] ) > 0 :
        lOpenSellTradedPrice = 0
        lOpenSellTradedQty = 0
        lQtyForWhichFillsCanBeGiven = ( gMaxQty - pTradeStats['currentPositionShort'] )
        lOpenOrCloseSide = 'Open'
        lPriceAtWhichOrderIsToBeKept = 0 
        if pPrevObj.OpenSell == 2: 
            lPriceAtWhichOrderIsToBeKept =  pPrevObj.AskP[1] - ( 1 * gTickSize) 
        else:
            lPriceAtWhichOrderIsToBeKept =  pPrevObj.AskP[0] - ( 1 * gTickSize) 
                    
        if  ( lPriceAtWhichOrderIsToBeKept == pPrevObj.AskP[0] - ( 1 * gTickSize) ) or pPrevObj.OpenSell == 1: 
            g_bestqty_list_for_open_sell = {} #Standing at Ask +1 
            l_dummy_TTQChange_For_Sell,l_dummy_BidQ0,lReasonForTradingOrNotTradingOpenSell,lOpenSellTradedQty,lOpenSellTradedPrice = fillForStandingAtAskMinus1Pip(pPrevObj, l_dummy_BidQ0,spreadAtTimeOfPreviousDataRow,\
                                                                                                        currentLTP, l_dummy_TTQChange_For_Sell , lQtyForWhichFillsCanBeGiven,lOpenOrCloseSide)
            gStandingAtAskPMinusOneTickInOpenSell = pPrevObj.AskP[0] - gTickSize
        else:
            l_dummy_TTQChange_For_Sell,lReasonForTradingOrNotTradingOpenSell,lOpenSellTradedQty,lOpenSellTradedPrice = fillForStandingAtAskForOpenSell(pPrevObj, currentLTP, l_dummy_TTQChange_For_Sell , lQtyForWhichFillsCanBeGiven , lOpenOrCloseSide , lPriceAtWhichOrderIsToBeKept)
            gStandingAtAskPMinusOneTickInOpenSell = 0            
        pTradeStats['totalSellAmountShort'] += lOpenSellTradedQty * lOpenSellTradedPrice
        pTradeStats['currentPositionShort'] += lOpenSellTradedQty
        pTradeStats['NumberOfOpenSell'] += lOpenSellTradedQty
    else:
        gStandingAtAskPMinusOneTickInOpenSell = 0 
                                      
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
    else:
        l_obj.AskP[0]  = float(pCurrentDataRow[colNumberOfData.BestAskP])
        l_obj.BidP[0]  = float(pCurrentDataRow[colNumberOfData.BestBidP])
        l_obj.AskQ[0] = int(pCurrentDataRow[colNumberOfData.BestAskQ])
        l_obj.BidQ[0] = int(pCurrentDataRow[colNumberOfData.BestBidQ])
        l_obj.AskP[1] = float(pCurrentDataRow[colNumberOfData.BestAskP1])
        l_obj.BidP[1] = float(pCurrentDataRow[colNumberOfData.BestBidP1])
        l_obj.AskQ[1] = int(pCurrentDataRow[colNumberOfData.BestAskQ1])
        l_obj.BidQ[1] = int(pCurrentDataRow[colNumberOfData.BestBidQ1])              
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
    

def readOnceAndWrite(pFileName, entryCL , exitCL , predictedValuesList):
    global g_bestqty_list_for_close_sell, g_bestqty_list_for_close_buy ,g_bestqty_list_for_open_sell, g_bestqty_list_for_open_buy 
    global transactionCost , currencyDivisor
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
    currentIndex = 0
    l_previous_obj = None
    l_obj= None
    print("Processing the data file for trades :")
    attribute.initList()
    print("EntryLevels",entryCL , exitCL)
    for currentDataRow,pObj in zip(dataFile.matrix[10000:],predictedValuesList):
        
        l_obj = update_obj_list(currentDataRow,pObj)
        if(l_previous_obj != None):
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
                                         str(l_previous_obj.TTQ) , str(l_previous_obj.LTP) ,str(l_previous_obj.fA),str(l_previous_obj.fB),str(l_previous_obj.fC),\
                                         str(l_previous_obj.fD),str(l_previous_obj.fE),str(l_previous_obj.fA1),str(l_previous_obj.fB1),str(l_previous_obj.fC1),str(l_previous_obj.fD1),str(l_previous_obj.fE1),\
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
            
            #Open Sell and Close Buy
            if((l_obj.currentBuyPredictedValue1 >= exitCL )and tradeStats['currentPositionShort'] > 0):
                g_bestqty_list_for_close_buy = {}
                l_obj.CloseBuy = -1       #For close by hitting
                

            if(l_obj.currentSellPredictedValue1 >= entryCL and tradeStats['currentPositionLong'] == 0):
                g_bestqty_list_for_open_sell = {}
                l_obj.OpenSell = 1    #For open buy
                
            if(l_obj.currentBuyPredictedValue2 >= .40 and tradeStats['currentPositionShort'] > 0) and (l_obj.CloseBuy != -1) :
                l_obj.CloseBuy = -2
            if(l_obj.currentSellPredictedValue2 >= .45 and tradeStats['currentPositionLong'] == 0) and (l_obj.OpenSell != 1) :
                l_obj.OpenSell = 2
            
            
            
            #Open Buy and Close Sell

            if(l_obj.currentSellPredictedValue1 >= exitCL and tradeStats['currentPositionLong'] > 0):
                g_bestqty_list_for_close_sell = {}
                l_obj.CloseSell = -1       #For close by hitting
                
            if(l_obj.currentBuyPredictedValue1 >= entryCL and tradeStats['currentPositionShort'] == 0) :
                g_bestqty_list_for_open_buy = {}
                l_obj.OpenBuy = 1       #For close by hitting
                 
            if(l_obj.currentSellPredictedValue2 >= .40 and tradeStats['currentPositionLong'] > 0) and (l_obj.CloseSell != -1)  :
                l_obj.CloseSell = -2   
            if  (l_obj.currentBuyPredictedValue2 >= .45 and tradeStats['currentPositionShort'] == 0) and (l_obj.OpenBuy != 1):          
                l_obj.OpenBuy = 2
        
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
    
    attribute.aList[currentIndex-1][0] = currentTimeStamp
    attribute.aList[currentIndex-1][1] = tradeStats['currentPositionLong']
    attribute.aList[currentIndex-1][2] = tradeStats['currentPositionShort']
    if(g_bestqty_list_for_close_buy != {}):
        l_best_bidq = g_bestqty_list_for_close_buy['qty']
        l_best_bidp = g_bestqty_list_for_close_buy['price'] 
    else:
        l_best_bidq = 0
        l_best_bidp = 0
    if(g_bestqty_list_for_close_sell != {}):
        l_best_askq = g_bestqty_list_for_close_sell['qty']
        l_best_askp = g_bestqty_list_for_close_sell['price'] 
    else:
        l_best_askq = 0
        l_best_askp = 0
    listOfStringsToPrint = [  str(l_previous_obj.BidQ[0]) , str(l_previous_obj.BidP[0]),str(l_previous_obj.BidQ[1]) , str(l_previous_obj.BidP[1]),\
                                         str(l_previous_obj.AskQ[0]) , str(l_previous_obj.AskP[0]) , str(l_previous_obj.AskQ[1]) , str(l_previous_obj.AskP[1]) ,\
                                         str(l_previous_obj.TTQ) , str(l_previous_obj.LTP) ,str(l_previous_obj.fA),str(l_previous_obj.fB),str(l_previous_obj.fC),\
                                         str(l_previous_obj.fD),str(l_previous_obj.fE),str(l_previous_obj.fA1),str(l_previous_obj.fB1),str(l_previous_obj.fC1),str(l_previous_obj.fD1),str(l_previous_obj.fE1),\
                                         str(l_previous_obj.currentBuyPredictedValue1) , str(l_previous_obj.currentSellPredictedValue1),str(l_previous_obj.currentBuyPredictedValue2) , str(l_previous_obj.currentSellPredictedValue2) , \
                                         str(l_previous_obj.OpenBuy) ,l_previous_obj.ReasonForTradingOrNotTradingOpenBuy ,str(l_previous_obj.CloseBuy) ,l_previous_obj.ReasonForTradingOrNotTradingCloseBuy , \
                                        str(l_previous_obj.OpenSell) ,l_previous_obj.ReasonForTradingOrNotTradingOpenSell ,str(l_previous_obj.CloseSell) ,l_previous_obj.ReasonForTradingOrNotTradingCloseSell  , \
                                        str(tradeStats['NumberOfCloseBuy']),str(tradeStats['NumberOfOpenBuy']),\
                                        str(tradeStats['NumberOfCloseBuy']),str(tradeStats['NumberOfOpenSell']),\
                                        str(tradeStats['NumberOfCloseSell']),str(lDummyBidQ0),str(lDummyAskQ0),\
                                        str(lDummyTTQForBuy),str(lDummyTTQForSell),str(l_best_bidq),str(l_best_bidp),str(l_best_askp), str(l_best_askq) , "0;0;0;0"]
    attribute.aList[currentIndex-1][3] =  ";".join(listOfStringsToPrint) 
    
    dirName = args.pd.replace('/ro/','/rs/')
    tradeLogMainDirName = dirName+"/t/"
    if not os.path.exists(tradeLogMainDirName):
        os.mkdir(tradeLogMainDirName)
    tradeLogSubDirectoryName =  tradeLogMainDirName + mainExperimentName+"/"
    if not os.path.exists(tradeLogSubDirectoryName):
        os.mkdir(tradeLogSubDirectoryName)
    
    fileName = tradeLogSubDirectoryName + pFileName + ".trade" 
    lHeaderColumnNamesList  = ['TimeStamp','CurrentPositionLong','CurrentPositionShort','BidQ0;BidP0;BidQ1;BidP1','AskQ0;AskP0;AskQ1;AskP1','TTQ','LTP',\
                               'f0;f1;f2;f3;f4;f60;f61;f62;f63;f64', 'CurBuyPredValue5Level','CurrentSellPredValue5Level','CurBuyPredValue6Level','CurrentSellPredValue6Level',\
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
    lIndexOfEntryOrExitCL = 0
    lWFDirName = args.pd.replace('/ro/','/wf/')
    featureAFileObject5Levels = open(lWFDirName+'/f/fColBidP0InCurrentRow[DivideBy]fWAPriceOfCol_FeatureBQAvgFor600_InLast1.5Secs-iT.ICICIBANK-oT.0-sP.-1.feature',"r")
    featureBFileObject5Levels = open(lWFDirName+'/f/fColAskP0InCurrentRow[DivideBy]fWAPriceOfCol_FeatureAQAvgFor600_InLast1.5Secs-iT.ICICIBANK-oT.0-sP.-1.feature',"r")
    featureCFileObject5Levels = open(lWFDirName+'/f/fCol_Feature1.5AmB600_InCurrentRow[DivideBy]fMovingAverageOfCol_Feature1.5AmB600_InLast1000Rows-iT.ICICIBANK-oT.0-sP.-1.feature',"r")
    featureDFileObject5Levels = open(lWFDirName+'/f/fColBidP0InCurrentRow[DivideBy]fInverseWAInLast3Levels-iT.ICICIBANK-oT.0-sP.-1.feature',"r")
    featureEFileObject5Levels = open(lWFDirName+'/f/fColAskP0InCurrentRow[DivideBy]fInverseWAInLast3Levels-iT.ICICIBANK-oT.0-sP.-1.feature',"r")

    featureAFileObject6Levels = open(lWFDirName+'/f/fColBidP1InCurrentRow[DivideBy]fWAPriceOfCol_FeatureBQAvgFor600For6Levels_InLast1.5SecsFor6Levels-iT.ICICIBANK-oT.0-sP.-1.feature',"r")
    featureBFileObject6Levels = open(lWFDirName+'/f/fColAskP1InCurrentRow[DivideBy]fWAPriceOfCol_FeatureAQAvgFor600For6Levels_InLast1.5SecsFor6Levels-iT.ICICIBANK-oT.0-sP.-1.feature',"r")
    featureCFileObject6Levels = open(lWFDirName+'/f/fCol_Feature1.5AmB600For6L_InCurrentRow[DivideBy]fMovingAverageOfCol_Feature1.5AmB600For6L_InLast1000Rows-iT.ICICIBANK-oT.0-sP.-1.feature',"r")
    featureDFileObject6Levels = open(lWFDirName+'/f/fColBidP1InCurrentRow[DivideBy]fInverseWAInLast3LevelsFor6-iT.ICICIBANK-oT.0-sP.-1.feature',"r")
    featureEFileObject6Levels = open(lWFDirName+'/f/fColAskP1InCurrentRow[DivideBy]fInverseWAInLast3LevelsFor6-iT.ICICIBANK-oT.0-sP.-1.feature',"r")
            
    lListOfAllPredcitionValues = getPredictionsIntoObjectList(featureAFileObject5Levels,featureBFileObject5Levels,featureCFileObject5Levels,featureDFileObject5Levels,featureEFileObject5Levels,\
                                                              featureAFileObject6Levels,featureBFileObject6Levels,featureCFileObject6Levels,featureDFileObject6Levels,featureEFileObject6Levels)
    for lFileName in initialFileName:
        entryCL = float("." + gEntryCLList[lIndexOfEntryOrExitCL] )
        exitCL = float("." + gExitCLList[lIndexOfEntryOrExitCL] )
        readOnceAndWrite(lFileName,entryCL,exitCL, lListOfAllPredcitionValues)
        lIndexOfEntryOrExitCL = lIndexOfEntryOrExitCL + 1
      
if __name__ == "__main__":

    dirName = args.pd.replace('/ro/','/rs/')
    checkAllFilesAreExistOrNot = 'false'
      
    lWFDirName = args.pd.replace('/ro/','/wf/')
    predictedBuyValuesFileName = lWFDirName+"/p/"+mainExperimentName+"/"+args.a + 'buy' + '-td.' + os.path.basename(os.path.abspath(args.td)) + '-dt.' + \
    args.dt + '-targetClass.' + args.targetClass + '-f.' + experimentName + "-wt." + args.wt+ attribute.generateExtension() + ".predictions"
      
    predictedSellValuesFileName = lWFDirName+"/p/"+mainExperimentName+"/"+args.a + 'sell' + '-td.' + os.path.basename(os.path.abspath(args.td)) + '-dt.' +\
    args.dt + '-targetClass.' + args.targetClass + '-f.' + experimentName + "-wt." + args.wt+ attribute.generateExtension() + ".predictions"
      
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


