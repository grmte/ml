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
parser.add_argument('-dt',required=False,help="Number of days it was trained")  
parser.add_argument('-targetClass',required=False,help="For which model was used ; binomial(target takes only true and false) / multinomial (target values takes more than 2 values)")
parser.add_argument('-tickSize',required=True,help="Nse Currency = 25000 , Future Options = 5")
parser.add_argument('-wt',required=False,help="default/exp , weight type to be given to different days")
parser.add_argument('-iT',required=False,help='Instrument name')
parser.add_argument('-sP',required=False,help='Strike price of instrument')
parser.add_argument('-oT',required=False,help='Options Type')
# parser.add_argument('-entryCL0',required=True,help="Percentage of the confidence level used to stand")
# parser.add_argument('-entryCL1',required=True,help="Percentage of the confidence level used to stand")
# parser.add_argument('-entryCL2',required=True,help="Percentage of the confidence level used to delete orders")
args = parser.parse_args()

sys.path.append("./src/")
sys.path.append("./ob/generators/")
import dataFile, colNumberOfData, common
import attribute
attribute.initializeInstDetails(args.iT,args.sP,args.oT)
if args.skipT == None:
    args.skipT = "no"
if args.dt == None:
    args.dt = "1"
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

totalEntryCL = args.entryCL.split(";")
totalExitCL = args.exitCL.split(";")
initialFileName = []
    

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
        self.AskP = 0.0
        self.AskQ = 0
        self.BidP = 0.0
        self.BidQ = 0
        self.LTP = 0.0
        self.TTQ  = 0
        self.currentTimeStamp = 0.0
        self.EnterTradeShort = 0
        self.EnterTradeLong = 0
        self.standingAtBid = 0
        self.standingAtAsk = 0
        self.standingAtBidPlus1pip = 0
        self.standingAtAskMinus1pip = 0
        self.CloseStandingAtBid = 0
        self.CloseStandingAtAsk = 0
        self.CloseStandingAtBidPlus1pip = 0
        self.CloseStandingAtAskMinus1pip = 0
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


def update_best_bidside_using_tick(pPrevObj ):
    global g_bestqty_list_for_buy
    if((pPrevObj.OrderType).upper() == "B"):
        if(pPrevObj.MsgCode == "M"):
            if(pPrevObj.OldP == g_bestqty_list_for_buy['price'] ):
                g_bestqty_list_for_buy['qty'] = g_bestqty_list_for_buy['qty'] - pPrevObj.OldQ
                if(g_bestqty_list_for_buy['qty'] < 0):
                    g_bestqty_list_for_buy['qty'] = 0
        if(pPrevObj.MsgCode == "X"):
            if(pPrevObj.NewP == g_bestqty_list_for_buy['price'] ):
                g_bestqty_list_for_buy['qty'] = g_bestqty_list_for_buy['qty'] - pPrevObj.NewQ
                if(g_bestqty_list_for_buy['qty'] < 0):
                    g_bestqty_list_for_buy['qty'] = 0
                
def update_best_askside_using_tick(pPrevObj ):
    global g_bestqty_list_for_sell
    if((pPrevObj.OrderType).upper() == "S"):
        if(pPrevObj.MsgCode == "M"):
            if(pPrevObj.OldP == g_bestqty_list_for_sell['price'] ):
                g_bestqty_list_for_sell['qty'] = g_bestqty_list_for_sell['qty'] - pPrevObj.OldQ
                if(g_bestqty_list_for_sell['qty'] < 0):
                    g_bestqty_list_for_sell['qty'] = 0
        if(pPrevObj.MsgCode == "X"):
            if(pPrevObj.NewP == g_bestqty_list_for_sell['price'] ):
                g_bestqty_list_for_sell['qty'] = g_bestqty_list_for_sell['qty'] - pPrevObj.NewQ 
                if(g_bestqty_list_for_sell['qty'] < 0):
                    g_bestqty_list_for_sell['qty'] = 0              
            
