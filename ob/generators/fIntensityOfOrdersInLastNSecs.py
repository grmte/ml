import sys, dataFile, colNumberOfData, attribute, common
from collections import deque
from math import exp,sqrt

class values_to_be_stored_across_whole_file(object):
    def __init__(self):
        self.totalBuyTradedQty = 0.0
        self.totalSellTradedQty = 0.0
        self.buyIntensitySum = 0.0
        self.sellIntensitySum = 0.0
        self.count = 0
         
class ticks_values_to_be_stored(object):
    def __init__(self):
        self.MsgCode = ''
        self.OrderType = ''
        self.NewP = 0.0
        self.NewQ = 0
        self.BidP0 = 0.0
        self.AskP0 = 0.0
        self.BidQ0 = 0
        self.AskQ0 = 0
        self.LTP = 0.0
        self.TTQ = 0
        self.typeOfCase = ''
        self.buyIntensityValue = 0.0
        self.sellIntensityValue = 0.0

def updateCurrentTickAdditionToQueue( pCurrentTickObject, pPreviousTickObject , pDataFileObject , timeElapsed):

    if pPreviousTickObject != None:
        if pCurrentTickObject.MsgCode == "T":
            if  pCurrentTickObject.NewP == pPreviousTickObject.AskP0:
                pCurrentTickObject.typeOfCase = "BUY_TRADE"
                pDataFileObject.totalBuyTradedQty += pCurrentTickObject.NewQ
                
        if pCurrentTickObject.MsgCode == "T":
            if  pCurrentTickObject.NewP == pPreviousTickObject.BidP0:
                pCurrentTickObject.typeOfCase = "SELL_TRADE"
                pDataFileObject.totalSellTradedQty += pCurrentTickObject.NewQ

    if timeElapsed != 0:
        pCurrentTickObject.buyIntensityValue = float(pDataFileObject.totalBuyTradedQty) / timeElapsed
        pCurrentTickObject.sellIntensityValue = float(pDataFileObject.totalSellTradedQty) / timeElapsed
    else:
        pCurrentTickObject.buyIntensityValue = pDataFileObject.totalBuyTradedQty
        pCurrentTickObject.sellIntensityValue = pDataFileObject.totalSellTradedQty
        
    pDataFileObject.buyIntensitySum += pCurrentTickObject.buyIntensityValue
    pDataFileObject.sellIntensitySum += pCurrentTickObject.sellIntensityValue 
    
    pDataFileObject.count += 1
     
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

                                           
def updateTickDeletionFromQueue(pObjectToBeDeleted , pDataFileObject ):

    if pObjectToBeDeleted.typeOfCase == "BUY_TRADE":
        pDataFileObject.totalBuyTradedQty -= pObjectToBeDeleted.NewQ
                
    if pObjectToBeDeleted.typeOfCase == "SELL_TRADE":
        pDataFileObject.totalSellTradedQty += pObjectToBeDeleted.NewQ

    pDataFileObject.buyIntensitySum -= pObjectToBeDeleted.buyIntensityValue
    pDataFileObject.sellIntensitySum -= pObjectToBeDeleted.sellIntensityValue 
    
    pDataFileObject.count -= 1
     
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
          
