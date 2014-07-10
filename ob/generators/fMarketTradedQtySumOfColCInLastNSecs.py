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
   colNumberOfTimeStamp = colNumberOfData.TimeStamp

   numberOfRowsInLastNSecs = 0
   queueOfValuesInLastNSecs = deque()
   totalOfRowsInLastNSecs = 0.0
   timeOfOldestRow = common.convertTimeStampFromStringToFloat(dataFile.matrix[0][colNumberOfTimeStamp],args.cType)
   currentRowNumberForWhichFeatureValueIsBeingCalculated = 0
   lengthOfDataMatrix = len(dataFile.matrix)
   while (currentRowNumberForWhichFeatureValueIsBeingCalculated < lengthOfDataMatrix):
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
         currentLTQ = int(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfData.NewQ])
         if ( currentMsgCode =='T' and  ( previousRowPrice == currentLTP ) ):
             totalOfRowsInLastNSecs += currentLTQ
             cellValue = currentLTQ
         else:
             cellValue = 0
         attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][0] = common.convertTimeStampFromStringToDecimal(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfTimeStamp],args.cType)
         attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][1] = totalOfRowsInLastNSecs # in 1st iteration currentRowNumberForWhichFeatureValueIsBeingCalculated = 0
         attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][2] = str(currentPrice) + ";" + str(currentLTP) + ";" + str(cellValue) + ";" + str(currentMsgCode) + ";" + str(timeElapsed)
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
               totalOfRowsInLastNSecs -= colValueInOldestElementInQueue
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

