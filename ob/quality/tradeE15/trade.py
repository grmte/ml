#!/usr/bin/python
from __future__ import division
from __future__ import print_function
import os,sys
sys.path.append("./src/")
sys.path.append("./ob/generators/")
sys.path.append("./ob/quality/tradeE15/")
import dataFile, colNumberOfData, common
import  attribute , dd

from itertools import islice

def getDataFileAndPredictionsIntoObjectList(dataFileObject,pFileObjectList,lMinOfExitCl):
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
    lFeatureFileRowList = {}
    for index in xrange(len(pFileObjectList)):
        if dd.gTreeVariablesPresent[index].lower() != "buyprob" and dd.gTreeVariablesPresent[index].lower() != "sellprob":  
            lFeatureFileRowList[ dd.gTreeVariablesPresent[index] ] = (list(islice(pFileObjectList[index],10000)))
    while True:
        lDataFileRowsList = list(islice(dataFileObject,dd.gNoOfLineReadPerChunk))
        lFeatureFileRowList = []
        index = 0
        lFeatureFileRowList = {}
        for index in xrange(len(pFileObjectList)):
            lFeatureFileRowList[ dd.gTreeVariablesPresent[index] ] = (list(islice(pFileObjectList[index],dd.gNoOfLineReadPerChunk)))
        if not lDataFileRowsList:
            print("Finished reading file")
            lObjectList.append(lPrevObj)    
            lPrevObj = None          
            break
        lengthOfDataList = len(lDataFileRowsList)
        for features in lFeatureFileRowList:
            if lengthOfDataList != len(lFeatureFileRowList[features]):
                print("Length of data file and feature file are not same ")
                os._exit(-1)                
        for currentRowIndex in range(lengthOfDataList):
            if(fileHasHeader == 1 and headerSkipped != 1):
                headerSkipped = 1 
                continue
            lDataRow = lDataFileRowsList[currentRowIndex].rstrip().split(dataFileSep)
            '''
            if((args.e).find("nsefut") >= 0):
                lAskP = float(lDataRow[colNumberOfData.BestAskP])
                lBidP = float(lDataRow[colNumberOfData.BestBidP])
                lAskQ = int(lDataRow[colNumberOfData.BestAskQ])
                lBidQ = int(lDataRow[colNumberOfData.BestBidQ])
            else:
            '''
            lAskP = float(lDataRow[colNumberOfData.AskP0])
            lBidP = float(lDataRow[colNumberOfData.BidP0])
            lAskQ = int(lDataRow[colNumberOfData.AskQ0])
            lBidQ = int(lDataRow[colNumberOfData.BidQ0])
            lTTQ = int(lDataRow[colNumberOfData.TTQ])
            lLTP = float(lDataRow[colNumberOfData.LTP]) 
            lCurrentDataRowTimeStamp = common.convertTimeStampFromStringToFloat(lDataRow[colNumberOfData.TimeStamp])
            lFeatureValueDict = {}
            for feature in lFeatureFileRowList:
                if feature.lower() == "buyprob" or feature.lower() == "sellprob":
                    lSep = ","
                    lTimeStampIndex = 1
                    lFeatureIndex = 2
                else:
                    lSep = ";"
                    lTimeStampIndex = 0
                    lFeatureIndex = 1
                #print("Varible name" , feature)
                lFeatureFileRow = lFeatureFileRowList[feature][currentRowIndex].rstrip().split(lSep)
                lFeatureFileTimeStamp = float(lFeatureFileRow[lTimeStampIndex])
                lFeatureFileValue = float(lFeatureFileRow[lFeatureIndex])
                if lCurrentDataRowTimeStamp != lFeatureFileTimeStamp:
                    print('Time stamp of data row with feature value is not matching .\n Data row time stamp :- ' , lCurrentDataRowTimeStamp,'Feature value Time Stamp :- ' , lFeatureFileTimeStamp)
                    os._exit(-1)
                lFeatureValueDict[feature]=lFeatureFileValue
            lObj = dd.Tick(lCurrentDataRowTimeStamp,lAskP,lBidP,lAskQ,lBidQ,lLTP,lTTQ,lFeatureValueDict)
            if lPrevObj!=None:
                lPrevObj.TTQChange  = lObj.TTQ - lPrevObj.TTQ
                lPrevObj.NextLTP = lObj.LTP
                if ( lPrevObj.AskP -lPrevObj.BidP > dd.gTickSize ) and ( lPrevObj.TTQChange == 0 ):
                    if lPrevObj.BidP not in lListOfBidP:
                        lListOfBidP.append(lPrevObj.BidP)
                    if lPrevObj.AskP not in lListOfAskP:
                        lListOfAskP.append(lPrevObj.AskP)
                    pass
                else:
                    if (1):
                        if len(lListOfBidP) > 1:
                            lPrevObj.bidPChangedInBetweenLastTickAndCurrentTick = 1
                        if len(lListOfAskP) > 1:
                            lPrevObj.askPChangedInBetweenLastTickAndCurrentTick = 1
                        lObjectList.append(lPrevObj)  
                        lListOfBidP = [lPrevObj.BidP]
                        lListOfAskP = [lPrevObj.AskP]
                    else:
                        if lPrevObj.BidP not in lListOfBidP:
                            lListOfBidP.append(lPrevObj.BidP)
                        if lPrevObj.AskP not in lListOfAskP:
                            lListOfAskP.append(lPrevObj.AskP)
            lPrevObj = lObj
            if lCurrentDataRowCount%50000 ==0:
                print("Completed reading ",lCurrentDataRowCount)
            lCurrentDataRowCount = lCurrentDataRowCount + 1 
    return lObjectList