def checkIfPreviousDecisionToEnterOrExitTradeWasSuccessful(pCurrentObj,pPrevObj , pTradeStats):
    global gTickSize , gMaxQty , g_quantity_adjustment_list_for_sell , g_quantity_adjustment_list_for_buy , g_bestqty_list_for_sell, g_bestqty_list_for_buy
    spreadAtTimeOfPreviousDataRow = pPrevObj.AskP - pPrevObj.BidP
    lReasonForTradingOrNotTradingShort = ""
    lReasonForTradingOrNotTradingLong = ""
    if(g_bestqty_list_for_buy == {} and  pPrevObj.EnterTradeLong == 1 and pPrevObj.standingAtBid ==1):
        g_bestqty_list_for_buy['price'] = pPrevObj.BidP 
        g_bestqty_list_for_buy['qty'] = pPrevObj.BidQ
    if(g_bestqty_list_for_sell == {} and pPrevObj.EnterTradeShort == 1 and pPrevObj.standingAtAsk ==1):
        g_bestqty_list_for_sell['price'] = pPrevObj.AskP 
        g_bestqty_list_for_sell['qty'] = pPrevObj.AskQ
    if pPrevObj.BidP in g_quantity_adjustment_list_for_sell:
        pPrevObj.BidQ = max( 0 , pPrevObj.BidQ - g_quantity_adjustment_list_for_sell[pPrevObj.BidP])
    else:
        g_quantity_adjustment_list_for_sell = {}

    if pPrevObj.AskP in g_quantity_adjustment_list_for_buy:
        pPrevObj.AskQ = max( 0 ,pPrevObj.AskQ - g_quantity_adjustment_list_for_buy[pPrevObj.AskP])
    else:
        g_quantity_adjustment_list_for_buy = {}    
        
    if(pPrevObj.EnterTradeShort == 0 and pPrevObj.EnterTradeLong == 0):
        return [ pPrevObj.BidQ , pPrevObj.AskQ , 0 , 0 ]


    currentLTP = pCurrentObj.LTP
    currentTTQ = pCurrentObj.TTQ    

    l_dummy_AskQ0 = pPrevObj.AskQ
    l_dummy_TTQChange_For_Buy = currentTTQ - pPrevObj.TTQ
    #close buy
    if(pPrevObj.EnterTradeShort == -1): # Need to buy we come here only if currentPosition is greater than 0 so no need to check again.
        #standing
        if spreadAtTimeOfPreviousDataRow > gTickSize:        
            if(l_dummy_TTQChange_For_Buy<=0):
                lReasonForTradingOrNotTradingShort = '(Spread>Pip)&&(NextTickTTQDidNotIncrease)'
            elif(currentLTP != pPrevObj.BidP): 
                lReasonForTradingOrNotTradingShort = '(Spread>Pip)&&(LTP!=Bid)'
            elif ("OpenSell(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingShort) or ("CloseSell(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingLong):
                lReasonForTradingOrNotTradingShort = 'TTQChangeBecauseOfOurOrder' 
            else:    
               
                lQtyTraded = min(  pTradeStats['currentPositionShort'] , l_dummy_TTQChange_For_Buy )
                l_dummy_TTQChange_For_Buy -= lQtyTraded
                pTradeStats['totalBuyAmountShort'] += lQtyTraded * (pPrevObj.BidP + gTickSize)
                pTradeStats['currentPositionShort'] -= lQtyTraded
                lReasonForTradingOrNotTradingShort = 'CloseBuy(Standing)'
                pTradeStats['NumberOfCloseBuy'] += lQtyTraded
        #hitting
        else:

            l_buy_qty = min( pTradeStats['currentPositionShort'], pPrevObj.AskQ)
            if pPrevObj.AskP in g_quantity_adjustment_list_for_buy:
                    g_quantity_adjustment_list_for_buy[pPrevObj.AskP] += l_buy_qty
            else:  
                    g_quantity_adjustment_list_for_buy = {} 
                    g_quantity_adjustment_list_for_buy[pPrevObj.AskP] = l_buy_qty
            l_dummy_AskQ0 -= l_buy_qty
            pTradeStats['totalBuyAmountShort'] += l_buy_qty * (pPrevObj.AskP)
            pTradeStats['currentPositionShort'] -= l_buy_qty
            pTradeStats['NumberOfCloseBuy'] += l_buy_qty
             
            if l_buy_qty > 0:
                lReasonForTradingOrNotTradingShort = 'CloseBuy(Hitting)'
            else :
                lReasonForTradingOrNotTradingShort = "DummyAskQExhuasted"
        
    #open buy
    #standing at best bid
    if(pPrevObj.standingAtBid == 1 and pPrevObj.EnterTradeLong == 1 and ( gMaxQty - pTradeStats['currentPositionLong'] ) > 0):
        if(g_bestqty_list_for_buy != {} and pPrevObj.BidP <= g_bestqty_list_for_buy['price']):
            update_best_bidside_using_tick(pPrevObj)
            if(l_dummy_TTQChange_For_Buy <= 0 ):
                lReasonForTradingOrNotTradingLong = 'AtBest1(NextTickTTQDidNotIncrease)'
            elif ("OpenSell(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingShort) or ("CloseSell(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingLong):
                lReasonForTradingOrNotTradingShort = 'TTQChangeBecauseOfOurOrder' 
            elif(l_dummy_TTQChange_For_Buy >= 0 and currentLTP <= g_bestqty_list_for_buy['price']):
                  if(g_bestqty_list_for_buy['qty'] > l_dummy_TTQChange_For_Buy):
                      l_dummy_TTQChange_For_Buy = 0
                      g_bestqty_list_for_buy['qty'] = g_bestqty_list_for_buy['qty'] -l_dummy_TTQChange_For_Buy
                  else:
                      l_dummy_TTQChange_For_Buy = l_dummy_TTQChange_For_Buy - g_bestqty_list_for_buy['qty']
                      g_bestqty_list_for_buy['qty'] = 0
                  if(l_dummy_TTQChange_For_Buy > 0):
                      lQtyToBeTraded = ( gMaxQty - pTradeStats['currentPositionLong'] )
                      lQtyForWhichWeTrade = min( lQtyToBeTraded , l_dummy_TTQChange_For_Buy)
                      l_dummy_TTQChange_For_Buy -= lQtyForWhichWeTrade
                      pTradeStats['totalBuyAmountLong'] += lQtyForWhichWeTrade * (g_bestqty_list_for_buy['price'])
                      pTradeStats['currentPositionLong'] += lQtyForWhichWeTrade
                      lReasonForTradingOrNotTradingLong = 'OpenBuyatBest(Standing)'
                      pTradeStats['NumberOfOpenBuy'] += lQtyForWhichWeTrade
                  else:
                      lReasonForTradingOrNotTradingLong = 'AtBest2(NextTickTTQDidNotIncrease)'   
        else:
            g_bestqty_list_for_buy['price'] = pPrevObj.BidP 
            g_bestqty_list_for_buy['qty'] = pPrevObj.BidQ
    elif(pPrevObj.standingAtBidPlus1pip == 1 and pPrevObj.EnterTradeLong == 1 and ( gMaxQty - pTradeStats['currentPositionLong'] ) > 0):
        #standing
        if spreadAtTimeOfPreviousDataRow > gTickSize:        
            if(l_dummy_TTQChange_For_Buy <= 0 ):
                lReasonForTradingOrNotTradingLong = '(Spread>Pip)&&(NextTickTTQDidNotIncrease)'
            elif(currentLTP != pPrevObj.BidP):
                lReasonForTradingOrNotTradingLong = '(Spread>Pip)&&(LTPDoesNotEqualBidP0Long)'
            elif ("OpenSell(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingShort) or ("CloseSell(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingLong):
                lReasonForTradingOrNotTradingShort = 'TTQChangeBecauseOfOurOrder' 
            else:

                lQtyToBeTraded = ( gMaxQty - pTradeStats['currentPositionLong'] )
                lQtyForWhichWeTrade = min( lQtyToBeTraded , l_dummy_TTQChange_For_Buy)
                l_dummy_TTQChange_For_Buy -= lQtyForWhichWeTrade
                pTradeStats['totalBuyAmountLong'] += lQtyForWhichWeTrade * (pPrevObj.BidP + gTickSize)
                pTradeStats['currentPositionLong'] += lQtyForWhichWeTrade
                lReasonForTradingOrNotTradingLong = 'OpenBuy(Standing)'
                pTradeStats['NumberOfOpenBuy'] += lQtyForWhichWeTrade
        #hitting
        else:
            if l_dummy_AskQ0 > 0 :

                lQtyToBeTraded = ( gMaxQty - pTradeStats['currentPositionLong'] )
                lQtyForWhichWeTrade = min( lQtyToBeTraded , l_dummy_AskQ0 )
                if pPrevObj.AskP in g_quantity_adjustment_list_for_buy:
                    g_quantity_adjustment_list_for_buy[pPrevObj.AskP] += lQtyForWhichWeTrade
                else:
                    g_quantity_adjustment_list_for_buy = {}
                    g_quantity_adjustment_list_for_buy[pPrevObj.AskP] = lQtyForWhichWeTrade
                pTradeStats['totalBuyAmountLong'] += lQtyForWhichWeTrade * (pPrevObj.AskP)
                pTradeStats['currentPositionLong'] += lQtyForWhichWeTrade
                pTradeStats['NumberOfOpenBuy'] += lQtyForWhichWeTrade
                l_dummy_AskQ0 -= lQtyForWhichWeTrade
                lReasonForTradingOrNotTradingLong = 'OpenBuy(Hitting)'
            else:
                lReasonForTradingOrNotTradingLong = "DummyAskQ0Exhausted"      
    else:
        if(pPrevObj.EnterTradeLong == 1 and ( gMaxQty - pTradeStats['currentPositionLong'] ) > 0): # Need to buy
            #Hitting
            if l_dummy_AskQ0 > 0 :

                lQtyToBeTraded = ( gMaxQty - pTradeStats['currentPositionLong'] )
                lQtyForWhichWeTrade = min( lQtyToBeTraded , l_dummy_AskQ0 )
                if pPrevObj.AskP in g_quantity_adjustment_list_for_buy:
                    g_quantity_adjustment_list_for_buy[pPrevObj.AskP] += lQtyForWhichWeTrade
                else:
                    g_quantity_adjustment_list_for_buy = {}
                    g_quantity_adjustment_list_for_buy[pPrevObj.AskP] = lQtyForWhichWeTrade
                pTradeStats['totalBuyAmountLong'] += lQtyForWhichWeTrade * (pPrevObj.AskP)
                pTradeStats['currentPositionLong'] += lQtyForWhichWeTrade
                pTradeStats['NumberOfOpenBuy'] += lQtyForWhichWeTrade
                l_dummy_AskQ0 -= lQtyForWhichWeTrade
                lReasonForTradingOrNotTradingLong = 'OpenBuy(Hitting)'
            else:
                lReasonForTradingOrNotTradingLong = "DummyAskQ0Exhausted"

    l_dummy_BidQ0 = pPrevObj.BidQ
    l_dummy_TTQChange_For_Sell = currentTTQ - pPrevObj.TTQ
    #close sell
    if(pPrevObj.EnterTradeLong == -1): # Need to sell we come here only if currentPosition is greater than 0 so no need to check again.
        #standing
        if spreadAtTimeOfPreviousDataRow > gTickSize:        
            if(l_dummy_TTQChange_For_Sell <= 0 ):
                lReasonForTradingOrNotTradingLong = '(Spread>Pip)&&(NextTickTTQDidNotIncrease)'
            elif(currentLTP != pPrevObj.AskP): 
                lReasonForTradingOrNotTradingLong = '(Spread>Pip)&&(NextTickLTP!=Ask)'
            elif ("OpenSell(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingShort) or ("CloseSell(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingLong):
                lReasonForTradingOrNotTradingShort = 'TTQChangeBecauseOfOurOrder' 
            else:    

                lQtyTraded = min(  pTradeStats['currentPositionLong'] , l_dummy_TTQChange_For_Sell )
                pTradeStats['totalSellAmountLong'] += lQtyTraded * (pPrevObj.AskP - gTickSize)
                pTradeStats['currentPositionLong'] -= lQtyTraded
                l_dummy_TTQChange_For_Sell -= lQtyTraded
                lReasonForTradingOrNotTradingLong = 'CloseSell(Standing)'
                pTradeStats['NumberOfCloseSell'] += lQtyTraded
        #hitting
        else:

            lQtyTraded = min( pTradeStats['currentPositionLong'] , pPrevObj.BidQ )
            if pPrevObj.BidP in g_quantity_adjustment_list_for_sell:
                g_quantity_adjustment_list_for_sell[pPrevObj.BidP] += lQtyTraded
            else:
                g_quantity_adjustment_list_for_sell = {}
                g_quantity_adjustment_list_for_sell[pPrevObj.BidP] = lQtyTraded
            pTradeStats['totalSellAmountLong'] += lQtyTraded * (pPrevObj.BidP)
            pTradeStats['currentPositionLong'] -= lQtyTraded
            l_dummy_BidQ0 -= lQtyTraded
            
            if lQtyTraded > 0 :
                lReasonForTradingOrNotTradingLong = 'CloseSell(Hitting)'
            else :
                lReasonForTradingOrNotTradingLong = "DummyBidQExhuasted"
            pTradeStats['NumberOfCloseSell'] += lQtyTraded
    
    #open sell
    if(pPrevObj.EnterTradeShort == 1 and pPrevObj.standingAtAsk  == 1 and  ( gMaxQty - pTradeStats['currentPositionShort'] ) > 0 ):
        if(g_bestqty_list_for_sell != {} and pPrevObj.AskP >= g_bestqty_list_for_sell['price']):
            update_best_askside_using_tick(pPrevObj)
            if(l_dummy_TTQChange_For_Sell <= 0):
                lReasonForTradingOrNotTradingShort = 'AtBest1(NextTickTTQDidNotIncrease)'
            elif ("OpenSell(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingShort) or ("CloseSell(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingLong):
                lReasonForTradingOrNotTradingShort = 'TTQChangeBecauseOfOurOrder' 
            elif(currentLTP >= g_bestqty_list_for_sell['price']):
                if(g_bestqty_list_for_sell['qty'] > l_dummy_TTQChange_For_Sell):
                    l_dummy_TTQChange_For_Sell = 0
                    g_bestqty_list_for_sell['qty'] = g_bestqty_list_for_sell['qty'] -l_dummy_TTQChange_For_Sell
                else:
                  l_dummy_TTQChange_For_Sell = l_dummy_TTQChange_For_Sell - g_bestqty_list_for_sell['qty']
                  g_bestqty_list_for_sell['qty'] = 0
                if(l_dummy_TTQChange_For_Sell > 0):
                    lQtyToBeTraded = ( gMaxQty - pTradeStats['currentPositionShort'] )
                    lQtyForWhichWeTrade = min( lQtyToBeTraded , l_dummy_TTQChange_For_Sell)
                    pTradeStats['totalSellAmountShort'] += lQtyForWhichWeTrade * (g_bestqty_list_for_sell['price'])
                    pTradeStats['currentPositionShort'] += lQtyForWhichWeTrade
                    l_dummy_TTQChange_For_Sell -= lQtyForWhichWeTrade
                    lReasonForTradingOrNotTradingShort = 'OpenSellBest(Standing)'
                    pTradeStats['NumberOfOpenSell'] += lQtyForWhichWeTrade
                else:
                    lReasonForTradingOrNotTradingShort = 'AtBest2(NextTickTTQDidNotIncrease)'
        else:
            if( pPrevObj.AskP < g_bestqty_list_for_sell['price']):
                g_bestqty_list_for_sell['price'] = pPrevObj.AskP 
                g_bestqty_list_for_sell['qty'] = pPrevObj.AskQ 
    elif(pPrevObj.EnterTradeShort == 1 and pPrevObj.standingAtAskMinus1pip  == 1 and  ( gMaxQty - pTradeStats['currentPositionShort'] ) > 0 ):
        #standing
        if spreadAtTimeOfPreviousDataRow > gTickSize:        
            if(l_dummy_TTQChange_For_Sell <= 0):
                lReasonForTradingOrNotTradingShort = '(Spread>Pip)&&(NextTickTTQDidNotIncrease)'
            elif(currentLTP != pPrevObj.AskP):
                lReasonForTradingOrNotTradingShort = '(Spread>Pip)&&(NextTickLTP!=Ask)'
            elif ("OpenSell(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingShort) or ("CloseSell(Hitting)" in pPrevObj.ReasonForTradingOrNotTradingLong):
                lReasonForTradingOrNotTradingShort = 'TTQChangeBecauseOfOurOrder' 
            else:

                lQtyToBeTraded = ( gMaxQty - pTradeStats['currentPositionShort'] )
                lQtyForWhichWeTrade = min( lQtyToBeTraded , l_dummy_TTQChange_For_Sell)
                pTradeStats['totalSellAmountShort'] += lQtyForWhichWeTrade * (pPrevObj.AskP - gTickSize)
                pTradeStats['currentPositionShort'] += lQtyForWhichWeTrade
                l_dummy_TTQChange_For_Sell -= lQtyForWhichWeTrade
                lReasonForTradingOrNotTradingShort = 'OpenSell(Standing)'
                pTradeStats['NumberOfOpenSell'] += lQtyForWhichWeTrade
        #hitting
        else:
            if l_dummy_BidQ0 > 0 :

                lQtyToBeTraded = ( gMaxQty - pTradeStats['currentPositionShort'] )
                lQtyForWhichWeTrade = min( lQtyToBeTraded , l_dummy_BidQ0 )
                if pPrevObj.BidP in g_quantity_adjustment_list_for_sell:
                    g_quantity_adjustment_list_for_sell[pPrevObj.BidP] += lQtyForWhichWeTrade
                else:
                    g_quantity_adjustment_list_for_sell = {}
                    g_quantity_adjustment_list_for_sell[pPrevObj.BidP] = lQtyForWhichWeTrade
                pTradeStats['totalSellAmountShort'] += lQtyForWhichWeTrade * (pPrevObj.BidP)
                pTradeStats['currentPositionShort'] += lQtyForWhichWeTrade
                lReasonForTradingOrNotTradingShort = 'OpenSell(Hitting)'
                pTradeStats['NumberOfOpenSell'] += lQtyForWhichWeTrade
                l_dummy_BidQ0 -= lQtyForWhichWeTrade
            else:
                lReasonForTradingOrNotTradingShort = 'DummyBidQZero'        
    else:
        if(pPrevObj.EnterTradeShort == 1 and  ( gMaxQty - pTradeStats['currentPositionShort'] ) > 0 ): # Need to sell
            #hitting
            if l_dummy_BidQ0 > 0 :

                lQtyToBeTraded = ( gMaxQty - pTradeStats['currentPositionShort'] )
                lQtyForWhichWeTrade = min( lQtyToBeTraded , l_dummy_BidQ0 )
                if pPrevObj.BidP in g_quantity_adjustment_list_for_sell:
                    g_quantity_adjustment_list_for_sell[pPrevObj.BidP] += lQtyForWhichWeTrade
                else:
                    g_quantity_adjustment_list_for_sell = {}
                    g_quantity_adjustment_list_for_sell[pPrevObj.BidP] = lQtyForWhichWeTrade
                pTradeStats['totalSellAmountShort'] += lQtyForWhichWeTrade * (pPrevObj.BidP)
                pTradeStats['currentPositionShort'] += lQtyForWhichWeTrade
                lReasonForTradingOrNotTradingShort = 'OpenSell(Hitting)'
                pTradeStats['NumberOfOpenSell'] += lQtyForWhichWeTrade
                l_dummy_BidQ0 -= lQtyForWhichWeTrade
            else:
                lReasonForTradingOrNotTradingShort = 'DummyBidQZero'

    pPrevObj.ReasonForTradingOrNotTradingShort = lReasonForTradingOrNotTradingShort
    pPrevObj.ReasonForTradingOrNotTradingLong = lReasonForTradingOrNotTradingLong
    return [  l_dummy_BidQ0 , l_dummy_AskQ0 , l_dummy_TTQChange_For_Buy , l_dummy_TTQChange_For_Sell]

def update_obj_list(pCurrentDataRow):
    l_obj = ticks_values_to_be_stored()
    l_obj.AskP = float(pCurrentDataRow[colNumberOfData.AskP0])
    l_obj.AskQ = float(pCurrentDataRow[colNumberOfData.AskQ0])
    l_obj.BidP = float(pCurrentDataRow[colNumberOfData.BidP0])
    l_obj.BidQ = float(pCurrentDataRow[colNumberOfData.BidQ0])
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
    

def readOnceAndWrite(pFileName, pEntryList, pExitList, predictedValuesDict):
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
    entryCL = float(pEntryList[3])/100
    entryCl0 = float(pEntryList[2])/100
    entryCL1 = float(pEntryList[1])/100
    entryCL2 = float(pEntryList[0])/100
    exitCL = float(pExitList[3])/100
    exitCl0 = float(pExitList[2])/100
    exitCL1 = float(pExitList[1])/100
    exitCL2 = float(pExitList[0])/100   
    print (entryCL, exitCL ,entryCl0, entryCL1 , entryCL2 )
    #  entryCLCutoff = float(args.entryCLCutoff)
    #  exitCLCutoff = float(args.exitCLCutoff)
    currentIndex = 0
    l_previous_obj = None
    l_obj= None
    print("Processing the data file for trades :")
    attribute.initList()
    for currentDataRow in dataFile.matrix:
        
        l_obj = update_obj_list(currentDataRow)
        if(l_previous_obj != None):
            lReturnList = checkIfPreviousDecisionToEnterOrExitTradeWasSuccessful( l_obj , l_previous_obj , tradeStats )
            
            lDummyBidQ0 = lReturnList[0]
            lDummyAskQ0 = lReturnList[1]
            lDummyTTQForBuy = lReturnList[2]
            lDummyTTQForSell = lReturnList[3]
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
                listOfStringsToPrint = [ str(l_previous_obj.BidQ) , str(l_previous_obj.BidP) , str(l_previous_obj.AskP) , \
                                        str(l_previous_obj.AskQ) , str(l_previous_obj.TTQ) , str(l_previous_obj.LTP) ,\
                                        str(currentSellPredictedValue) , str(l_previous_obj.EnterTradeShort) ,l_previous_obj.ReasonForTradingOrNotTradingShort , str(currentBuyPredictedValue) ,\
                                        str(l_previous_obj.EnterTradeLong) ,l_previous_obj.ReasonForTradingOrNotTradingLong , str(tradeStats['NumberOfCloseBuy']),\
                                        str(tradeStats['NumberOfOpenBuy']),str(tradeStats['NumberOfOpenSell']),\
                                        str(tradeStats['NumberOfCloseBuy']),str(lDummyBidQ0),str(lDummyAskQ0),\
                                        str(lDummyTTQForBuy),str(lDummyTTQForSell),str(l_best_bidq),str(l_best_bidp),str(l_best_askp), str(l_best_askq) ]
                attribute.aList[currentIndex-1][3] =  ";".join(listOfStringsToPrint)
            currentTimeStamp = common.convertTimeStampFromStringToFloat(currentDataRow[colNumberOfData.TimeStamp])
            
            try:
                currentSellPredictedValue = float(predictedValuesDict[l_obj.currentTimeStamp]['sell']) 
                currentBuyPredictedValue  = float(predictedValuesDict[l_obj.currentTimeStamp]['buy'])
            except:
                noPredictionForThisRow += 1
            
            #short decisions
            if(currentSellPredictedValue >= entryCL):
                g_bestqty_list_for_sell = {}
                l_obj.standingAtAsk = 0
                l_obj.EnterTradeShort = 1
                l_obj.standingAtAskMinus1pip = 0
            elif(currentSellPredictedValue >= entryCL0):
                g_bestqty_list_for_sell = {}
                l_obj.standingAtAsk = 0
                l_obj.standingAtAskMinus1pip = 1
                l_obj.EnterTradeShort = 1
            elif (currentSellPredictedValue >= entryCL1):
                l_obj.standingAtAskMinus1pip = 0
                if(l_previous_obj.standingAtAsk  == 0):
                    g_bestqty_list_for_sell = {}
                l_obj.standingAtAsk = 1
                l_obj.EnterTradeShort = 1
            elif (l_previous_obj.standingAtAsk == 1 and currentSellPredictedValue >= entryCL2):
                l_obj.standingAtAsk = 1
                l_obj.EnterTradeShort = 1
            #close Long positions
            elif((currentBuyPredictedValue >= exitCL)and tradeStats['currentPositionShort'] > 0):
                l_obj.EnterTradeShort = -1  # Implies to exit the trade
                g_bestqty_list_for_buy = {}
                l_obj.CloseStandingAtBid = 0
            elif((currentBuyPredictedValue >= exitCL0)and tradeStats['currentPositionShort'] > 0):
                l_obj.EnterTradeShort = -1  # Implies to exit the trade
                g_bestqty_list_for_buy = {}
                l_obj.CloseStandingAtBidPlus1pip = 1
                l_obj.CloseStandingAtBid = 0
            elif((currentBuyPredictedValue >= exitCL1)and tradeStats['currentPositionShort'] > 0):
                l_obj.EnterTradeShort = -1  # Implies to exit the trade
                if(l_previous_obj.CloseStandingAtBid  == 0):
                    g_bestqty_list_for_sell = {}
                g_bestqty_list_for_buy = {}
                l_obj.CloseStandingAtBidPlus1pip = 0
                l_obj.CloseStandingAtBid = 1
            elif(l_previous_obj.CloseStandingAtBid  == 1 and (currentBuyPredictedValue >= exitCL2)and tradeStats['currentPositionShort'] > 0):
                l_obj.EnterTradeShort = -1  # Implies to exit the trade
                l_obj.CloseStandingAtBidPlus1pip = 0
                l_obj.CloseStandingAtBid = 1                              
            else:
                g_bestqty_list_for_sell = {}
                l_obj.standingAtAsk = 0
                l_obj.standingAtAskMinus1pip = 0
                l_obj.CloseStandingAtBidPlus1pip = 0
                l_obj.CloseStandingAtBid = 0
                l_obj.EnterTradeShort = 0  # Implies make no change
                
            #       if EnterTradeShort == 1:
            #           if currentPredictedValue <= entryCLCutoff:
            #               enterTrade = 0
            #       if enterTrade == -1:
            #           if currentPredictedValue >= exitCLCutoff:
            #               enterTrade = 0
                    
            #long decisions
            if(currentBuyPredictedValue >= entryCL):
                g_bestqty_list_for_buy = {}
                l_obj.standingAtBid = 0
                l_obj.EnterTradeLong = 1
            elif(currentBuyPredictedValue >= entryCL0):
                g_bestqty_list_for_buy = {}
                l_obj.standingAtBid = 0
                l_obj.standingAtBidPlus1pip = 1
                l_obj.EnterTradeLong = 1
            elif (currentBuyPredictedValue >= entryCL1):
                if(l_previous_obj.standingAtBid  == 0):
                    g_bestqty_list_for_buy = {}
                l_obj.standingAtBid = 1
                l_obj.EnterTradeLong = 1
                l_obj.standingAtBidPlus1pip = 0
            elif (l_previous_obj.standingAtBid == 1 and currentBuyPredictedValue >= entryCL2):
                l_obj.standingAtBid = 1
                l_obj.EnterTradeLong = 1
            #Close Long positions
            elif((currentSellPredictedValue >= exitCL ) and tradeStats['currentPositionLong'] > 0):
                l_obj.EnterTradeLong = -1  # Implies to exit the trade
                l_obj.CloseStandingAtAsk = 0
                l_obj.CloseStandingAtAskMinus1pip = 0
            elif((currentSellPredictedValue >= exitCL0 ) and tradeStats['currentPositionLong'] > 0):
                l_obj.EnterTradeLong = -1  # Implies to exit the trade
                l_obj.CloseStandingAtAsk = 0
                l_obj.CloseStandingAtAskMinus1pip = 1
            elif((currentSellPredictedValue >= exitCL1 ) and tradeStats['currentPositionLong'] > 0):
                l_obj.EnterTradeLong = -1  # Implies to exit the trade
                if(l_previous_obj.CloseStandingAtAsk  == 0):
                    g_bestqty_list_for_sell = {}
                l_obj.CloseStandingAtAsk = 1
                l_obj.CloseStandingAtAskMinus1pip = 0
            elif(l_previous_obj.CloseStandingAtAsk == 1 and (currentSellPredictedValue >= exitCL2 ) and tradeStats['currentPositionLong'] > 0):
                l_obj.EnterTradeLong = -1  # Implies to exit the trade
                l_obj.CloseStandingAtAsk = 1
                l_obj.CloseStandingAtAskMinus1pip = 0
            else:
                g_bestqty_list_for_buy = {}
                l_obj.standingAtBid = 0
                l_obj.CloseStandingAtAsk = 0
                l_obj.standingAtBidPlus1pip = 0
                l_obj.CloseStandingAtAskMinus1pip = 0
                l_obj.EnterTradeLong = 0  # Implies make no change
            

        
        l_previous_obj = l_obj
        currentIndex = currentIndex + 1

# Squaring off if some open position there   
    if tradeStats['currentPositionLong'] > 0:
        tradeStats['NumberOfCloseSell'] += tradeStats['currentPositionLong']
        tradeStats['totalSellAmountLong'] += tradeStats['currentPositionLong'] * (l_previous_obj.BidP)
        tradeStats['currentPositionLong'] = 0
        l_obj.ReasonForTradingOrNotTradingLong = 'CloseSell(Hitting)'
    if tradeStats['currentPositionShort'] > 0:
        tradeStats['NumberOfCloseBuy'] += tradeStats['currentPositionShort']
        tradeStats['totalBuyAmountShort'] += tradeStats['currentPositionShort'] * (l_previous_obj.AskP)
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
    listOfStringsToPrint = [ str(l_previous_obj.BidQ) , str(l_previous_obj.BidP) , str(l_previous_obj.AskP) , \
                            str(l_previous_obj.AskQ) , str(l_previous_obj.TTQ) , str(l_previous_obj.LTP) ,\
                            str(currentSellPredictedValue) , str(l_previous_obj.EnterTradeShort) ,l_previous_obj.ReasonForTradingOrNotTradingShort , str(currentBuyPredictedValue) ,\
                            str(l_previous_obj.EnterTradeLong) ,l_previous_obj.ReasonForTradingOrNotTradingLong , str(tradeStats['NumberOfCloseBuy']),\
                            str(tradeStats['NumberOfOpenBuy']),str(tradeStats['NumberOfOpenSell']),\
                            str(tradeStats['NumberOfCloseBuy']),str(lDummyBidQ0),str(lDummyAskQ0),\
                            str(lDummyTTQForBuy),str(lDummyTTQForSell),str(l_best_bidq),str(l_best_bidp),str(l_best_askp), str(l_best_askq) ]
    attribute.aList[currentIndex-1][3] =  ";".join(listOfStringsToPrint) 
    
    dirName = args.pd.replace('/ro/','/rs/')
    tradeLogMainDirName = dirName+"/t/"
    if not os.path.exists(tradeLogMainDirName):
        os.mkdir(tradeLogMainDirName)
    tradeLogSubDirectoryName =  tradeLogMainDirName + mainExperimentName+"/"
    if not os.path.exists(tradeLogSubDirectoryName):
        os.mkdir(tradeLogSubDirectoryName)
    
    fileName = tradeLogSubDirectoryName + pFileName + ".trade" 
    lHeaderColumnNamesList  = ['TimeStamp','CurrentPositionLong','CurrentPositionShort','BidQ0','BidP0','AskP0','AskQ0','TTQ','LTP','CurPredValueShort','EnterTradeShort','ReasonForTradingOrNotTradingShort','CurPredValueLong','EnterTradeLong','ReasonForTradingOrNotTradingLong','totalBuyTradeShort','totalBuyLong','totalSellShort','totalSellLong','DummyBidQ0','DummyAskQ0','DummyTTQChangeForSell','DummyTTQChangeForBuy' ,'BestBidQ','BestBidP','BestAskP','BestAskQ']
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
    lower_entry = totalEntryCL[0]
    upper_entry = totalEntryCL[1]
    lower_exit = totalExitCL[0]
    l_index_gap = 0.2
    l_max_gap = (upper_entry - lower_entry)/(4)
    while l_index_gap < l_max_gap:
        exitCL2 = lower_exit + float(l_index_gap) 
        exitCL1 = lower_exit + 2*float(l_index_gap) 
        exitCL0 = lower_exit + 3*float(l_index_gap) 
        exitCL = lower_exit + 4*float(l_index_gap)
        if(lower_entry < exitCL):
            lower_entry = lower_exit + 4*float(l_index_gap)
        entryCL2 = lower_entry + float(l_index_gap)
        entryCL1 = lower_entry + 2*float(l_index_gap) 
        entryCL0 = lower_entry + 3*float(l_index_gap) 
        entryCL = lower_entry + 4*float(l_index_gap)
        l_entry_list = [entryCL2,entryCL1,entryCL0 , entryCL]
        l_exit_list = [exitCL2,exitCL1,exitCL0 , exitCL]
        print("Entry Exit list" + str(l_entry_list)+ str(l_exit_list))
        if(exitCL < entryCL2 and entryCL <= upper_entry):
            lInitialFileName = args.a + '-td.' + os.path.basename(os.path.abspath(args.td)) + \
                           '-dt.' + args.dt + '-targetClass.' + args.targetClass + '-f.' + experimentName + "-wt." + args.wt+ attribute.generateExtension() + \
                           '-l.'+entryCL+"-"+entryCL0+"-"+entryCL1+"-"+entryCL2+"-"+exitCL +"-"+exitCL0 +"-"+exitCL1 +"-"+exitCL2 + "-tq." + args.orderQty  + "-te.10" 
            initialFileName.append(lInitialFileName)
            for lFileName in initialFileName:
                readOnceAndWrite(lFileName, l_entry_list, l_exit_list, predictedValuesDict)
        else:
            l_index_gap = l_index_gap + 0.1
    
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


