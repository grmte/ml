import sys, os, dataFile, colNumberOfData, attribute, common
from collections import deque

def extractAttributeFromDataMatrix(args):
   if args.n == None:
      N = 5
   else:
      N = int(args.n) 
   try:
      #Value of argument c can be taken as BidP0 and AskP0 
      args.c
   except:
      print "Since -c has not been specified I cannot proceed"
      os._exit()
   colNumberOfAttribute = eval("colNumberOfData."+ args.c )
   colNumberOfOppositeAttribute = eval("colNumberOfData.BestBidP") if "ask" in args.c else eval("colNumberOfData.BestAskP")
   colNumberOfTimeStamp = colNumberOfData.TimeStamp
   if "ask" in args.c.lower():
      colAttributeRowNo = [colNumberOfData.BestAskP, colNumberOfData.BestAskP1]#, colNumberOfData.BestAskP2, colNumberOfData.BestAskP3, colNumberOfData.BestAskP4] 
   else:
      colAttributeRowNo = [colNumberOfData.BestBidP, colNumberOfData.BestBidP1]#, colNumberOfData.BestBidP2, colNumberOfData.BestBidP3, colNumberOfData.BestBidP4]
   numberOfRowsInLastNSecs = 0
   queueOfValuesInLastNSecs = deque()
   totalOfRowsInLastNSecs = 0.0
   totalOfRowsInLastNSecs = 0.0
   totalOfQtyInLastNSecs = 0.0
   timeOfOldestRow = common.convertTimeStampFromStringToFloat(dataFile.matrix[0][colNumberOfTimeStamp],args.cType)
   currentRowNumberForWhichFeatureValueIsBeingCalculated = 0
   lengthOfDataMatrix = len(dataFile.matrix)
   while (currentRowNumberForWhichFeatureValueIsBeingCalculated < lengthOfDataMatrix):
      colAttributeRow = map(float, [dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][i] for i in colAttributeRowNo])
      timeOfCurrentRow = common.convertTimeStampFromStringToFloat(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfTimeStamp],args.cType)
      timeElapsed = timeOfCurrentRow - timeOfOldestRow
      oppositeAttribute = float(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfOppositeAttribute])
      if (timeElapsed < N):
         if  currentRowNumberForWhichFeatureValueIsBeingCalculated != 0:
             previousRowPrice = float(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated - 1][colNumberOfAttribute])
         else:
             previousRowPrice = 0
         currentPrice = float(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfAttribute])
         currentLTP = float(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfData.LTP])
         currentMsgCode = dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfData.MsgCode]
         newQty = int(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfData.NewQ])
         newPrice = int(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfData.NewP])
         oldQty = int(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfData.OldQ])
         oldPrice = int(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfData.OldP])
         if ( currentMsgCode =='T' and (( oppositeAttribute <= currentLTP ) if "bid" in args.c.lower() else (oppositeAttribute >= currentLTP))):
             totalOfRowsInLastNSecs += newQty * currentLTP
             cellValueTotal = newQty * currentLTP
             totalOfQtyInLastNSecs += newQty
             cellValueQty = newQty
         if ( currentMsgCode == 'M' and ( newPrice in colAttributeRow ) and ((newPrice > oldPrice) if "bid" in args.c.lower() else (newPrice < oldPrice))):
             totalOfRowsInLastNSecs += newPrice * newQty
             cellValueTotal = newPrice * newQty
             totalOfQtyInLastNSecs += newQty
             cellValueQty = newQty
         elif ( currentMsgCode == 'N' and ( newPrice in colAttributeRow )):
             totalOfRowsInLastNSecs += newPrice * newQty
             cellValueTotal = newPrice * newQty
             totalOfQtyInLastNSecs += newQty
             cellValueQty = newQty
         else:
             cellValueTotal = 0
             cellValueQty = 0
         attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][0] = common.convertTimeStampFromStringToDecimal(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfTimeStamp],args.cType)
         attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][1] = (float(totalOfRowsInLastNSecs) / totalOfQtyInLastNSecs) if totalOfQtyInLastNSecs > 0 else currentPrice # in 1st iteration currentRowNumberForWhichFeatureValueIsBeingCalculated = 0
         attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][2] = str(currentPrice) + ";" + str(currentLTP) + ";" + str(cellValueTotal) + ";" + str(currentMsgCode) + ";" + str(timeElapsed)
         queueOfValuesInLastNSecs.append([cellValueTotal,timeOfCurrentRow,cellValueQty])
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
               colQtyInOldestElementInQueue = oldestElementInQueue[2]
               totalOfRowsInLastNSecs -= colValueInOldestElementInQueue
               totalOfQtyInLastNSecs -= colQtyInOldestElementInQueue
               if len(queueOfValuesInLastNSecs) == 0:
                    timeElapsed = 0
                    timeOfOldestRow = timeOfCurrentRow
               else:
                    timeOfOldestRow = queueOfValuesInLastNSecs[0][1]
               numberOfRowsInLastNSecs -= 1 # every pop from the queue gets a -1
               timeElapsed = timeOfCurrentRow - timeOfOldestRow
               if(len(queueOfValuesInLastNSecs) != numberOfRowsInLastNSecs):
                  print "Sanity check: This condition is not possible logically. There has been an unknown error"
                  sys.exit(-1)
 
      print "Processed row number " + str(currentRowNumberForWhichFeatureValueIsBeingCalculated)
   
   lNameOfFeaturePrinted = "fMarketTradedQtySumOfCol" + args.c + "InLast" + str(args.n) + "Secs"
   return [ "TimeStamp", lNameOfFeaturePrinted , args.c , "LTP" , "TradedQtyWhichIs="+ args.c , "MsgCode" , "TimeElapsed"]

