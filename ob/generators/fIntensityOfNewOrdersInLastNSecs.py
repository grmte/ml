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
        self.typeOfCase = ''
        self.buyIntensityValue = 0.0
        self.sellIntensityValue = 0.0

              
def updateCurrentTickAdditionToQueue( pCurrentTickObject, pDataFileObject , timeElapsed , l_first_time_elapsed , N):

    if pCurrentTickObject.MsgCode == "N":
        if  pCurrentTickObject.OrderType.upper() =='B':
            pCurrentTickObject.typeOfCase = "BUY_NEW"
            pDataFileObject.totalBuyTradedQty += pCurrentTickObject.NewQ
            
    if pCurrentTickObject.MsgCode == "N":
        if  pCurrentTickObject.OrderType.upper() =='S':
            pCurrentTickObject.typeOfCase = "SELL_NEW"
            pDataFileObject.totalSellTradedQty += pCurrentTickObject.NewQ

    if timeElapsed != 0:
        if l_first_time_elapsed == False:
            pCurrentTickObject.buyIntensityValue = float(pDataFileObject.totalBuyTradedQty) / timeElapsed
            pCurrentTickObject.sellIntensityValue = float(pDataFileObject.totalSellTradedQty) / timeElapsed
        else:
            pCurrentTickObject.buyIntensityValue = float(pDataFileObject.totalBuyTradedQty) / N
            pCurrentTickObject.sellIntensityValue = float(pDataFileObject.totalSellTradedQty) / N            
    else:
        pCurrentTickObject.buyIntensityValue = pDataFileObject.totalBuyTradedQty
        pCurrentTickObject.sellIntensityValue = pDataFileObject.totalSellTradedQty
        
    pDataFileObject.buyIntensitySum += pCurrentTickObject.buyIntensityValue
    pDataFileObject.sellIntensitySum += pCurrentTickObject.sellIntensityValue 
    
    pDataFileObject.count += 1
     
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def variance_across_mean(queueOfValuesInLastNSecs , lBuyIntensityMean , lSellIntensityMean):
    
    l_sum_of_variance_across_buy_mean = 0.0
    l_sum_of_variance_across_sell_mean = 0.0
    for element in queueOfValuesInLastNSecs:
        lObj = element[0]
        l_sum_of_variance_across_buy_mean = l_sum_of_variance_across_buy_mean +  ( ( lObj.buyIntensityValue - lBuyIntensityMean )**2)
        l_sum_of_variance_across_sell_mean = l_sum_of_variance_across_sell_mean +  ( ( lObj.sellIntensityValue - lSellIntensityMean )**2)
    return l_sum_of_variance_across_buy_mean , l_sum_of_variance_across_sell_mean

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
                                           
def updateTickDeletionFromQueue(pObjectToBeDeleted , pDataFileObject ):

    if pObjectToBeDeleted.typeOfCase == "BUY_NEW":
        pDataFileObject.totalBuyTradedQty -= pObjectToBeDeleted.NewQ
                
    if pObjectToBeDeleted.typeOfCase == "SELL_NEW":
        pDataFileObject.totalSellTradedQty -= pObjectToBeDeleted.NewQ

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
    l_first_time_elapsed = False   
    queueOfValuesInLastNSecs = deque()
    timeOfOldestRow = common.convertTimeStampFromStringToFloat(dataFile.matrix[0][colNumberOfTimeStamp])
    currentRowNumberForWhichFeatureValueIsBeingCalculated = 0
    lengthOfDataMatrix = len(dataFile.matrix)
    l_global_file_object = values_to_be_stored_across_whole_file()
    while (currentRowNumberForWhichFeatureValueIsBeingCalculated < lengthOfDataMatrix):
        lCurrentTickObject = ticks_values_to_be_stored()
        lCurrentDataRow = dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated]
        timeOfCurrentRow = common.convertTimeStampFromStringToFloat(lCurrentDataRow[colNumberOfTimeStamp],args.cType)
        timeElapsed = timeOfCurrentRow - timeOfOldestRow
        if (timeElapsed < N):
            lCurrentTickObject.MsgCode = lCurrentDataRow[colNumberOfData.MsgCode]
            lCurrentTickObject.OrderType = lCurrentDataRow[colNumberOfData.OrderType]
            lCurrentTickObject.NewP = float(lCurrentDataRow[colNumberOfData.NewP])
            lCurrentTickObject.NewQ = int(lCurrentDataRow[colNumberOfData.NewQ])
            updateCurrentTickAdditionToQueue(lCurrentTickObject, l_global_file_object , timeElapsed , l_first_time_elapsed , N )
            lBuyIntensityMinusSellInstensity =  lCurrentTickObject.buyIntensityValue  - lCurrentTickObject.sellIntensityValue 
            try:
                lBuyIntensityMean =  ( float(l_global_file_object.buyIntensitySum) / l_global_file_object.count )
            except:
                lBuyIntensityMean =  float(l_global_file_object.buyIntensitySum)
            try:
                lSellIntensityMean =  ( float(l_global_file_object.sellIntensitySum) / l_global_file_object.count )
            except:
                lSellIntensityMean =   float(l_global_file_object.sellIntensitySum)

            lBuyIntensityVariance,lSellIntensityVariance = variance_across_mean(queueOfValuesInLastNSecs , lBuyIntensityMean , lSellIntensityMean)
                
            try:
                lFeatureValue = lBuyIntensityMinusSellInstensity / sqrt( lBuyIntensityVariance/l_global_file_object.count + lSellIntensityVariance/l_global_file_object.count )
            except:
                lFeatureValue = lBuyIntensityMinusSellInstensity
                
            attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][0] = common.convertTimeStampFromStringToDecimal(lCurrentDataRow[colNumberOfTimeStamp])
            attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][1] = str(lFeatureValue) 
            attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][2] = ";".join( map( str , [ timeElapsed , l_global_file_object.totalBuyTradedQty , l_global_file_object.totalSellTradedQty , lCurrentTickObject.buyIntensityValue , lCurrentTickObject.sellIntensityValue , \
                                                                                                              l_global_file_object.buyIntensitySum , l_global_file_object.sellIntensitySum ,\
                                                                                                          lBuyIntensityMean , lSellIntensityMean ,  lBuyIntensityVariance , lSellIntensityVariance , lCurrentTickObject.MsgCode ,\
                                                                                                          lCurrentTickObject.OrderType , lCurrentTickObject.NewP , lCurrentTickObject.NewQ ] ) )

            queueOfValuesInLastNSecs.append([lCurrentTickObject,timeOfCurrentRow])
            numberOfRowsInLastNSecs += 1   # Every append gets a +1 
            currentRowNumberForWhichFeatureValueIsBeingCalculated += 1
            continue     # Since we are going back 1 row from current we cannot get data from current row
        
        else:
            # We need to reset the timeOfOldestRow since timeElapsed has exceeded N seconds
            l_first_time_elapsed = True
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
            "BuyIntensityMean" , "SellIntensityMean" , "BuyIntensityVariance" , "SellIntensityVariance" , "MsgCode" , "Ordertype" ,"NewP","NewQ"
            ]
            