def checkIfDecisionToEnterOrExitTradeIsSuccessful(pObject, pEnterTradeShort, pEnterTradeLong, pTradeStats,pReasonForTrade ,pPrevReasonForTradingOrNotTradingLong, pPrevReasonForTradingOrNotTradingShort ):
    lSpread = pObject.AskP - pObject.BidP
    lReasonForTradingOrNotTradingShort = ""
    lReasonForTradingOrNotTradingLong = ""

    if pObject.BidP in dd.g_quantity_adjustment_list_for_sell and pObject.bidPChangedInBetweenLastTickAndCurrentTick==0:
        l_dummy_BidQ0 = max( 0 , pObject.BidQ - dd.g_quantity_adjustment_list_for_sell[pObject.BidP])
    else:
        dd.g_quantity_adjustment_list_for_sell = {}
        l_dummy_BidQ0 =  pObject.BidQ

    if pObject.AskP in dd.g_quantity_adjustment_list_for_buy and pObject.askPChangedInBetweenLastTickAndCurrentTick==0:
        l_dummy_AskQ0 = max( 0 ,pObject.AskQ - dd.g_quantity_adjustment_list_for_buy[pObject.AskP])
    else:
        dd.g_quantity_adjustment_list_for_buy = {}    
        l_dummy_AskQ0 = pObject.AskQ
        
    if(pEnterTradeShort == 0 and pEnterTradeLong == 0):
        return lReasonForTradingOrNotTradingShort , lReasonForTradingOrNotTradingLong ,0 , 0 , 0 , 0

    l_dummy_TTQChange_For_Buy = pObject.TTQChange
    #close buy
    if(pEnterTradeShort == -1): # Need to buy we come here only if currentPosition is greater than 0 so no need to check again.
        #standing
        if lSpread > dd.gTickSize:        
            if(l_dummy_TTQChange_For_Buy<=0):
                pReasonForTrade['VolumeDidNotIncreaseDuringBuyAttemptShort'] += 1
                lReasonForTradingOrNotTradingShort = '(Spread>Pip)&&(NextTickTTQDidNotIncrease)'
            elif(pObject.NextLTP != pObject.BidP): 
                pReasonForTrade['LTPDoesNotEqualBidP0Short'] += 1
                lReasonForTradingOrNotTradingShort = '(Spread>Pip)&&(LTP!=Bid)'
            else:    
               
                lQtyTraded = min(  pTradeStats['currentPositionShort'] , l_dummy_TTQChange_For_Buy )
                l_dummy_TTQChange_For_Buy -= lQtyTraded
                pTradeStats['totalBuyValueShort'] += lQtyTraded * (pObject.BidP + dd.gTickSize)
                pTradeStats['currentPositionShort'] -= lQtyTraded
                lReasonForTradingOrNotTradingShort = 'CloseBuy(Standing)'
                pReasonForTrade['CloseBuyTradeHappened'] += lQtyTraded
        #hitting
        else:

            l_buy_qty = min( pTradeStats['currentPositionShort'], l_dummy_AskQ0)
            if pObject.AskP in dd.g_quantity_adjustment_list_for_buy:
                    dd.g_quantity_adjustment_list_for_buy[pObject.AskP] += l_buy_qty
            else:  
                    dd.g_quantity_adjustment_list_for_buy = {} 
                    dd.g_quantity_adjustment_list_for_buy[pObject.AskP] = l_buy_qty
            l_dummy_AskQ0 -= l_buy_qty
            pTradeStats['totalBuyValueShort'] += l_buy_qty * (pObject.AskP)
            pTradeStats['currentPositionShort'] -= l_buy_qty
            pReasonForTrade['CloseBuyTradeHappened'] += l_buy_qty
             
            if l_buy_qty > 0:
                lReasonForTradingOrNotTradingShort = 'CloseBuy(Hitting)'
            else :
                lReasonForTradingOrNotTradingShort = "DummyAskQExhuasted"
        
    #open buy
    if(pEnterTradeLong == 1 and ( dd.gMaxQty - pTradeStats['currentPositionLong'] ) > 0): # Need to buy
        #standing
        if lSpread > dd.gTickSize:        
            if(l_dummy_TTQChange_For_Buy <= 0 ):
                pReasonForTrade['VolumeDidNotIncreaseDuringBuyAttemptLong'] += 1
                lReasonForTradingOrNotTradingLong = '(Spread>Pip)&&(NextTickTTQDidNotIncrease)'
            elif(pObject.NextLTP != pObject.BidP):
                pReasonForTrade['LTPDoesNotEqualBidP0Long'] += 1
                lReasonForTradingOrNotTradingLong = '(Spread>Pip)&&(LTPDoesNotEqualBidP0Long)'
            else:

                lQtyToBeTraded = ( dd.gMaxQty - pTradeStats['currentPositionLong'] )
                lQtyForWhichWeTrade = min( lQtyToBeTraded , l_dummy_TTQChange_For_Buy)
                l_dummy_TTQChange_For_Buy -= lQtyForWhichWeTrade
                pTradeStats['totalBuyValueLong'] += lQtyForWhichWeTrade * (pObject.BidP + dd.gTickSize)
                pTradeStats['currentPositionLong'] += lQtyForWhichWeTrade
                lReasonForTradingOrNotTradingLong = 'OpenBuy(Standing)'
                pReasonForTrade['OpenBuyTradeHappened'] += lQtyForWhichWeTrade
        #hitting
        else:
            if l_dummy_AskQ0 > 0 :

                lQtyToBeTraded = ( dd.gMaxQty - pTradeStats['currentPositionLong'] )
                lQtyForWhichWeTrade = min( lQtyToBeTraded , l_dummy_AskQ0 )
                if pObject.AskP in dd.g_quantity_adjustment_list_for_buy:
                    dd.g_quantity_adjustment_list_for_buy[pObject.AskP] += lQtyForWhichWeTrade
                else:
                    dd.g_quantity_adjustment_list_for_buy = {}
                    dd.g_quantity_adjustment_list_for_buy[pObject.AskP] = lQtyForWhichWeTrade
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
        if lSpread > dd.gTickSize:        
            if(l_dummy_TTQChange_For_Sell <= 0 ):
                pReasonForTrade['VolumeDidNotIncreaseDuringSellAttemptLong'] += 1
                lReasonForTradingOrNotTradingLong = '(Spread>Pip)&&(NextTickTTQDidNotIncrease)'
            elif(pObject.NextLTP != pObject.AskP): 
                pReasonForTrade['LTPDoesNotEqualAskP0Long'] += 1
                lReasonForTradingOrNotTradingLong = '(Spread>Pip)&&(NextTickLTP!=Ask)'
            else:    

                lQtyTraded = min(  pTradeStats['currentPositionLong'] , l_dummy_TTQChange_For_Sell )
                pTradeStats['totalSellValueLong'] += lQtyTraded * (pObject.AskP - dd.gTickSize)
                pTradeStats['currentPositionLong'] -= lQtyTraded
                l_dummy_TTQChange_For_Sell -= lQtyTraded
                lReasonForTradingOrNotTradingLong = 'CloseSell(Standing)'
                pReasonForTrade['CloseSellTradeHappened'] += lQtyTraded
        #hitting
        else:

            lQtyTraded = min( pTradeStats['currentPositionLong'] , l_dummy_BidQ0 )
            if pObject.BidP in dd.g_quantity_adjustment_list_for_sell:
                dd.g_quantity_adjustment_list_for_sell[pObject.BidP] += lQtyTraded
            else:
                dd.g_quantity_adjustment_list_for_sell = {}
                dd.g_quantity_adjustment_list_for_sell[pObject.BidP] = lQtyTraded
            pTradeStats['totalSellValueLong'] += lQtyTraded * (pObject.BidP)
            pTradeStats['currentPositionLong'] -= lQtyTraded
            l_dummy_BidQ0 -= lQtyTraded
            
            if lQtyTraded > 0 :
                lReasonForTradingOrNotTradingLong = 'CloseSell(Hitting)'
            else :
                lReasonForTradingOrNotTradingLong = "DummyBidQExhuasted"
            pReasonForTrade['CloseSellTradeHappened'] += lQtyTraded
    
    #open sell
    if(pEnterTradeShort == 1 and  ( dd.gMaxQty - pTradeStats['currentPositionShort'] ) > 0 ): # Need to sell
        #standing
        if lSpread > dd.gTickSize:        
            if(l_dummy_TTQChange_For_Sell <= 0):
                pReasonForTrade['VolumeDidNotIncreaseDuringSellAttemptShort'] += 1
                lReasonForTradingOrNotTradingShort = '(Spread>Pip)&&(NextTickTTQDidNotIncrease)'
            elif(pObject.NextLTP != pObject.AskP):
                pReasonForTrade['LTPDoesNotEqualAskP0Short'] += 1
                lReasonForTradingOrNotTradingShort = '(Spread>Pip)&&(NextTickLTP!=Ask)'
            else:

                lQtyToBeTraded = ( dd.gMaxQty - pTradeStats['currentPositionShort'] )
                lQtyForWhichWeTrade = min( lQtyToBeTraded , l_dummy_TTQChange_For_Sell)
                pTradeStats['totalSellValueShort'] += lQtyForWhichWeTrade * (pObject.AskP - dd.gTickSize)
                pTradeStats['currentPositionShort'] += lQtyForWhichWeTrade
                l_dummy_TTQChange_For_Sell -= lQtyForWhichWeTrade
                lReasonForTradingOrNotTradingShort = 'OpenSell(Standing)'
                pReasonForTrade['OpenSellTradeHappened'] += lQtyForWhichWeTrade
        #hitting
        else:
            if l_dummy_BidQ0 > 0 :

                lQtyToBeTraded = ( dd.gMaxQty - pTradeStats['currentPositionShort'] )
                lQtyForWhichWeTrade = min( lQtyToBeTraded , l_dummy_BidQ0 )
                if pObject.BidP in dd.g_quantity_adjustment_list_for_sell:
                    dd.g_quantity_adjustment_list_for_sell[pObject.BidP] += lQtyForWhichWeTrade
                else:
                    dd.g_quantity_adjustment_list_for_sell = {}
                    dd.g_quantity_adjustment_list_for_sell[pObject.BidP] = lQtyForWhichWeTrade
                pTradeStats['totalSellValueShort'] += lQtyForWhichWeTrade * (pObject.BidP)
                pTradeStats['currentPositionShort'] += lQtyForWhichWeTrade
                lReasonForTradingOrNotTradingShort = 'OpenSell(Hitting)'
                pReasonForTrade['OpenSellTradeHappened'] += lQtyForWhichWeTrade
                l_dummy_BidQ0 -= lQtyForWhichWeTrade
            else:
                lReasonForTradingOrNotTradingShort = 'DummyBidQZero'
    return lReasonForTradingOrNotTradingShort, lReasonForTradingOrNotTradingLong,l_dummy_BidQ0 , l_dummy_AskQ0 , l_dummy_TTQChange_For_Buy , l_dummy_TTQChange_For_Sell

