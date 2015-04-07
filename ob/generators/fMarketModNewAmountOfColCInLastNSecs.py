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
      colAttributeRowNo = [colNumberOfData.BestAskP, colNumberOfData.BestAskP1, colNumberOfData.BestAskP2, colNumberOfData.BestAskP3, colNumberOfData.BestAskP4] 
   else:
      colAttributeRowNo = [colNumberOfData.BestBidP, colNumberOfData.BestBidP1, colNumberOfData.BestBidP2, colNumberOfData.BestBidP3, colNumberOfData.BestBidP4]
   numberOfRowsInLastNSecs = 0
   queueOfValuesInLastNSecs = deque()
   totalOfRowsInLastNSecsX = 0.0
   totalOfRowsInLastNSecsN = 0.0
   totalOfQtyInLastNSecsX = 0.0
   totalOfQtyInLastNSecsN = 0.0   
   timeOfOldestRow = common.convertTimeStampFromStringToFloat(dataFile.matrix[0][colNumberOfTimeStamp],args.cType)
   currentRowNumberForWhichFeatureValueIsBeingCalculated = 0
   lengthOfDataMatrix = len(dataFile.matrix)
   while (currentRowNumberForWhichFeatureValueIsBeingCalculated < lengthOfDataMatrix):
      colAttributeRow = map(float, [dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][i] for i in colAttributeRowNo])
      timeOfCurrentRow = common.convertTimeStampFromStringToFloat(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfTimeStamp],args.cType)
      timeElapsed = timeOfCurrentRow - timeOfOldestRow
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
         if ( currentMsgCode =='T' and (( colNumberOfOppositeAttribute <= currentLTP ) if "bid" in args.c.lower() else (colNumberOfOppositeAttribute >= currentLTP))):
             totalOfRowsInLastNSecsX += newQty * currentLTP
             cellValueTotalX = newQty * currentLTP
             totalOfQtyInLastNSecsX += newQty
             cellValueQtyX = newQty
             cellValueTotalN = 0
             cellValueQtyN = 0
             
         elif currentMsgCode == 'M':
             totalOfRowsInLastNSecsN += (newPrice * newQty) if ( newPrice in colAttributeRow ) else 0 
             cellValueTotalN = newPrice * newQty if ( newPrice in colAttributeRow ) else 0
             totalOfQtyInLastNSecsN += newQty if ( newPrice in colAttributeRow ) else 0
             cellValueQtyN = newQty if ( newPrice in colAttributeRow ) else 0
             totalOfRowsInLastNSecsX += oldPrice * oldQty if ( oldPrice in colAttributeRow ) else 0
             cellValueTotalX = oldPrice * oldQty if ( oldPrice in colAttributeRow ) else 0
             totalOfQtyInLastNSecsX += oldQty if ( oldPrice in colAttributeRow ) else 0
             cellValueQtyX = oldQty if ( oldPrice in colAttributeRow ) else 0
         
         elif ( currentMsgCode == 'N' and ( newPrice in colAttributeRow )):
             totalOfRowsInLastNSecsN += newPrice * newQty
             cellValueTotalN = newPrice * newQty
             totalOfQtyInLastNSecsN += newQty
             cellValueQtyN = newQty
             cellValueTotalX = 0
             cellValueQtyX = 0
             
         elif ( currentMsgCode == 'X' and ( newPrice in colAttributeRow )):
             totalOfRowsInLastNSecsX += newPrice * newQty
             cellValueTotalX = newPrice * newQty
             totalOfQtyInLastNSecsX += newQty
             cellValueQtyX = newQty
             cellValueTotalN = 0
             cellValueQtyN = 0

         else:
             cellValueTotalN = 0
             cellValueQtyN = 0
             cellValueTotalX = 0
             cellValueQtyX = 0
             
         maxQty = max(totalOfQtyInLastNSecsN, totalOfQtyInLastNSecsX)
         newSide = (float(totalOfRowsInLastNSecsN + (maxQty - totalOfQtyInLastNSecsN) * colAttributeRow[4]) / maxQty) if maxQty > 0 else currentPrice
         cancelSide = (float(totalOfRowsInLastNSecsX + (maxQty - totalOfQtyInLastNSecsX) * colAttributeRow[4]) / maxQty) if maxQty > 0 else currentPrice
         attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][0] = common.convertTimeStampFromStringToDecimal(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfTimeStamp],args.cType)
         attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][1] = (float(newSide) / cancelSide) # in 1st iteration currentRowNumberForWhichFeatureValueIsBeingCalculated = 0
         attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][2] = str(currentPrice) + ";" + str(cellValueQtyN) + ";" + str(cellValueQtyX) + ";" + str(cellValueTotalN) + ";" + str(cellValueTotalX) + ";" + str(currentMsgCode) + ";" + str(timeElapsed)
         queueOfValuesInLastNSecs.append([cellValueTotalN,timeOfCurrentRow,cellValueQtyN,cellValueTotalX,cellValueQtyX])
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
               colValueInOldestElementInQueueN = oldestElementInQueue[0]
               colQtyInOldestElementInQueueN = oldestElementInQueue[2]
               colValueInOldestElementInQueueX = oldestElementInQueue[3]
               colQtyInOldestElementInQueueX = oldestElementInQueue[4]
               totalOfRowsInLastNSecsN -= colValueInOldestElementInQueueN
               totalOfQtyInLastNSecsN -= colQtyInOldestElementInQueueN
               totalOfRowsInLastNSecsX -= colValueInOldestElementInQueueX
               totalOfQtyInLastNSecsX -= colQtyInOldestElementInQueueX

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
   return [ "TimeStamp", lNameOfFeaturePrinted , args.c , "QtyForN" , "QtyForX", "AmountN" , "AmountX", "MsgCode" , "TimeElapsed"]

