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

totalEntryCL = args.entryCL.split(";")
totalExitCL = args.exitCL.split(";")
initialFileName = []
for indexOfCL in range(0,len(totalEntryCL)):
    lInitialFileName = args.a + '-td.' + os.path.basename(os.path.abspath(args.td)) + \
                   '-dt.' + args.dt + '-targetClass.' + args.targetClass + '-f.' + experimentName + "-wt." + args.wt+ attribute.generateExtension() + \
                   '-l.'+totalEntryCL[indexOfCL]+"-"+totalExitCL[indexOfCL] + "-tq." + args.orderQty + "-te.7" 
    initialFileName.append(lInitialFileName)
    

g_quantity_adjustment_list_for_sell = {}
g_quantity_adjustment_list_for_buy = {}

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
#         os._exit(-1)
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
#         os._exit(-1)
    sys.stdout.flush()
#-----------------Getting predicted values into dictionary -------------------------------------
    for elements in lPredictedBuyValuesDict.keys():
        pPredictedValuesDict[elements] = {}
        pPredictedValuesDict[elements]['buy'] = lPredictedBuyValuesDict[elements]
        pPredictedValuesDict[elements]['sell'] = lPredictedSellValuesDict[elements] 


def checkIfPreviousDecisionToEnterOrExitTradeWasSuccessful(pCurrentDataRow,pTTQAtTimeOfPreviousDataRow,pAskP0AtTimeOfPreviousDataRow,pBidP0AtTimeOfPreviousDataRow,\
                                                           pAskQ0AtTimeOfPreviousDataRow , pBidQ0AtTimeOfPreviousDataRow , pEnterTradeShort, pEnterTradeLong, pTradeStats,pReasonForTrade ,\
                                                           pPrevReasonForTradingOrNotTradingLong, pPrevReasonForTradingOrNotTradingShort ):
    global gTickSize , gMaxQty , g_quantity_adjustment_list_for_sell , g_quantity_adjustment_list_for_buy
    spreadAtTimeOfPreviousDataRow = pAskP0AtTimeOfPreviousDataRow - pBidP0AtTimeOfPreviousDataRow
    lReasonForTradingOrNotTradingShort = ""
    lReasonForTradingOrNotTradingLong = ""

    if pBidP0AtTimeOfPreviousDataRow in g_quantity_adjustment_list_for_sell:
        pBidQ0AtTimeOfPreviousDataRow = max( 0 , pBidQ0AtTimeOfPreviousDataRow - g_quantity_adjustment_list_for_sell[pBidP0AtTimeOfPreviousDataRow])
    else:
        g_quantity_adjustment_list_for_sell = {}

    if pAskP0AtTimeOfPreviousDataRow in g_quantity_adjustment_list_for_buy:
        pAskQ0AtTimeOfPreviousDataRow = max( 0 ,pAskQ0AtTimeOfPreviousDataRow - g_quantity_adjustment_list_for_buy[pAskP0AtTimeOfPreviousDataRow])
    else:
        g_quantity_adjustment_list_for_buy = {}    

    if(pEnterTradeShort == 0 and pEnterTradeLong == 0):
        return [ lReasonForTradingOrNotTradingShort , lReasonForTradingOrNotTradingLong , pBidQ0AtTimeOfPreviousDataRow , pAskQ0AtTimeOfPreviousDataRow , 0 , 0 ]

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

