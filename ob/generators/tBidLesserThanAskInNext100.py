import os
import colNumberOfData
import dataFile

import attribute
import common

def extractAttributeFromDataMatrix(args):
   """
   In the next 100 order book entries is there a case where the bidP0 is > current askP0
   """
   currentRowCount = 0

   while currentRowCount < len(dataFile.matrix)-101:
      futureRowCount = 1

      attribute.aList[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount],colNumberOfData.TimeStamp)
      while(futureRowCount < 100):
         if( float(dataFile.matrix[currentRowCount+futureRowCount][colNumberOfData.BidP0]) < float(dataFile.matrix[currentRowCount][colNumberOfData.AskP0]) ):
            attribute.aList[currentRowCount][1] = 1
         futureRowCount = futureRowCount + 1

      currentRowCount = currentRowCount + 1
      if(currentRowCount % 1000 == 0):
         print "Processed row number " + str(currentRowCount) 

   lNameOfTarget = "tBidLesserThanAskNext" + args.n
   return ["TimeStamp",lNameOfTarget,"Zero1","Zero2"]
