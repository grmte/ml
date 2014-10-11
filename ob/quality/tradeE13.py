#!/usr/bin/python
from __future__ import division
from __future__ import print_function
import os, sys, argparse
from configobj import ConfigObj

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

gEntryCLList = args.entryCL.split(";")
gExitCLList = args.exitCL.split(";")

initialFileName = []
for indexOfCL in range(0,len(gEntryCLList)):
    lInitialFileName = args.a + '-td.' + os.path.basename(os.path.abspath(args.td)) + \
                   '-dt.' + args.dt + '-targetClass.' + args.targetClass + '-f.' + experimentName + "-wt." + args.wt+ attribute.generateExtension() + \
                   '-l.'+gEntryCLList[indexOfCL]+"_"+gExitCLList[indexOfCL] + "-tq." + args.orderQty + "-te.13" 
    initialFileName.append(lInitialFileName)
    
g_quantity_adjustment_list_for_sell = {}
g_quantity_adjustment_list_for_buy = {}
g_bestqty_list_for_sell = {}
g_bestqty_list_for_buy = {}
class ticks_values_to_be_stored(object):
    def __init__(self):
        self.MsgCode = ''
        self.OrderType = ''
        self.NewP = 0.0
        self.NewQ = 0
        self.OldP = 0.0
        self.OldQ = 0
        self.AskP = [0.0,0.0,0.0,0.0,0.0]
        self.AskQ = [0,0,0,0,0]
        self.BidP = [0.0,0.0,0.0,0.0,0.0]
        self.BidQ = [0,0,0,0,0]
        self.LTP = 0.0
        self.TTQ  = 0
        self.currentTimeStamp = 0.0
        self.EnterTradeShort = 0
        self.EnterTradeLong = 0
        self.CloseBuyTradeHappened= 0
        self.OpenBuyTradeHappened = 0
        self.OpenSellTradeHappened = 0
        self.CloseSellTradeHappened= 0
        self.ReasonForTradingOrNotTradingShort = ""
        self.ReasonForTradingOrNotTradingLong = ""
        self.currentBuyPredictedValue = 0
        self.currentSellPredictedValue = 0
    
def functionToReadPredictionFileToDictionary(pPredictedValuesFile,pPredictedValuesDict,pFileHeader):
    lNumberOfLinesInPredictedValuesFile = 0
    for line in pPredictedValuesFile:
        if pFileHeader == True:
            pFileHeader = False
            continue
        line=line.rstrip('\n')
        splitLine = line.split(',')
        timeStamp = float(splitLine[1])
        try:#TODO: remove this and then run the code to identify errors.
            predictedProb = float(splitLine[2])
        except:
            predictedProb = 0
        pPredictedValuesDict[timeStamp] = predictedProb
        lNumberOfLinesInPredictedValuesFile += 1
    return lNumberOfLinesInPredictedValuesFile

def getPredictedValuesIntoDict(pPredictedValuesDict):
    # The following will take care if args.e = "ob/e1/" or args.e = "ob/e1"
    dirName = args.pd.replace('/ro/','/wf/')
    config = ConfigObj(args.e+"/design.ini")
    target = config["target"]
    lPredictedBuyValuesDict = dict()
    predictedBuyValuesFileName = dirName+"/p/"+mainExperimentName+"/"+args.a + target.keys()[0] + '-td.' + os.path.basename(os.path.abspath(args.td)) + \
                                 '-dt.' + args.dt + '-targetClass.' + args.targetClass + '-f.' + experimentName + "-wt." + args.wt+ attribute.generateExtension() + ".predictions"
    print("Buy Predicted values file : "+ predictedBuyValuesFileName)
    sys.stdout.flush()
    predictedBuyValuesFile = open(predictedBuyValuesFileName)
    fileHasHeader = True
    numberOfLinesInBuyPredictedValuesFile = functionToReadPredictionFileToDictionary(predictedBuyValuesFile,lPredictedBuyValuesDict,fileHasHeader)
    print("Finished reading the buy predicted values file")    
    print("The number of elements in the buy predicted values dictionary is : " + str(len(lPredictedBuyValuesDict)))
    if (numberOfLinesInBuyPredictedValuesFile != len(lPredictedBuyValuesDict)):
        print("Number of duplicate time stamps rejected in buy predicted values dictionary = " + str(numberOfLinesInBuyPredictedValuesFile - len(lPredictedBuyValuesDict)))
        #os._exit(-1)
    sys.stdout.flush()

    lPredictedSellValuesDict = dict()
    predictedSellValuesFileName = dirName+"/p/"+mainExperimentName+"/"+args.a + target.keys()[1] + '-td.' + os.path.basename(os.path.abspath(args.td)) + \
                                 '-dt.' + args.dt + '-targetClass.' + args.targetClass + '-f.' + experimentName +  "-wt." + args.wt + attribute.generateExtension()+ ".predictions"
    print("Sell Predicted values file : "+ predictedSellValuesFileName)
    sys.stdout.flush()
    predictedSellValuesFile = open(predictedSellValuesFileName)
    fileHasHeader = True
    numberOfLinesInSellPredictedValuesFile = functionToReadPredictionFileToDictionary(predictedSellValuesFile,lPredictedSellValuesDict,fileHasHeader)
    print("Finished reading the sell predicted values file")    
    print("The number of elements in the sell predicted values dictionary is : " + str(len(lPredictedSellValuesDict)))
    if (numberOfLinesInSellPredictedValuesFile != len(lPredictedSellValuesDict)):
        print("Number of duplicate timestamps rejected in sell predicted values dictionary = " + str(numberOfLinesInSellPredictedValuesFile - len(lPredictedSellValuesDict)))
        #os._exit(-1)
    sys.stdout.flush()