def doTrade(pFileName, pEntryCL, pExitCL, pObjectList,predictionDir,mainExperimentName):
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
    #         if args.pT.lower()=="yes":
    #              attribute.aList =  [[0 for x in xrange(4)] for x in xrange(len(pObjectList))]
    lFormulaForOpenBuy = dd.gFinalCondition['buy'][pEntryCL]
    lFormulaForCloseBuy = dd.gFinalCondition['buy'][pExitCL]
    lFormulaForOpenSell = dd.gFinalCondition['sell'][pEntryCL]
    lFormulaForCloseSell = dd.gFinalCondition['sell'][pExitCL]
    print("OpenBuy Formula" , lFormulaForOpenBuy)
    print("CloseBuy Formula" , lFormulaForCloseBuy)
    print("OpenSell Formula" , lFormulaForOpenSell)
    print("CloseSell Formula" , lFormulaForCloseSell)
    for lObject in pObjectList[:-1]:
        for variable in dd.gTreeVariablesPresent:
            #print('%s = lObject.featureDict["%s"]' %(variable,variable))
            exec('%s = lObject.featureDict["%s"]' %(variable,variable))
            
        #short decisions
        if(eval(lFormulaForOpenSell)):
            enterTradeShort = 1
            numberOfTimesAskedToEnterTradeShort += 1
        elif(eval(lFormulaForCloseBuy) and tradeStats['currentPositionShort'] > 0):
            numberOfTimesAskedToExitTradeShort += 1
            enterTradeShort = -1  # Implies to exit the trade
        else:
            enterTradeShort = 0  # Implies make no change
            
        #long decisions
        if(eval(lFormulaForOpenBuy)):
            enterTradeLong = 1
            numberOfTimesAskedToEnterTradeLong += 1
        elif(eval(lFormulaForCloseSell) and tradeStats['currentPositionLong'] > 0):
            numberOfTimesAskedToExitTradeLong += 1
            enterTradeLong = -1  # Implies to exit the trade
        else:
            enterTradeLong = 0  # Implies make no change
        
        lReasonForTradingOrNotTradingShort, lReasonForTradingOrNotTradingLong, lDummyBidQ0 , lDummyAskQ0 , lDummyTTQForBuy , lDummyTTQForSell= checkIfDecisionToEnterOrExitTradeIsSuccessful(lObject, enterTradeShort,enterTradeLong,tradeStats,reasonForTrade,lReasonForTradingOrNotTradingLong,lReasonForTradingOrNotTradingShort )
        attribute.aList[currentIndex][0] = lObject.currentTimeStamp
        attribute.aList[currentIndex][1] = tradeStats['currentPositionLong']
        attribute.aList[currentIndex][2] = tradeStats['currentPositionShort']
        listOfStringsToPrint = [ str(lObject.BidQ) , str(lObject.BidP) , str(lObject.AskP) , \
                                str(lObject.AskQ) , str(lObject.TTQ) , str(lObject.NextLTP) ,\
                                str(SA) , str(enterTradeShort) ,lReasonForTradingOrNotTradingShort , str(sellProb) ,\
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

    dirName = predictionDir.replace('/ro/','/rs/')
    
    attribute.aList[currentIndex][0] = lObject.currentTimeStamp
    attribute.aList[currentIndex][1] = tradeStats['currentPositionLong']
    attribute.aList[currentIndex][2] = tradeStats['currentPositionShort']
    listOfStringsToPrint = [ str(lObject.BidQ) , str(lObject.BidP) , str(lObject.AskP) , \
                            str(lObject.AskQ) , str(lObject.TTQ) , str(lObject.NextLTP) ,\
                            str("lObject.currentSellPredictedValue") , str(enterTradeShort) ,lReasonForTradingOrNotTradingShort , str("lObject.currentBuyPredictedValue") ,\
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
    lHeaderColumnNamesList  = ['TimeStamp','CurrentPositionLong','CurrentPositionShort','BidQ0','BidP0','AskP0','AskQ0','TTQ','LTP','SA','EnterTradeShort','ReasonForTradingOrNotTradingShort','sellProb','EnterTradeLong','ReasonForTradingOrNotTradingLong','totalBuyTradeShort','totalBuyLong','totalSellShort','totalSellLong','DummyBidQ0','DummyAskQ0','DummyTTQChangeForSell','DummyTTQChangeForBuy']
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
    net_short_profit = gross_short_profit - ( dd.gTransactionCost * ( tradeStats['totalSellValueShort'] +  tradeStats['totalBuyValueShort'] ) ) 
    net_long_profit = gross_long_profit - ( dd.gTransactionCost * ( tradeStats['totalSellValueLong'] +  tradeStats['totalBuyValueLong'] ) )
    net_profit = net_short_profit + net_long_profit
    
    gross_short_profit_in_dollars = gross_profit / (dd.currencyDivisor * 60)
    net_profit_in_dollars = net_profit / (dd.currencyDivisor * 60 )
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


