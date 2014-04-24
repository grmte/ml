import sys, dataFile, colNumberOfData, attribute, common
from collections import deque
from math import exp

def extractAttributeFromDataMatrix(args):
   if args.n == None:
      N = 5
   else:
      N = int(args.n) 

   try:
      args.c
   except:
      print "Since -c has not been specified I cannot proceed"
      os._exit()
      
   colNumberOfTimeStamp = colNumberOfData.TimeStamp

   numberOfRowsInLastNSecs = 0
   queueOfValuesInLastNSecs = deque()
   totalOfRowsInLastNSecs = 0.0
   timeOfOldestRow = common.convertTimeStampFromStringToFloat(dataFile.matrix[0][colNumberOfTimeStamp])
   currentRowNumberForWhichFeatureValueIsBeingCalculated = 0
   lengthOfDataMatrix = len(dataFile.matrix)
   while (currentRowNumberForWhichFeatureValueIsBeingCalculated < lengthOfDataMatrix):
      if currentRowNumberForWhichFeatureValueIsBeingCalculated != 0:
          lPreviousDataRow = dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated - 1]
      lCurrentDataRow = dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated]
      lPreviousRowData = dataFile.matrix[ currentRowNumberForWhichFeatureValueIsBeingCalculated - 1 ]
      timeOfCurrentRow = common.convertTimeStampFromStringToFloat(lCurrentDataRow[colNumberOfTimeStamp],args.cType)
      timeElapsed = timeOfCurrentRow - timeOfOldestRow
      if (timeElapsed < N):
         lMsgCode = lCurrentDataRow[colNumberOfData.MsgCode]
         lOrderType = lCurrentDataRow[colNumberOfData.OrderType]
         lNewPrice = float(lCurrentDataRow[colNumberOfData.NewP])
         lNewQty = int(lCurrentDataRow[colNumberOfData.NewQ])
         if lMsgCode == "M":
             lOldPrice = float(lCurrentDataRow[colNumberOfData.OldP])
             lOldQty = int(lCurrentDataRow[colNumberOfData.OldQ])
         if args.c.lower() == "ask" :
             lColCQtyList = [ lCurrentDataRow[colNumberOfData.AskQ0] , lCurrentDataRow[colNumberOfData.AskQ1] , lCurrentDataRow[colNumberOfData.AskQ2] , lCurrentDataRow[colNumberOfData.AskQ3] , lCurrentDataRow[colNumberOfData.AskQ4] ]
         else:
             lColCQtyList = [ lCurrentDataRow[colNumberOfData.BidQ0] , lCurrentDataRow[colNumberOfData.BidQ1] , lCurrentDataRow[colNumberOfData.BidQ2] , lCurrentDataRow[colNumberOfData.BidQ3] , lCurrentDataRow[colNumberOfData.BidQ4] ]        
         lColCPrevPriceList = []
         lColCPriceList = []
         if args.c.lower() == "ask" :
             lColCPriceList = [ lCurrentDataRow[colNumberOfData.AskP0] , lCurrentDataRow[colNumberOfData.AskP1] , lCurrentDataRow[colNumberOfData.AskP2] , lCurrentDataRow[colNumberOfData.AskP3] , lCurrentDataRow[colNumberOfData.AskP4] ]
             if currentRowNumberForWhichFeatureValueIsBeingCalculated != 0:
                 lColCPrevPriceList = [lPreviousDataRow[colNumberOfData.AskP0],lPreviousDataRow[colNumberOfData.AskP1],lPreviousDataRow[colNumberOfData.AskP2],lPreviousDataRow[colNumberOfData.AskP3],lPreviousDataRow[colNumberOfData.AskP4]]
         else:
             lColCPriceList = [ lCurrentDataRow[colNumberOfData.BidP0] , lCurrentDataRow[colNumberOfData.BidP1] , lCurrentDataRow[colNumberOfData.BidP2] , lCurrentDataRow[colNumberOfData.BidP3] , lCurrentDataRow[colNumberOfData.BidP4] ]
             if currentRowNumberForWhichFeatureValueIsBeingCalculated != 0:
                 lColCPrevPriceList = [lPreviousDataRow[colNumberOfData.BidP0],lPreviousDataRow[colNumberOfData.BidP1],lPreviousDataRow[colNumberOfData.BidP2],lPreviousDataRow[colNumberOfData.BidP3],lPreviousDataRow[colNumberOfData.BidP4]]

         cellValue = 0
         if (lMsgCode == "N" and args.c.lower() == "ask" and lOrderType == "S") or (lMsgCode == "N" and args.c.lower() == "bid" and lOrderType == "B"):
             cellValue = lNewQty
         elif (lMsgCode == "X" and args.c.lower() == "ask" and lOrderType == "S") or (lMsgCode == "X" and args.c.lower() == "bid" and lOrderType == "B"):
             cellValue = -1 * lNewQty
         elif (lMsgCode == "M" and args.c.lower() == "ask" and lOrderType == "S") or (lMsgCode == "M" and args.c.lower() == "bid" and lOrderType == "B"):
             if len(lColCPrevPriceList) == 0:
                cellValue = lNewQty
            #Case 1------------------------------------------------------------------------------------------------------------ 
             if (lNewPrice in lColCPriceList) and (lOldPrice not in lColCPrevPriceList) :
                cellValue = lNewQty
            #Case 2------------------------------------------------------------------------------------------------------------
             elif (lNewPrice not in lColCPriceList) and (lOldPrice in lColCPrevPriceList):
                cellValue = -1 * lOldQty 
             else:
                cellValue =  lNewQty - lOldQty
         elif (len(lColCPrevPriceList) != 0) and (lMsgCode == "T" and lNewPrice==lColCPrevPriceList[0]):
                cellValue = -1 * lNewQty
         totalOfRowsInLastNSecs = totalOfRowsInLastNSecs + cellValue
         attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][0] = common.convertTimeStampFromStringToDecimal(lCurrentDataRow[colNumberOfTimeStamp])
         attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][1] = exp(totalOfRowsInLastNSecs/(numberOfRowsInLastNSecs+1)) # in 1st iteration currentRowNumberForWhichFeatureValueIsBeingCalculated = 0
         attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][2] = str(totalOfRowsInLastNSecs/(numberOfRowsInLastNSecs+1))+ ";"+ str(totalOfRowsInLastNSecs) + ";" + str(numberOfRowsInLastNSecs) + ";" + str(timeElapsed)
         queueOfValuesInLastNSecs.append([cellValue,timeOfCurrentRow])
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
               if(totalOfRowsInLastNSecs != 0):
                  print "Sanity check: This condition is not possible logically. totalOfRowsInLastNSecs should have been 0. There has been an unknown error"
                  sys.exit(-1)   
            else:   
               oldestElementInQueue = queueOfValuesInLastNSecs.popleft()
               colValueInOldestElementInQueue = oldestElementInQueue[0]
               colTimeStampInOldestElementInQueue = oldestElementInQueue[1]
               totalOfRowsInLastNSecs -= colValueInOldestElementInQueue
               timeOfOldestRow = colTimeStampInOldestElementInQueue
               numberOfRowsInLastNSecs -= 1 # every pop from the queue gets a -1
               timeElapsed = timeOfCurrentRow - timeOfOldestRow
               if(len(queueOfValuesInLastNSecs) != numberOfRowsInLastNSecs):
                  print "Sanity check: This condition is not possible logically. There has been an unknown error"
                  sys.exit(-1)
 
      print "Processed row number " + str(currentRowNumberForWhichFeatureValueIsBeingCalculated)
   
   lNameOfFeaturePrinted = "fEMovAvgOfMsgQtyOverCol" + args.c + "InLast" + str(args.n) + "Secs"
   return [ "TimeStamp", lNameOfFeaturePrinted , "AvgOverLastNSec","TotalOfRowsInLastNSecs" , "NumberOfRowsInLastNSecs" , "TimeElapsed"]