#-----------------Getting predicted values into dictionary -------------------------------------
    for elements in lPredictedBuyValuesDict.keys():
        pPredictedValuesDict[elements] = {}
        pPredictedValuesDict[elements]['buy'] = lPredictedBuyValuesDict[elements]
        pPredictedValuesDict[elements]['sell'] = lPredictedSellValuesDict[elements] 

def fillsForHittingAtAsk(pPrevObj, p_dummy_AskQ0 , pQtyForWhichFillCanBeGiven, pOpenOrCloseSide):
    global g_quantity_adjustment_list_for_buy
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
        lTradedQty = l_buy_qty
        p_dummy_AskQ0 -= l_buy_qty
        lReasonForTradingOrNotTrading = pOpenOrCloseSide + 'Buy(Hitting)'
    else:
        lReasonForTradingOrNotTrading = "DummyAskQExhuasted"
    return p_dummy_AskQ0, lReasonForTradingOrNotTrading, lTradedQty, lTradedPrice

def fillsForHittingAtBid(pPrevObj, p_dummy_BidQ0, pQtyForWhichFillCanBeGiven, pOpenOrCloseSide ):
    global g_quantity_adjustment_list_for_sell
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
        lTradedQty = lQtyForWhichWeTrade
        p_dummy_BidQ0 -= lQtyForWhichWeTrade
        lReasonForTradingOrNotTrading = pOpenOrCloseSide + 'Sell(Hitting)'
    else:
        lReasonForTradingOrNotTrading = "DummyBidQExhuasted"
    return p_dummy_BidQ0 , lReasonForTradingOrNotTrading, lTradedQty, lTradedPrice