def extractAttributeFromDataMatrix(args):
    N = 5
    if args.n == None:
        N = 5
    else:
        N = int(args.n) 
    
    try:
        args.c
    except:
        import os
        print "Since -c has not been specified I cannot proceed"
        os._exit()
       
    colNumberOfTimeStamp = colNumberOfData.TimeStamp
    numberOfRowsInLastNSecs = 0
    queueOfValuesInLastNSecs = deque()
    timeOfOldestRow = common.convertTimeStampFromStringToFloat(dataFile.matrix[0][colNumberOfTimeStamp])
    currentRowNumberForWhichFeatureValueIsBeingCalculated = 0
    lengthOfDataMatrix = len(dataFile.matrix)
    l_global_file_object = values_to_be_stored_across_whole_file()
    lPreviousTickObject = None
    while (currentRowNumberForWhichFeatureValueIsBeingCalculated < lengthOfDataMatrix):
        if len(queueOfValuesInLastNSecs) != 0:
            lPreviousTickObject = queueOfValuesInLastNSecs[-1][0]
        lCurrentTickObject = ticks_values_to_be_stored()
        lCurrentDataRow = dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated]
        timeOfCurrentRow = common.convertTimeStampFromStringToFloat(lCurrentDataRow[colNumberOfTimeStamp],args.cType)
        timeElapsed = timeOfCurrentRow - timeOfOldestRow
        if (timeElapsed < N):
            lCurrentTickObject.MsgCode = lCurrentDataRow[colNumberOfData.MsgCode]
            lCurrentTickObject.OrderType = lCurrentDataRow[colNumberOfData.OrderType]
            lCurrentTickObject.NewP = float(lCurrentDataRow[colNumberOfData.NewP])
            lCurrentTickObject.NewQ = int(lCurrentDataRow[colNumberOfData.NewQ])
            lCurrentTickObject.BidP0 = float(lCurrentDataRow[colNumberOfData.BidP0])
            lCurrentTickObject.AskP0 = float(lCurrentDataRow[colNumberOfData.AskP0])
            lCurrentTickObject.BidQ0 = int(float(lCurrentDataRow[colNumberOfData.BidQ0]))
            lCurrentTickObject.AskQ0 = int(float(lCurrentDataRow[colNumberOfData.AskQ0]))
            lCurrentTickObject.LTP = float(lCurrentDataRow[colNumberOfData.LTP])
            lCurrentTickObject.TTQ = int(float(lCurrentDataRow[colNumberOfData.TTQ]))
            updateCurrentTickAdditionToQueue(lCurrentTickObject, lPreviousTickObject , l_global_file_object , timeElapsed)
            lBuyIntensityMinusSellInstensity =  lCurrentTickObject.buyIntensityValue  - lCurrentTickObject.sellIntensityValue 
            try:
                lBuyIntensityMean =  ( float(l_global_file_object.buyIntensitySum) / l_global_file_object.count )
            except:
                lBuyIntensityMean =  float(l_global_file_object.buyIntensitySum)
            lBuyIntensityVariance = ( lCurrentTickObject.buyIntensityValue - lBuyIntensityMean) *  (lCurrentTickObject.buyIntensityValue - lBuyIntensityMean)
            try:
                lSellIntensityMean =  ( float(l_global_file_object.sellIntensitySum) / l_global_file_object.count )
            except:
                lSellIntensityMean =   float(l_global_file_object.sellIntensitySum)
                
            lSellIntensityVariance = (lCurrentTickObject.sellIntensityValue - lSellIntensityMean) *  (lCurrentTickObject.sellIntensityValue - lSellIntensityMean)
            
            try:
                lFeatureValue = lBuyIntensityMinusSellInstensity / sqrt( lBuyIntensityVariance + lSellIntensityVariance )
            except:
                lFeatureValue = lBuyIntensityMinusSellInstensity
                
            attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][0] = common.convertTimeStampFromStringToDecimal(lCurrentDataRow[colNumberOfTimeStamp])
            attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][1] = str(lFeatureValue) 
            attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][2] = ";".join( map( str , [ timeElapsed , l_global_file_object.totalBuyTradedQty , l_global_file_object.totalSellTradedQty , lCurrentTickObject.buyIntensityValue , lCurrentTickObject.sellIntensityValue , \
                                                                                                              l_global_file_object.buyIntensitySum , l_global_file_object.sellIntensitySum ,\
                                                                                                          lBuyIntensityMean , lSellIntensityMean ,  lBuyIntensityVariance , lSellIntensityVariance , lCurrentTickObject.MsgCode ,\
                                                                                                          lCurrentTickObject.OrderType , lCurrentTickObject.NewP , lCurrentTickObject.NewQ  , lCurrentTickObject.BidP0 , lCurrentTickObject.AskP0 , \
                                                                                                          lCurrentTickObject.BidQ0 , lCurrentTickObject.AskQ0  , lCurrentTickObject.LTP , lCurrentTickObject.TTQ] ) )

            queueOfValuesInLastNSecs.append([lCurrentTickObject,timeOfCurrentRow])
            numberOfRowsInLastNSecs += 1   # Every append gets a +1 
            currentRowNumberForWhichFeatureValueIsBeingCalculated += 1
            continue     # Since we are going back 1 row from current we cannot get data from current row
        
        else:
            # We need to reset the timeOfOldestRow since timeElapsed has exceeded N seconds
            while(timeElapsed >= N):
                if(len(queueOfValuesInLastNSecs) == 0):
                    timeOfOldestRow = timeOfCurrentRow
                    timeElapsed = 0
                    if(numberOfRowsInLastNSecs != 0):
                        print "Sanity check: This condition is not possible logically. numberOfRowsInLastNSecs should been 0. There has been an unknown error"
                        sys.exit(-1)
                else:   
                    oldestElementInQueue = queueOfValuesInLastNSecs.popleft()
                    colValueInOldestElementInQueue = oldestElementInQueue[0]
                    colTimeStampInOldestElementInQueue = oldestElementInQueue[1]
                    updateTickDeletionFromQueue(colValueInOldestElementInQueue , l_global_file_object )
                    timeOfOldestRow = colTimeStampInOldestElementInQueue
                    numberOfRowsInLastNSecs -= 1 # every pop from the queue gets a -1
                    timeElapsed = timeOfCurrentRow - timeOfOldestRow
                    if(len(queueOfValuesInLastNSecs) != numberOfRowsInLastNSecs):
                        print "Sanity check: This condition is not possible logically. There has been an unknown error"
                        sys.exit(-1)
        
        print "Processed row number " + str(currentRowNumberForWhichFeatureValueIsBeingCalculated)

    lNameOfFeaturePrinted = "fIntensityOfOrdersInLast" + str(args.n) + "Secs" 
    return [ "TimeStamp", lNameOfFeaturePrinted , "TimeElapsed" ,"totalBuyTradedQty","totalSellTradedQty" ,\
            "BuyIntensityValue" , "SellIntensityValue" , "BuyIntensityValueSum" , "SellIntensityValueSum" , \
            "BuyIntensityMean" , "SellIntensityMean" , "BuyIntensityVariance" , "SellIntensityVariance" , "MsgCode" , "Ordertype" ,"NewP","NewQ","BidP0","AskP0","BidQ","AskQ","LTP","TTQ"
            ]
            