def readOnceAndWrite(pFileName, pIndexOfEntryOrExitCL, predictedValuesDict):
    global transactionCost , currencyDivisor 
    attribute.initList()
    enterTradeShort = 0
    enterTradeLong = 0
    ltpAtTimeOfPreviousDataRow = 0
    ttqAtTimeOfPreviousDataRow = 0
    askP0AtTimeOfPreviousDataRow = 0
    bidP0AtTimeOfPreviousDataRow = 0
    askQ0AtTimeOfPreviousDataRow = 0
    bidQ0AtTimeOfPreviousDataRow = 0
    currentTimeStamp = 0
    tradeStats = dict()
    tradeStats['totalSellValueShort'] = 0
    tradeStats['totalBuyValueShort'] = 0
    tradeStats['currentPositionShort'] = 0
    tradeStats['totalSellValueLong'] = 0
    tradeStats['totalBuyValueLong'] = 0
    tradeStats['currentPositionLong'] = 0
    noPredictionForThisRow = 0
    currentSellPredictedValue = 0
    currentBuyPredictedValue = 0
    entryCL = float(totalEntryCL[pIndexOfEntryOrExitCL])/100
    exitCL = float(totalExitCL[pIndexOfEntryOrExitCL])/100
    print (entryCL, exitCL)
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
    print("Processing the data file for trades :")
    attribute.initList()
    for currentDataRow in dataFile.matrix:
        
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
                                    str(currentSellPredictedValue) , str(enterTradeShort) ,lReasonForTradingOrNotTradingShort , str(currentBuyPredictedValue) ,\
                                    str(enterTradeLong) ,lReasonForTradingOrNotTradingLong , str(reasonForTrade['CloseBuyTradeHappened']),\
                                    str(reasonForTrade['OpenBuyTradeHappened']),str(reasonForTrade['OpenSellTradeHappened']),\
                                    str(reasonForTrade['CloseSellTradeHappened']),str(lDummyBidQ0),str(lDummyAskQ0),\
                                    str(lDummyTTQForBuy),str(lDummyTTQForSell)]
            attribute.aList[currentIndex-1][3] =  ";".join(listOfStringsToPrint)
        currentTimeStamp = common.convertTimeStampFromStringToFloat(currentDataRow[colNumberOfData.TimeStamp])
    
        try:
            currentSellPredictedValue = float(predictedValuesDict[currentTimeStamp]['sell']) 
            currentBuyPredictedValue  = float(predictedValuesDict[currentTimeStamp]['buy'])
        except:
            noPredictionForThisRow += 1
    
        #short decisions
        if(currentSellPredictedValue >= entryCL):
            enterTradeShort = 1
            numberOfTimesAskedToEnterTradeShort += 1
        elif(currentBuyPredictedValue >= exitCL and tradeStats['currentPositionShort'] > 0):
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
        if(currentBuyPredictedValue >= entryCL):
            enterTradeLong = 1
            numberOfTimesAskedToEnterTradeLong += 1
        elif(currentSellPredictedValue >= exitCL and tradeStats['currentPositionLong'] > 0):
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
    listOfStringsToPrint = [ str(bidQ0AtTimeOfPreviousDataRow) , str(bidP0AtTimeOfPreviousDataRow) , str(askP0AtTimeOfPreviousDataRow) , str(askQ0AtTimeOfPreviousDataRow) , str(ttqAtTimeOfPreviousDataRow) , str(ltpAtTimeOfPreviousDataRow) , str(currentSellPredictedValue) , str(enterTradeShort) , "" , str(currentBuyPredictedValue) , str(enterTradeLong) ,"" , str(reasonForTrade['CloseBuyTradeHappened']),str(reasonForTrade['OpenBuyTradeHappened']),str(reasonForTrade['OpenSellTradeHappened']),str(reasonForTrade['CloseSellTradeHappened']),str(lDummyBidQ0),str(lDummyAskQ0),str(lDummyTTQForBuy),str(lDummyTTQForSell)]
    attribute.aList[currentIndex-1][3] =  ";".join(listOfStringsToPrint) 
    
    dirName = args.pd.replace('/ro/','/rs/')
    tradeLogMainDirName = dirName+"/t/"
    if not os.path.exists(tradeLogMainDirName):
         os.mkdir(tradeLogMainDirName)
    tradeLogSubDirectoryName =  tradeLogMainDirName + mainExperimentName+"/"
    if not os.path.exists(tradeLogSubDirectoryName):
         os.mkdir(tradeLogSubDirectoryName)
    
    fileName = tradeLogSubDirectoryName + pFileName + ".trade" 
    lHeaderColumnNamesList  = ['TimeStamp','CurrentPositionLong','CurrentPositionShort','BidQ0','BidP0','AskP0','AskQ0','TTQ','LTP','CurPredValueShort','EnterTradeShort','ReasonForTradingOrNotTradingShort','CurPredValueLong','EnterTradeLong','ReasonForTradingOrNotTradingLong','totalBuyTradeShort','totalBuyLong','totalSellShort','totalSellLong','DummyBidQ0','DummyAskQ0','DummyTTQChangeForSell','DummyTTQChangeForBuy']
    #attribute.writeToFile(fileName , lHeaderColumnNamesList)
    
    tradeResultMainDirName = dirName+"/r/"
    if not os.path.exists(tradeResultMainDirName):
         os.mkdir(tradeResultMainDirName)
    tradeResultSubDirectoryName =  tradeResultMainDirName + mainExperimentName+"/"
    if not os.path.exists(tradeResultSubDirectoryName):
         os.mkdir(tradeResultSubDirectoryName)
    fileName = tradeResultSubDirectoryName+pFileName+".result" 
    outputFile = open(fileName,"w")
    gross_short_profit = tradeStats['totalSellValueShort'] - tradeStats['totalBuyValueShort']
    gross_long_profit = tradeStats['totalSellValueLong'] - tradeStats['totalBuyValueLong']
    gross_profit = gross_short_profit - gross_long_profit
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
    print("The net results for Short are: %.6f" + net_short_profit, file = outputFile)
    print("The net results for Long are: %.6f" + net_long_profit, file = outputFile)
    print("Gross Results in Dollars: %.6f" + gross_short_profit_in_dollars, file = outputFile)
    print("Net Results in Dollars: %.6f" + net_profit_in_dollars, file = outputFile)
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


def main():
    dataFile.getDataIntoMatrix(args.pd)
    predictedValuesDict = dict()
    getPredictedValuesIntoDict(predictedValuesDict)
    lIndexOfEntryOrExitCL = 0
    for lFileName in initialFileName:
        readOnceAndWrite(lFileName, lIndexOfEntryOrExitCL, predictedValuesDict)
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
       print(predictedBuyValuesFileName,predictedSellValuesFileName)
       print ("Predcition files not yet generated")