def fillForStandingAtBidPlus1Pip(pPrevObj, p_dummy_AskQ0, spreadAtTimeOfPreviousDataRow, currentLTP, l_dummy_TTQChange_For_Buy, pQtyForWhichFillCanBeGiven , pOpenOrCloseSide):
    global gTickSize , gMaxQty , g_quantity_adjustment_list_for_sell , g_quantity_adjustment_list_for_buy , g_bestqty_list_for_sell, g_bestqty_list_for_buy
    lTradedPrice = 0
    lTradedQty = 0
    lReasonForTradingOrNotTrading = ''
    #standing 
    if spreadAtTimeOfPreviousDataRow > gTickSize:
        if (l_dummy_TTQChange_For_Buy <= 0):
            lReasonForTradingOrNotTrading = '(Spread>Pip)&&(NextTickTTQDidNotIncrease)'
        elif (currentLTP != pPrevObj.BidP[0]):
            lReasonForTradingOrNotTrading = '(Spread>Pip)&&(LTP!=Bid)'
        elif ("OpenSell(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingShort) or ("CloseSell(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingLong):
            lReasonForTradingOrNotTrading = 'TTQChangeBecauseOfOurOrder'
        else:
            
            lTradedQty = min(pQtyForWhichFillCanBeGiven,l_dummy_TTQChange_For_Buy)
            l_dummy_TTQChange_For_Buy -= lTradedQty
            lTradedPrice = (pPrevObj.BidP[0] + gTickSize)
            lReasonForTradingOrNotTrading = pOpenOrCloseSide + 'Buy(Standing)'
    #hitting
    else:
        p_dummy_AskQ0, lReasonForTradingOrNotTrading, lTradedQty, lTradedPrice = fillsForHittingAtAsk(pPrevObj, p_dummy_AskQ0 ,pQtyForWhichFillCanBeGiven, pOpenOrCloseSide)
    return l_dummy_TTQChange_For_Buy, p_dummy_AskQ0 , lReasonForTradingOrNotTrading, lTradedQty , lTradedPrice

def fillForStandingAtAskMinus1Pip(pPrevObj, p_dummy_BidQ0, spreadAtTimeOfPreviousDataRow, currentLTP, l_dummy_TTQChange_For_Sell, pQtyForWhichFillCanBeGiven , pOpenOrCloseSide):
    global gTickSize , gMaxQty , g_quantity_adjustment_list_for_sell , g_quantity_adjustment_list_for_buy , g_bestqty_list_for_sell, g_bestqty_list_for_buy
    lTradedPrice = 0
    lTradedQty = 0
    lReasonForTradingOrNotTrading = ''
    #standing
    if spreadAtTimeOfPreviousDataRow > gTickSize:
        if (l_dummy_TTQChange_For_Sell <= 0):
            lReasonForTradingOrNotTrading = '(Spread>Pip)&&(NextTickTTQDidNotIncrease)'
        elif (currentLTP != pPrevObj.AskP[0]):
            lReasonForTradingOrNotTrading = '(Spread>Pip)&&(NextTickLTP!=Ask)'
        elif ("OpenSell(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingShort) or ("CloseSell(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingLong):
            lReasonForTradingOrNotTrading = 'TTQChangeBecauseOfOurOrder'
        else:
            
            lQtyForWhichWeTrade = min(pQtyForWhichFillCanBeGiven, l_dummy_TTQChange_For_Sell)
            lTradedPrice = pPrevObj.AskP[0] - gTickSize
            lTradedQty = lQtyForWhichWeTrade
            l_dummy_TTQChange_For_Sell -= lQtyForWhichWeTrade
            lReasonForTradingOrNotTrading = pOpenOrCloseSide + 'Sell(Standing)'
    #hitting
    else: 
        p_dummy_BidQ0,lReasonForTradingOrNotTrading,lTradedQty,lTradedPrice = fillsForHittingAtBid(pPrevObj, p_dummy_BidQ0, pQtyForWhichFillCanBeGiven, pOpenOrCloseSide)
    return l_dummy_TTQChange_For_Sell , p_dummy_BidQ0 , lReasonForTradingOrNotTrading , lTradedQty , lTradedPrice

def fillForStandingAtBid(pPrevObj, currentLTP, l_dummy_TTQChange_For_Buy , pQtyForWhichFillCanBeGiven, pOpenOrCloseSide , pPriceAtWhichOrderIsToBeKept):
    global g_bestqty_list_for_buy 
    lTradedPrice = 0
    lTradedQty = 0
    lReasonForTradingOrNotTrading = ''
    print(pPriceAtWhichOrderIsToBeKept)
    if (g_bestqty_list_for_buy != {} and pPriceAtWhichOrderIsToBeKept != g_bestqty_list_for_buy['price']) or (g_bestqty_list_for_buy == {}):
        g_bestqty_list_for_buy = {} 
        g_bestqty_list_for_buy['price'] = pPriceAtWhichOrderIsToBeKept
        l_qty = 0
        try:
            indexAtWhichPriceIsFound = pPrevObj.BidP.index(pPriceAtWhichOrderIsToBeKept)
            l_qty = pPrevObj.BidQ[ indexAtWhichPriceIsFound ]
        except:
            for price,qty in zip(pPrevObj.BidP,pPrevObj.BidQ):
                if price > pPriceAtWhichOrderIsToBeKept:
                    l_qty = l_qty + qty
            
        g_bestqty_list_for_buy['qty'] = l_qty
        
    else:
        if (l_dummy_TTQChange_For_Buy <= 0):
            lReasonForTradingOrNotTrading = 'StandingAtBid(NextTickTTQDidNotIncrease)'
        elif ("OpenBuy(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingShort) or ("CloseBuy(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingLong):
            lReasonForTradingOrNotTrading = 'AtBestBidTTQChangeBecauseOfOurOrder'
        elif (l_dummy_TTQChange_For_Buy > 0 ):
            import pdb
            pdb.set_trace()
            if (currentLTP == g_bestqty_list_for_buy['price']):
                if (g_bestqty_list_for_buy['qty'] > l_dummy_TTQChange_For_Buy):
                    l_qty_for_buy_fill_possible = 0
                    g_bestqty_list_for_buy['qty'] = g_bestqty_list_for_buy['qty'] - l_dummy_TTQChange_For_Buy
                else:
                    l_qty_for_buy_fill_possible = l_dummy_TTQChange_For_Buy - g_bestqty_list_for_buy['qty']
                    g_bestqty_list_for_buy['qty'] = 0
                    g_bestqty_list_for_buy = {}
                    
                if (l_qty_for_buy_fill_possible > 0):
                    lQtyForWhichWeTrade = min(pQtyForWhichFillCanBeGiven, l_qty_for_buy_fill_possible)
                    l_dummy_TTQChange_For_Buy -= lQtyForWhichWeTrade
                    lTradedPrice = g_bestqty_list_for_buy['price']
                    lTradedQty = lQtyForWhichWeTrade
                    lReasonForTradingOrNotTrading = pOpenOrCloseSide + 'BuyBest(Standing)'
                else:
                    lReasonForTradingOrNotTrading = 'AtBestBid2(NextTickTTQDidNotIncrease)'
            elif (currentLTP < g_bestqty_list_for_buy['price']):
                lQtyForWhichWeTrade = pQtyForWhichFillCanBeGiven
                l_dummy_TTQChange_For_Buy -= lQtyForWhichWeTrade
                lTradedPrice = g_bestqty_list_for_buy['price']
                lTradedQty = lQtyForWhichWeTrade
                lReasonForTradingOrNotTrading = pOpenOrCloseSide + 'BuyBest(Standing)' 
                g_bestqty_list_for_buy = {}
                       
    return l_dummy_TTQChange_For_Buy, lReasonForTradingOrNotTrading, lTradedQty , lTradedPrice 

def fillForStandingAtAsk(pPrevObj, currentLTP, l_dummy_TTQChange_For_Sell , pQtyForWhichFillCanBeGiven, pOpenOrCloseSide , pPriceAtWhichOrderIsToBeKept):
    global g_bestqty_list_for_sell 
    lTradedPrice = 0
    lTradedQty = 0
    lReasonForTradingOrNotTrading = ''
    if (g_bestqty_list_for_sell != {} and pPriceAtWhichOrderIsToBeKept != g_bestqty_list_for_sell['price']) or (g_bestqty_list_for_sell == {}):
        g_bestqty_list_for_sell = {} 
        g_bestqty_list_for_sell['price'] = pPriceAtWhichOrderIsToBeKept
        l_qty = 0
        try:
            indexAtWhichPriceIsFound = pPrevObj.AskP.index(pPriceAtWhichOrderIsToBeKept)
            l_qty = pPrevObj.AskQ[ indexAtWhichPriceIsFound ]
        except:
            for price,qty in zip(pPrevObj.AskP,pPrevObj.AskQ):
                if price < pPriceAtWhichOrderIsToBeKept:
                    l_qty = l_qty + qty
            
        g_bestqty_list_for_sell['qty'] = l_qty
        
    else:
        if (l_dummy_TTQChange_For_Sell <= 0):
            lReasonForTradingOrNotTrading = 'StandingAtAsk(NextTickTTQDidNotIncrease)'
        elif ("OpenSell(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingShort) or ("CloseSell(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingLong):
            lReasonForTradingOrNotTrading = 'AtBestAskTTQChangeBecauseOfOurOrder'
        elif (l_dummy_TTQChange_For_Sell > 0 ):
            if (currentLTP == g_bestqty_list_for_sell['price']):
                if (g_bestqty_list_for_sell['qty'] > l_dummy_TTQChange_For_Sell):
                    l_qty_for_sell_fill_possible = 0
                    g_bestqty_list_for_sell['qty'] = g_bestqty_list_for_sell['qty'] - l_dummy_TTQChange_For_Sell
                else:
                    l_qty_for_sell_fill_possible = l_dummy_TTQChange_For_Sell - g_bestqty_list_for_sell['qty']
                    g_bestqty_list_for_sell['qty'] = 0
                    g_bestqty_list_for_sell = {}
                    
                if (l_qty_for_sell_fill_possible > 0):
                    lQtyForWhichWeTrade = min(pQtyForWhichFillCanBeGiven, l_qty_for_sell_fill_possible)
                    l_dummy_TTQChange_For_Sell -= lQtyForWhichWeTrade
                    lTradedPrice = g_bestqty_list_for_sell['price']
                    lTradedQty = lQtyForWhichWeTrade
                    lReasonForTradingOrNotTrading = pOpenOrCloseSide + 'SellBest(Standing)'
                else:
                    lReasonForTradingOrNotTrading = 'AtBestAsk2(NextTickTTQDidNotIncrease)'
            elif (currentLTP < g_bestqty_list_for_sell['price']):
                lQtyForWhichWeTrade = pQtyForWhichFillCanBeGiven
                l_dummy_TTQChange_For_Sell -= lQtyForWhichWeTrade
                lTradedPrice = g_bestqty_list_for_sell['price']
                lTradedQty = lQtyForWhichWeTrade
                lReasonForTradingOrNotTrading = pOpenOrCloseSide + 'SellBest(Standing)' 
                g_bestqty_list_for_sell = {}
                       
    return l_dummy_TTQChange_For_Sell, lReasonForTradingOrNotTrading, lTradedQty , lTradedPrice 

def checkIfPreviousDecisionToEnterOrExitTradeWasSuccessful(pCurrentObj,pPrevObj , pTradeStats):
    global gTickSize , gMaxQty , g_quantity_adjustment_list_for_sell , g_quantity_adjustment_list_for_buy , g_bestqty_list_for_sell, g_bestqty_list_for_buy
    lBuyTradedPrice = 0 
    lBuyTradedQty = 0
    lSellTradedPrice = 0
    lSellTradedQty = 0
    spreadAtTimeOfPreviousDataRow = pPrevObj.AskP[0] - pPrevObj.BidP[0]
    lReasonForTradingOrNotTradingShort = ""
    lReasonForTradingOrNotTradingLong = ""
        
    if pPrevObj.BidP[0] in g_quantity_adjustment_list_for_sell:
        pPrevObj.BidQ[0] = max( 0 , pPrevObj.BidQ[0] - g_quantity_adjustment_list_for_sell[pPrevObj.BidP[0]])
    else:
        g_quantity_adjustment_list_for_sell = {}

    if pPrevObj.AskP[0] in g_quantity_adjustment_list_for_buy:
        pPrevObj.AskQ[0] = max( 0 ,pPrevObj.AskQ[0] - g_quantity_adjustment_list_for_buy[pPrevObj.AskP[0]])
    else:
        g_quantity_adjustment_list_for_buy = {}    
        
    if(pPrevObj.EnterTradeShort == 0 and pPrevObj.EnterTradeLong == 0):
        g_bestqty_list_for_buy = {}
        g_bestqty_list_for_sell = {}
        return [ pPrevObj.BidQ[0] , pPrevObj.AskQ[0] , 0 , 0 , 0 ,0 ,0, 0]


    currentLTP = pCurrentObj.LTP
    currentTTQ = pCurrentObj.TTQ    

    l_dummy_AskQ0 = pPrevObj.AskQ[0]
    l_dummy_TTQChange_For_Buy = currentTTQ - pPrevObj.TTQ
    #close buy
    if(pPrevObj.EnterTradeShort < 0 ): # Need to buy we come here only if currentPosition is greater than 0 so no need to check again.
        lBuyTradedPrice = 0
        lBuyTradedQty = 0
        lQtyForWhichFillsCanBeGiven = pTradeStats['currentPositionShort']
        lOpenOrCloseSide = 'Close'
        lPriceAtWhichOrderIsToBeKept = 0
        if pPrevObj.EnterTradeShort == -2: #Standing at bid +1 
            lPriceAtWhichOrderIsToBeKept = max( pPrevObj.AskP[0] - ( 2 * gTickSize) , pPrevObj.BidP[0] + ( 1 * gTickSize) )

        if  ( lPriceAtWhichOrderIsToBeKept == pPrevObj.BidP[0] + ( 1 * gTickSize) ) or pPrevObj.EnterTradeShort == -1:
            g_bestqty_list_for_buy = {}
            l_dummy_TTQChange_For_Buy, l_dummy_AskQ0 , lReasonForTradingOrNotTradingShort, lBuyTradedQty,lBuyTradedPrice = fillForStandingAtBidPlus1Pip(pPrevObj, l_dummy_AskQ0,spreadAtTimeOfPreviousDataRow,\
                                                                                                                             currentLTP, l_dummy_TTQChange_For_Buy , lQtyForWhichFillsCanBeGiven,lOpenOrCloseSide)
        else:  #Standing at Bid
            l_dummy_TTQChange_For_Buy, lReasonForTradingOrNotTradingShort, lBuyTradedQty,lBuyTradedPrice = fillForStandingAtBid(pPrevObj, currentLTP, l_dummy_TTQChange_For_Buy , lQtyForWhichFillsCanBeGiven , lOpenOrCloseSide , lPriceAtWhichOrderIsToBeKept)
        
        
        pTradeStats['totalBuyAmountShort'] += lBuyTradedQty * lBuyTradedPrice
        pTradeStats['currentPositionShort'] -= lBuyTradedQty
        pTradeStats['NumberOfCloseBuy'] += lBuyTradedQty
    
    #open buy
    if(pPrevObj.EnterTradeLong > 0 and ( gMaxQty - pTradeStats['currentPositionLong'] ) > 0):
        lBuyTradedPrice = 0
        lBuyTradedQty = 0
        lQtyForWhichFillsCanBeGiven = gMaxQty - pTradeStats['currentPositionLong'] 
        lOpenOrCloseSide = 'Open'
        l_dummy_TTQChange_For_Buy, l_dummy_AskQ0 , lReasonForTradingOrNotTradingLong, lBuyTradedQty,lBuyTradedPrice = fillForStandingAtBidPlus1Pip(pPrevObj, l_dummy_AskQ0,spreadAtTimeOfPreviousDataRow,\
                                                                                                                     currentLTP, l_dummy_TTQChange_For_Buy , lQtyForWhichFillsCanBeGiven,lOpenOrCloseSide)
        pTradeStats['totalBuyAmountLong'] += lBuyTradedQty * lBuyTradedPrice
        pTradeStats['currentPositionLong'] += lBuyTradedQty
        pTradeStats['NumberOfOpenBuy'] += lBuyTradedQty
    
    l_dummy_BidQ0 = pPrevObj.BidQ[0]
    l_dummy_TTQChange_For_Sell = currentTTQ - pPrevObj.TTQ
    #Close Sell
    if(pPrevObj.EnterTradeLong < 0):
        lSellTradedPrice = 0
        lSellTradedQty = 0
        lQtyForWhichFillsCanBeGiven = pTradeStats['currentPositionLong'] 
        lOpenOrCloseSide = 'Close'         
        lPriceAtWhichOrderIsToBeKept = 0 
        if pPrevObj.EnterTradeLong == -2: #Hitting Fills
            lPriceAtWhichOrderIsToBeKept = max( pPrevObj.BidP[0] + ( 2 * gTickSize) , pPrevObj.AskP[0] - ( 1 * gTickSize) )
        if  ( lPriceAtWhichOrderIsToBeKept == pPrevObj.AskP[0] - ( 1 * gTickSize) ) or pPrevObj.EnterTradeLong == -1:
            g_bestqty_list_for_sell = {} #Standing at Ask +1 
            l_dummy_TTQChange_For_Sell,l_dummy_BidQ0,lReasonForTradingOrNotTradingLong,lSellTradedQty,lSellTradedPrice = fillForStandingAtAskMinus1Pip(pPrevObj, l_dummy_BidQ0,spreadAtTimeOfPreviousDataRow,\
                                                                                                                             currentLTP, l_dummy_TTQChange_For_Sell , lQtyForWhichFillsCanBeGiven,lOpenOrCloseSide)
        else: #Standing at Ask
            l_dummy_TTQChange_For_Sell,lReasonForTradingOrNotTradingLong,lSellTradedQty,lSellTradedPrice = fillForStandingAtAsk(pPrevObj, currentLTP, l_dummy_TTQChange_For_Sell , lQtyForWhichFillsCanBeGiven , lOpenOrCloseSide , lPriceAtWhichOrderIsToBeKept)
        pTradeStats['totalSellAmountLong'] += lSellTradedQty * lSellTradedPrice
        pTradeStats['currentPositionLong'] -= lSellTradedQty
        pTradeStats['NumberOfCloseSell'] += lSellTradedQty
    
    #Open Sell
    if pPrevObj.EnterTradeShort > 0 and (gMaxQty - pTradeStats['currentPositionShort'] ) > 0 :
        lSellTradedPrice = 0
        lSellTradedQty = 0
        lQtyForWhichFillsCanBeGiven = ( gMaxQty - pTradeStats['currentPositionShort'] )
        lOpenOrCloseSide = 'Open'
        l_dummy_TTQChange_For_Sell,l_dummy_BidQ0,lReasonForTradingOrNotTradingShort,lSellTradedQty,lSellTradedPrice = fillForStandingAtAskMinus1Pip(pPrevObj, l_dummy_BidQ0,spreadAtTimeOfPreviousDataRow,\
                                                                                                                             currentLTP, l_dummy_TTQChange_For_Sell , lQtyForWhichFillsCanBeGiven,lOpenOrCloseSide)
        pTradeStats['totalSellAmountShort'] += lSellTradedQty * lSellTradedPrice
        pTradeStats['currentPositionShort'] += lSellTradedQty
        pTradeStats['NumberOfOpenSell'] += lSellTradedQty
                                      
    pPrevObj.ReasonForTradingOrNotTradingShort = lReasonForTradingOrNotTradingShort
    pPrevObj.ReasonForTradingOrNotTradingLong = lReasonForTradingOrNotTradingLong
    return [  l_dummy_BidQ0 , l_dummy_AskQ0 , l_dummy_TTQChange_For_Buy , l_dummy_TTQChange_For_Sell , lBuyTradedPrice , lBuyTradedQty,lSellTradedPrice,lSellTradedQty ]

def update_obj_list(pCurrentDataRow):
    l_obj = ticks_values_to_be_stored()
    l_obj.AskP[0] = float(pCurrentDataRow[colNumberOfData.AskP0])
    l_obj.AskQ[0] = float(pCurrentDataRow[colNumberOfData.AskQ0])
    l_obj.BidP[0] = float(pCurrentDataRow[colNumberOfData.BidP0])
    l_obj.BidQ[0] = float(pCurrentDataRow[colNumberOfData.BidQ0])
    l_obj.AskP[1] = float(pCurrentDataRow[colNumberOfData.AskP1])
    l_obj.AskQ[1] = float(pCurrentDataRow[colNumberOfData.AskQ1])
    l_obj.BidP[1] = float(pCurrentDataRow[colNumberOfData.BidP1])
    l_obj.BidQ[1] = float(pCurrentDataRow[colNumberOfData.BidQ1])
    l_obj.AskP[2] = float(pCurrentDataRow[colNumberOfData.AskP2])
    l_obj.AskQ[2] = float(pCurrentDataRow[colNumberOfData.AskQ2])
    l_obj.BidP[2] = float(pCurrentDataRow[colNumberOfData.BidP2])
    l_obj.BidQ[2] = float(pCurrentDataRow[colNumberOfData.BidQ2])
    l_obj.AskP[3] = float(pCurrentDataRow[colNumberOfData.AskP3])
    l_obj.AskQ[3] = float(pCurrentDataRow[colNumberOfData.AskQ3])
    l_obj.BidP[3] = float(pCurrentDataRow[colNumberOfData.BidP3])
    l_obj.BidQ[3] = float(pCurrentDataRow[colNumberOfData.BidQ3])
    l_obj.AskP[4] = float(pCurrentDataRow[colNumberOfData.AskP4])
    l_obj.AskQ[4] = float(pCurrentDataRow[colNumberOfData.AskQ4])
    l_obj.BidP[4] = float(pCurrentDataRow[colNumberOfData.BidP4])
    l_obj.BidQ[4] = float(pCurrentDataRow[colNumberOfData.BidQ4])
    
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
    

def readOnceAndWrite(pFileName, entryCL , exitCL , predictedValuesDict):
    global g_bestqty_list_for_sell, g_bestqty_list_for_buy
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
    noPredictionForThisRow = 0
    currentSellPredictedValue = 0
    currentBuyPredictedValue = 0
    currentIndex = 0
    l_previous_obj = None
    l_obj= None
    print("Processing the data file for trades :")
    attribute.initList()
    print("EntryLevels",entryCL , exitCL)
    for currentDataRow in dataFile.matrix:
        
        l_obj = update_obj_list(currentDataRow)
        if(l_previous_obj != None):
            lReturnList = checkIfPreviousDecisionToEnterOrExitTradeWasSuccessful( l_obj , l_previous_obj , tradeStats )
            
            lDummyBidQ0 = lReturnList[0]
            lDummyAskQ0 = lReturnList[1]
            lDummyTTQForBuy = lReturnList[2]
            lDummyTTQForSell = lReturnList[3]
            lBuyTradedPrice = lReturnList[4]
            lBuyTradedQty = lReturnList[5]
            lSellTradedPrice = lReturnList[6]
            lSellTradedQty = lReturnList[7]
            if currentIndex > 0:
                if(g_bestqty_list_for_buy != {}):
                    l_best_bidq = g_bestqty_list_for_buy['qty']
                    l_best_bidp = g_bestqty_list_for_buy['price']
                else:
                    l_best_bidq = 0
                    l_best_bidp = 0
                if(g_bestqty_list_for_sell != {}):
                    l_best_askq = g_bestqty_list_for_sell['qty']
                    l_best_askp = g_bestqty_list_for_sell['price'] 
                else:
                    l_best_askq = 0
                    l_best_askp = 0
                attribute.aList[currentIndex-1][0] = l_obj.currentTimeStamp
                attribute.aList[currentIndex-1][1] = tradeStats['currentPositionLong']
                attribute.aList[currentIndex-1][2] = tradeStats['currentPositionShort']
                listOfStringsToPrint = [ str(l_previous_obj.BidQ[0]) , str(l_previous_obj.BidP[0]),str(l_previous_obj.BidQ[1]) , str(l_previous_obj.BidP[1]),str(l_previous_obj.BidQ[2]) , str(l_previous_obj.BidP[2]),str(l_previous_obj.BidQ[3]) ,\
                                         str(l_previous_obj.BidP[4]),str(l_previous_obj.BidQ[4]) , str(l_previous_obj.AskQ[0]) , str(l_previous_obj.AskP[0]) , str(l_previous_obj.AskQ[1]) , str(l_previous_obj.AskP[1]) ,str(l_previous_obj.AskQ[2]) , str(l_previous_obj.AskP[2]) ,\
                                         str(l_previous_obj.AskQ[3]) , str(l_previous_obj.AskP[3]) ,str(l_previous_obj.AskQ[4]) , str(l_previous_obj.AskP[4]) ,\
                                         str(l_previous_obj.TTQ) , str(l_previous_obj.LTP) ,\
                                        str(currentSellPredictedValue) , str(l_previous_obj.EnterTradeShort) ,l_previous_obj.ReasonForTradingOrNotTradingShort , str(currentBuyPredictedValue) ,\
                                        str(l_previous_obj.EnterTradeLong) ,l_previous_obj.ReasonForTradingOrNotTradingLong , str(tradeStats['NumberOfCloseBuy']),\
                                        str(tradeStats['NumberOfOpenBuy']),str(tradeStats['NumberOfOpenSell']),\
                                        str(tradeStats['NumberOfCloseBuy']),str(lDummyBidQ0),str(lDummyAskQ0),\
                                        str(lDummyTTQForBuy),str(lDummyTTQForSell),str(l_best_bidq),str(l_best_bidp),str(l_best_askp),\
                                        str(l_best_askq) ,str(lBuyTradedPrice), str(lBuyTradedQty), str(lSellTradedPrice),str(lSellTradedQty)]
                attribute.aList[currentIndex-1][3] =  ";".join(listOfStringsToPrint)
            currentTimeStamp = common.convertTimeStampFromStringToFloat(currentDataRow[colNumberOfData.TimeStamp])
            
            try:
                currentSellPredictedValue = float(predictedValuesDict[l_obj.currentTimeStamp]['sell']) 
                currentBuyPredictedValue  = float(predictedValuesDict[l_obj.currentTimeStamp]['buy'])
            except:
                noPredictionForThisRow += 1

            #Open sell and Close Buy
            if(currentSellPredictedValue >= entryCL and tradeStats['currentPositionLong'] == 0):
                g_bestqty_list_for_sell = {}
                l_obj.EnterTradeShort = 1       #For open buy
            elif(currentBuyPredictedValue >= exitCL and tradeStats['currentPositionShort'] > 0):
                g_bestqty_list_for_buy = {}
                l_obj.EnterTradeShort = -1       #For close by hitting
            elif(tradeStats['currentPositionShort'] > 0):
                g_bestqty_list_for_buy = {}
                l_obj.EnterTradeShort = -2  
            else:
                l_obj.EnterTradeShort = 0

            #Open Buy
            if(currentBuyPredictedValue >= entryCL and tradeStats['currentPositionShort'] == 0):
                g_bestqty_list_for_buy = {}
                l_obj.EnterTradeLong = 1       #For close by hitting
            elif(currentSellPredictedValue >= exitCL and tradeStats['currentPositionLong'] > 0):
                g_bestqty_list_for_sell = {}
                l_obj.EnterTradeLong = -1       #For close by hitting
            elif():
                g_bestqty_list_for_sell = {}
                l_obj.EnterTradeLong = -2       #For close by hitting               
            else:
                l_obj.EnterTradeLong = 0        
            

        
        l_previous_obj = l_obj
        currentIndex = currentIndex + 1

# Squaring off if some open position there   
    if tradeStats['currentPositionLong'] > 0:
        tradeStats['NumberOfCloseSell'] += tradeStats['currentPositionLong']
        tradeStats['totalSellAmountLong'] += tradeStats['currentPositionLong'] * (l_previous_obj.BidP[0])
        tradeStats['currentPositionLong'] = 0
        l_obj.ReasonForTradingOrNotTradingLong = 'CloseSell(Hitting)'
    if tradeStats['currentPositionShort'] > 0:
        tradeStats['NumberOfCloseBuy'] += tradeStats['currentPositionShort']
        tradeStats['totalBuyAmountShort'] += tradeStats['currentPositionShort'] * (l_previous_obj.AskP[0])
        tradeStats['currentPositionShort'] = 0
        l_obj.ReasonForTradingOrNotTradingLong = 'CloseBuy(Hitting)'
    
    attribute.aList[currentIndex-1][0] = currentTimeStamp
    attribute.aList[currentIndex-1][1] = tradeStats['currentPositionLong']
    attribute.aList[currentIndex-1][2] = tradeStats['currentPositionShort']
    if(g_bestqty_list_for_buy != {}):
        l_best_bidq = g_bestqty_list_for_buy['qty']
        l_best_bidp = g_bestqty_list_for_buy['price'] 
    else:
        l_best_bidq = 0
        l_best_bidp = 0
    if(g_bestqty_list_for_sell != {}):
        l_best_askq = g_bestqty_list_for_sell['qty']
        l_best_askp = g_bestqty_list_for_sell['price'] 
    else:
        l_best_askq = 0
        l_best_askp = 0
    listOfStringsToPrint = [ str(l_previous_obj.BidQ[0]) , str(l_previous_obj.BidP[0]),str(l_previous_obj.BidQ[1]) , str(l_previous_obj.BidP[1]),str(l_previous_obj.BidQ[2]) , str(l_previous_obj.BidP[2]),str(l_previous_obj.BidQ[3]) ,\
                             str(l_previous_obj.BidP[4]),str(l_previous_obj.BidQ[4]) , str(l_previous_obj.AskQ[0]) , str(l_previous_obj.AskP[0]) , str(l_previous_obj.AskQ[1]) , str(l_previous_obj.AskP[1]) ,str(l_previous_obj.AskQ[2]) , str(l_previous_obj.AskP[2]) ,\
                             str(l_previous_obj.AskQ[3]) , str(l_previous_obj.AskP[3]) ,str(l_previous_obj.AskQ[4]) , str(l_previous_obj.AskP[4]) ,\
                             str(l_previous_obj.TTQ) , str(l_previous_obj.LTP) ,\
                            str(currentSellPredictedValue) , str(l_previous_obj.EnterTradeShort) ,l_previous_obj.ReasonForTradingOrNotTradingShort , str(currentBuyPredictedValue) ,\
                            str(l_previous_obj.EnterTradeLong) ,l_previous_obj.ReasonForTradingOrNotTradingLong , str(tradeStats['NumberOfCloseBuy']),\
                            str(tradeStats['NumberOfOpenBuy']),str(tradeStats['NumberOfOpenSell']),\
                            str(tradeStats['NumberOfCloseBuy']),str(lDummyBidQ0),str(lDummyAskQ0),\
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
    lHeaderColumnNamesList  = ['TimeStamp','CurrentPositionLong','CurrentPositionShort','BidQ0;BidP0;BidQ1;BidP1;BidQ2;BidP2;BidQ3;BidP3;BidQ4;BidP4','AskQ0;AskP0;AskQ1;AskP1;AskQ2;AskP2;AskQ3;AskP3;AskQ4;AskP4','TTQ','LTP','CurPredValueShort',\
                               'EnterTradeShort','ReasonForTradingOrNotTradingShort','CurPredValueLong','EnterTradeLong','ReasonForTradingOrNotTradingLong',\
                               'totalBuyTradeShort','totalBuyLong','totalSellShort','totalSellLong','DummyBidQ0','DummyAskQ0','DummyTTQChangeForSell','DummyTTQChangeForBuy' \
                               ,'BestBidQ','BestBidP','BestAskP','BestAskQ','BuyTradedPrcie','BuyTradedQty','SellTradedPrice','SellTradedQty']
    
    attribute.writeToFile(fileName , lHeaderColumnNamesList)

    
    tradeResultMainDirName = dirName+"/r/"
    if not os.path.exists(tradeResultMainDirName):
        os.mkdir(tradeResultMainDirName)
    tradeResultSubDirectoryName =  tradeResultMainDirName + mainExperimentName+"/"
    if not os.path.exists(tradeResultSubDirectoryName):
        os.mkdir(tradeResultSubDirectoryName)
    fileName = tradeResultSubDirectoryName+pFileName+".result" 
    outputFile = open(fileName,"w")
    
    #changed file write to modify it to Short Long version
    print("Starting to write: "+fileName)
    print("The gross profit for Short are: " + str(tradeStats['totalSellAmountShort'] - tradeStats['totalBuyAmountShort']), file = outputFile)
    print("The gross profit for Long are: " + str(tradeStats['totalSellAmountLong'] - tradeStats['totalBuyAmountLong']), file = outputFile)
    print("The total open sell amount is: " + str(tradeStats['totalSellAmountShort']), file = outputFile)
    print("The total close sell amount is: " + str(tradeStats['totalSellAmountLong']), file = outputFile)
    print("The total close buy amount is: " + str(tradeStats['totalBuyAmountShort']), file = outputFile)
    print("The total open buy amount is: " + str(tradeStats['totalBuyAmountLong']), file = outputFile)
    print("Number open sell trade happened: " + str(tradeStats['NumberOfOpenSell']), file = outputFile)
    print("Number close sell trade happened: " + str(tradeStats['NumberOfCloseSell']), file = outputFile)
    print("Number close buy trade happened: " + str(tradeStats['NumberOfCloseBuy']), file = outputFile)
    print("Number open buy trade happened: " + str(tradeStats['NumberOfOpenBuy']), file = outputFile)
       
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
    predictedValuesDict = dict()
    getPredictedValuesIntoDict(predictedValuesDict)
    lIndexOfEntryOrExitCL = 0
    for lFileName in initialFileName:
        entryCL = float("." + gEntryCLList[lIndexOfEntryOrExitCL] )
        exitCL = float("." + gExitCLList[lIndexOfEntryOrExitCL] )
        readOnceAndWrite(lFileName,entryCL,exitCL, predictedValuesDict)
        lIndexOfEntryOrExitCL = lIndexOfEntryOrExitCL + 1
      
if __name__ == "__main__":

    dirName = args.pd.replace('/ro/','/rs/')
    checkAllFilesAreExistOrNot = 'false'
      
    lWFDirName = args.pd.replace('/ro/','/wf/')
    predictedBuyValuesFileName = lWFDirName+"/p/"+mainExperimentName+"/"+args.a + 'buy' + '-td.' + os.path.basename(os.path.abspath(args.td)) + '-dt.' + \
    args.dt + '-targetClass.' + args.targetClass + '-f.' + experimentName + "-wt." + args.wt+ attribute.generateExtension() + ".predictions"
      
    predictedSellValuesFileName = lWFDirName+"/p/"+mainExperimentName+"/"+args.a + 'sell' + '-td.' + os.path.basename(os.path.abspath(args.td)) + '-dt.' +\
    args.dt + '-targetClass.' + args.targetClass + '-f.' + experimentName + "-wt." + args.wt+ attribute.generateExtension() + ".predictions"
      
    if os.path.isfile(predictedBuyValuesFileName) and os.path.isfile(predictedSellValuesFileName):
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


