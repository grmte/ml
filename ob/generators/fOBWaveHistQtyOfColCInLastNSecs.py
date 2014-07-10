import sys, dataFile, colNumberOfData, attribute, common
from collections import deque
import obwave_theta_calculation

#------------------------Declaration of global variables-------------------------------------
currentRowPriceList = []
currentRowQtyList = []
currentRowLTP = 0.0
currentRowTTQ = 0
currentRowMsgCode = ''
currentRowOrderType = ''
currentRowNewP= 0.0
currentRowNewQ = 0
currentRowOldP = 0.0
currentRowOldQ = 0
prevRowPriceList = []
prevRowQtyList = []
prevRowLTP = 0.0
prevRowTTQ = 0
prevRowMsgCode = ''
prevRowOrderType = ''
prevRowNewP= 0.0
prevRowNewQ = 0
prevRowOldP = 0.0
prevRowOldQ = 0

#++++++++++++++++++++++++++++++++Global Constant Used+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
g_weight_list = [0.2,0.2,0.2,0.2,0.2]
g_upper_cutoff_for_LHS = 2.5
g_lower_cutoff_for_LHS = 0.4
g_new_short_cutoff = 0.1
g_new_long_cutoff = 0.1
g_list_new_cutoff = [0.1, 0.1, 0.1]
g_trade_condition_upper_range_short = 4.0
g_trade_condition_upper_range_long = 2.0
g_trade_condition_lower_range_short = 0.5
g_trade_condition_lower_range_long = 0.25
new_theta = 0.8        
cancel_theta = 1.25    
trade_theta = 1.25     
mod_theta = 1.25       
g_theta_upper = 10000000000
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def create_price_list_dictionary( pBuyOrSellSide , pTickSize):
    global currentRowPriceList , currentRowQtyList , currentRowLTP , currentRowTTQ , currentRowMsgCode , currentRowOrderType , currentRowNewP , currentRowNewQ , currentRowOldP , currentRowOldQ
    global prevRowPriceList , prevRowQtyList , prevRowLTP , prevRowTTQ , prevRowMsgCode , prevRowOrderType , prevRowNewP , prevRowNewQ , prevRowOldP , prevRowOldQ
    
    lPriceDict = {}
    for index in range(5):
        lPriceDict[currentRowPriceList[index]] = currentRowQtyList[index]
    if pBuyOrSellSide == "Ask":
        startIndex = currentRowPriceList[0]
        endIndex = currentRowPriceList[4]
    else:
        startIndex = currentRowPriceList[4]
        endIndex = currentRowPriceList[0]
    price = startIndex
    while( price < endIndex ):
        if price not in lPriceDict:
            lPriceDict[price] = 0
        price += pTickSize
    return lPriceDict

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def theta_calculation_and_calculate_corresponding_qty(pBuyOrSellSide , pTickSize , pQueueOfValuesInLastNSecs , p_dict_sum_for_price,pFirstTimeWindowPrepared):
    global currentRowPriceList , currentRowQtyList , currentRowLTP , currentRowTTQ , currentRowMsgCode , currentRowOrderType , currentRowNewP , currentRowNewQ , currentRowOldP , currentRowOldQ
    global prevRowPriceList , prevRowQtyList , prevRowLTP , prevRowTTQ , prevRowMsgCode , prevRowOrderType , prevRowNewP , prevRowNewQ , prevRowOldP , prevRowOldQ
    global new_theta , cancel_theta , mod_theta , trade_theta
    if len(pQueueOfValuesInLastNSecs) == 0:
        print "Length of history is zero"
        for lPrice in currentRowPriceList:
            p_dict_sum_for_price[lPrice] = 0
        return

    for lPrice in prevRowPriceList:
        p_dict_sum_for_price[lPrice] += pQueueOfValuesInLastNSecs[-1][2][lPrice]
    
    currentLenghtOfQueue = len(pQueueOfValuesInLastNSecs)
    if ((pBuyOrSellSide == "Ask") and (currentRowMsgCode == "M" and currentRowOrderType == "S")) or ( (pBuyOrSellSide == "Bid") and (currentRowMsgCode == "M" and currentRowOrderType == "B")):
        #-----------------------------------------------MOD Cancel-------------------------------------------------------------------------------------------------------------------
        l_need_to_drag = False
        #Modify Case 1----------------------------------------------------------------------------------------------------------------------------------------------------------------
        if (currentRowOldP in prevRowPriceList and currentRowOldP not in currentRowPriceList) and (currentRowNewP in currentRowPriceList and currentRowNewP in prevRowPriceList):
            if pFirstTimeWindowPrepared == True:
                cancel_theta = obwave_theta_calculation.calculate_theta_for_mod_cancel_case1(currentLenghtOfQueue,currentRowPriceList,prevRowPriceList,currentRowQtyList,prevRowQtyList,currentRowOldP,p_dict_sum_for_price)
            l_need_to_drag = True
        #Modify Case 2---------------------------------------------------------------------------------------------------------------------------------------------------------------- 
        elif (currentRowNewP not in prevRowPriceList and currentRowNewP not in currentRowPriceList) and (currentRowOldP not in currentRowPriceList and currentRowOldP in prevRowPriceList):
            if pFirstTimeWindowPrepared == True:
                cancel_theta = obwave_theta_calculation.calculate_theta_for_mod_cancel_case2(currentLenghtOfQueue,currentRowPriceList,prevRowPriceList,currentRowQtyList,prevRowQtyList,currentRowOldP,p_dict_sum_for_price)
            l_need_to_drag = True
 
        if l_need_to_drag == True :
            l_added_mod_price = currentRowPriceList[4]
            l_added_mod_qty = currentRowQtyList[4]
            l_index_for_dictionary_traversal = currentLenghtOfQueue - 1
            while l_index_for_dictionary_traversal >= 0:
                l_dict_of_prices = pQueueOfValuesInLastNSecs[l_index_for_dictionary_traversal][2]
                l_dict_of_prices[l_added_mod_price] = cancel_theta * l_added_mod_qty
                l_index_for_dictionary_traversal -= 1
                
        #-----------------------------------------------MOD NEw-------------------------------------------------------------------------------------------------------------------------
        l_need_to_drag = False
        #Case 1----------------------------------------------------------------------------------------------------------------------------------------------------------------
        if (currentRowNewP in currentRowPriceList and currentRowNewP not in prevRowPriceList) and (currentRowOldP in currentRowPriceList and currentRowOldP in prevRowPriceList):
            if pFirstTimeWindowPrepared == True:
                new_theta = obwave_theta_calculation.calculate_theta_for_mod_new_case1(currentLenghtOfQueue,currentRowPriceList,prevRowPriceList,currentRowQtyList,prevRowQtyList,currentRowNewQ,currentRowNewP,p_dict_sum_for_price)
            l_need_to_drag = True
         
        #Case 2----------------------------------------------------------------------------------------------------------------------------------------------------------------   
        elif (currentRowOldP not in prevRowPriceList) and (currentRowNewP in currentRowPriceList and currentRowNewP not in prevRowPriceList) :
            if pFirstTimeWindowPrepared == True:
                new_theta = obwave_theta_calculation.calculate_theta_for_mod_new_case2(currentLenghtOfQueue,currentRowPriceList,prevRowPriceList,currentRowQtyList,prevRowQtyList,currentRowNewQ,currentRowNewP,p_dict_sum_for_price)
            l_need_to_drag = True
            
        #Case 3----------------------------------------------------------------------------------------------------------------------------------------------------------------
        elif (currentRowOldP in prevRowPriceList and currentRowOldP not in currentRowPriceList) and (currentRowNewP in currentRowPriceList and currentRowNewP not in prevRowPriceList):
            if pFirstTimeWindowPrepared == True:
                new_theta = obwave_theta_calculation.calculate_theta_for_mod_new_case3(currentLenghtOfQueue,currentRowPriceList,prevRowPriceList,currentRowQtyList,prevRowQtyList,currentRowNewQ,currentRowNewP,currentRowOldQ,currentRowOldP,p_dict_sum_for_price)
            l_need_to_drag = True
        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        if l_need_to_drag == True:
            l_index_for_dictionary_traversal = currentLenghtOfQueue - 1
            while l_index_for_dictionary_traversal >= 0:
                l_dict_of_prices = pQueueOfValuesInLastNSecs[l_index_for_dictionary_traversal][2]
                l_dict_of_prices[currentRowNewP] = new_theta * currentRowNewQ
                l_index_for_dictionary_traversal -= 1
                            
    if ((pBuyOrSellSide == "Ask") and (currentRowMsgCode == "X" and currentRowOrderType == "S")) or ( (pBuyOrSellSide == "Bid") and (currentRowMsgCode == "X" and currentRowOrderType == "B")):     
        l_cancel_price = currentRowNewP
        l_cancel_qty = currentRowNewQ
        if l_cancel_price in prevRowPriceList:
            if l_cancel_qty == prevRowQtyList[prevRowPriceList.index(l_cancel_price)]:
                if pFirstTimeWindowPrepared == True:
                    cancel_theta = obwave_theta_calculation.calculate_theta_for_price_cancel(currentLenghtOfQueue,currentRowPriceList,prevRowPriceList,currentRowQtyList,prevRowQtyList,currentRowNewP,p_dict_sum_for_price)        
                l_index_for_dictionary_traversal = currentLenghtOfQueue - 1
                while l_index_for_dictionary_traversal >= 0:
                    l_dict_of_prices = pQueueOfValuesInLastNSecs[l_index_for_dictionary_traversal][2]
                    l_dict_of_prices[currentRowPriceList[4]] = cancel_theta * currentRowQtyList[4]
                    l_index_for_dictionary_traversal -= 1
        
    if currentRowMsgCode == "T":
        if  currentRowNewP in prevRowPriceList:
            l_traded_price = currentRowNewP
            l_traded_qty = currentRowNewQ
            
            if l_traded_qty == prevRowQtyList[prevRowPriceList.index(l_traded_price)]:
                if pFirstTimeWindowPrepared == True:
                    trade_theta = obwave_theta_calculation.calculate_theta_for_trade(currentLenghtOfQueue,currentRowPriceList,prevRowPriceList,currentRowQtyList,prevRowQtyList,l_traded_price,p_dict_sum_for_price)
                l_index_for_dictionary_traversal = currentLenghtOfQueue - 1
                while l_index_for_dictionary_traversal >= 0:
                    l_dict_of_prices = pQueueOfValuesInLastNSecs[l_index_for_dictionary_traversal][2]
                    l_dict_of_prices[currentRowPriceList[4]] = trade_theta * currentRowQtyList[4]
                    l_index_for_dictionary_traversal -= 1        

    if ((pBuyOrSellSide == "Ask") and (currentRowMsgCode == "N" and currentRowOrderType == "S")) or ( (pBuyOrSellSide == "Bid") and (currentRowMsgCode == "N" and currentRowOrderType == "B")):  
        if currentRowNewP not in prevRowPriceList :
            if pFirstTimeWindowPrepared == True:
                new_theta = obwave_theta_calculation.calculate_theta_for_new(currentLenghtOfQueue,currentRowPriceList,prevRowPriceList,currentRowQtyList,prevRowQtyList,currentRowNewQ,currentRowNewP,p_dict_sum_for_price) 
            l_index_for_dictionary_traversal = currentLenghtOfQueue - 1
            while l_index_for_dictionary_traversal >= 0:
                l_dict_of_prices = pQueueOfValuesInLastNSecs[l_index_for_dictionary_traversal][2]
                l_dict_of_prices[currentRowNewP] = new_theta * currentRowNewQ
                l_index_for_dictionary_traversal -= 1 
    
    for lPrice in currentRowPriceList:
        if lPrice not in prevRowPriceList:
           p_dict_sum_for_price[lPrice] = currentLenghtOfQueue * pQueueOfValuesInLastNSecs[-1][2][lPrice]
    for lPrevPrice in prevRowPriceList:
        if lPrevPrice != 0 and lPrevPrice not in currentRowPriceList:
            del p_dict_sum_for_price[lPrevPrice]
    return
    
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                    
def extractAttributeFromDataMatrix(args):
   global currentRowPriceList , currentRowQtyList , currentRowLTP , currentRowTTQ , currentRowMsgCode , currentRowOrderType , currentRowNewP , currentRowNewQ , currentRowOldP , currentRowOldQ
   global prevRowPriceList , prevRowQtyList , prevRowLTP , prevRowTTQ , prevRowMsgCode , prevRowOrderType , prevRowNewP , prevRowNewQ , prevRowOldP , prevRowOldQ
   global new_theta , cancel_theta , mod_theta , trade_theta
   if args.n == None:
      N = 5
   else:
      N = int(args.n) 
   try:
      args.c
   except:
      print "Since -c has not been specified I cannot proceed"
      os._exit()
   colNumberOfPrice = eval("colNumberOfData."+ args.c + "P0" )
   colNumberOfQty = eval("colNumberOfData."+ args.c + "Q0")
   colNumberOfTimeStamp = colNumberOfData.TimeStamp
   lFirstTimeWindowPrepared = False 
   tickSize = int(args.tickSize)
   numberOfRowsInLastNSecs = 0
   queueOfValuesInLastNSecs = deque()
   dict_sum_for_price = {}
   timeOfOldestRow = common.convertTimeStampFromStringToFloat(dataFile.matrix[0][colNumberOfTimeStamp],args.cType)
   currentRowNumberForWhichFeatureValueIsBeingCalculated = 0
   lengthOfDataMatrix = len(dataFile.matrix)
   while (currentRowNumberForWhichFeatureValueIsBeingCalculated < lengthOfDataMatrix):
      timeOfCurrentRow = common.convertTimeStampFromStringToFloat(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfTimeStamp],args.cType)
      timeElapsed = timeOfCurrentRow - timeOfOldestRow
      dataFileCurrentRow = dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated]
      currentRowPriceList = [ float(dataFileCurrentRow[colNumberOfPrice]) , float(dataFileCurrentRow[colNumberOfPrice+2]) , float(dataFileCurrentRow[colNumberOfPrice + 4]) , float(dataFileCurrentRow[colNumberOfPrice + 6]) , float(dataFileCurrentRow[colNumberOfPrice + 8]) ]
      currentRowQtyList = [int(dataFileCurrentRow[colNumberOfQty]),int(dataFileCurrentRow[colNumberOfQty + 2]),int(dataFileCurrentRow[colNumberOfQty + 4]),int(dataFileCurrentRow[colNumberOfQty + 6]),int(dataFileCurrentRow[colNumberOfQty + 8])]
      currentRowLTP = float(dataFileCurrentRow[colNumberOfData.LTP])
      currentRowTTQ = float(dataFileCurrentRow[colNumberOfData.TTQ])
      currentRowMsgCode = dataFileCurrentRow[colNumberOfData.MsgCode]
      currentRowOrderType = dataFileCurrentRow[colNumberOfData.OrderType]
      currentRowNewP = float(dataFileCurrentRow[colNumberOfData.NewP])
      currentRowNewQ = int(dataFileCurrentRow[colNumberOfData.NewQ])
      if currentRowMsgCode == 'M':
          currentRowOldP = float(dataFileCurrentRow[colNumberOfData.OldP])
          currentRowOldQ = int(dataFileCurrentRow[colNumberOfData.OldQ])
      if (timeElapsed < N):
         theta_calculation_and_calculate_corresponding_qty(args.c,tickSize,queueOfValuesInLastNSecs,dict_sum_for_price,lFirstTimeWindowPrepared)
         priceDictionary = create_price_list_dictionary(args.c,tickSize)
         cellValue = (g_weight_list[0]*dict_sum_for_price[currentRowPriceList[0]]) + (g_weight_list[1]*dict_sum_for_price[currentRowPriceList[1]]) + (g_weight_list[2]*dict_sum_for_price[currentRowPriceList[2]]) + \
                     (g_weight_list[3]*dict_sum_for_price[currentRowPriceList[3]]) +  (g_weight_list[4]*dict_sum_for_price[currentRowPriceList[4]])
         attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][0] = common.convertTimeStampFromStringToDecimal(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfTimeStamp],args.cType)
         attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][1] = cellValue/(numberOfRowsInLastNSecs+1) # in 1st iteration currentRowNumberForWhichFeatureValueIsBeingCalculated = 0
         attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][2] = str(cellValue) + ";" + str(numberOfRowsInLastNSecs) + ";" + str(timeElapsed) + ";" + str(dict_sum_for_price[currentRowPriceList[0]]+currentRowQtyList[0]) +\
                                                                                        ";" + str(dict_sum_for_price[currentRowPriceList[1]]+currentRowQtyList[1]) + ";" + str(dict_sum_for_price[currentRowPriceList[2]]+currentRowQtyList[2]) +\
                                                                                        ";" + str(dict_sum_for_price[currentRowPriceList[3]]+currentRowQtyList[3]) +\
                                                                                        ";" + str(dict_sum_for_price[currentRowPriceList[4]]+currentRowQtyList[4]) + ";" + str(new_theta) + ";" + str(cancel_theta) +\
                                                                                        ";" + str(trade_theta)
                                                                                        #new_theta , cancel_theta , mod_theta , trade_theta
         queueOfValuesInLastNSecs.append([cellValue,timeOfCurrentRow,priceDictionary])
         numberOfRowsInLastNSecs += 1   # Every append gets a +1 
         currentRowNumberForWhichFeatureValueIsBeingCalculated += 1
         prevRowPriceList = currentRowPriceList
         prevRowQtyList = currentRowQtyList
         prevRowLTP  = currentRowLTP
         prevRowTTQ =  currentRowTTQ
         prevRowMsgCode = currentRowMsgCode
         prevRowOrderType = currentRowOrderType
         prevRowNewP = currentRowNewP
         prevRowNewQ = currentRowNewQ
         if prevRowOrderType == 'M':
             prevRowOldP = currentRowOldP
             prevRowOldQ = currentRowOldQ
         continue     # Since we are going back 1 row from current we cannot get data from current row
      else:
         # We need to reset the timeOfOldestRow since timeElapsed has exceeded N seconds
         while(timeElapsed >= N):
            lFirstTimeWindowPrepared = True 
            if(len(queueOfValuesInLastNSecs) == 0):
               timeOfOldestRow = timeOfCurrentRow
               timeElapsed = 0
               if(numberOfRowsInLastNSecs != 0):
                  print "Sanity check: This condition is not possible logically. numberOfRowsInLastNSecs should been 0. There has been an unknown error"
                  sys.exit(-1)
            else:   
               oldestElementInQueue = queueOfValuesInLastNSecs.popleft()
               colDictInOldestElementInQueue = oldestElementInQueue[2]
               if len(queueOfValuesInLastNSecs) == 0:
                    timeElapsed = 0
                    timeOfOldestRow = timeOfCurrentRow
               else:
                    timeOfOldestRow = queueOfValuesInLastNSecs[0][1]
               numberOfRowsInLastNSecs -= 1 # every pop from the queue gets a -1
               timeElapsed = timeOfCurrentRow - timeOfOldestRow

               oldestPricesList = colDictInOldestElementInQueue.keys()
               for lPrice in oldestPricesList:
                    try:
                        dict_sum_for_price[lPrice] -= colDictInOldestElementInQueue[lPrice]
                    except:
                        pass

               if(len(queueOfValuesInLastNSecs) != numberOfRowsInLastNSecs):
                  print "Sanity check: This condition is not possible logically. There has been an unknown error"
                  sys.exit(-1)

      print "Processed row number " + str(currentRowNumberForWhichFeatureValueIsBeingCalculated)
   
   lNameOfFeaturePrinted = "fOBWaveHistQtyOf" + args.c + "InLast" + str(args.n) + "Secs"
   return [ "TimeStamp", lNameOfFeaturePrinted , "TotalOfRowsInLastNSecs" , "NumberOfRowsInLastNSecs" , "TimeElapsed","HP0","HP1","HP2","HP3","HP4","NewTheta","CancelTheta","TradeTheta"]

