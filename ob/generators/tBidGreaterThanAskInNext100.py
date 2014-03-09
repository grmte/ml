import os
import colNumberOfData
import dataFile
import tGenArgs
import target
import common

def extractTargetFromDataMatrix():
   """
   In the next 100 order book entries is there a case where the bidP0 is > current askP0
   """
   currentRowCount = 0

   while currentRowCount < len(dataFile.matrix)-101:
      futureRowCount = 1

      target.vector[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount])
      while(futureRowCount < 100):
         if( float(dataFile.matrix[currentRowCount+futureRowCount][colNumberOfData.BidP0]) > float(dataFile.matrix[currentRowCount][colNumberOfData.AskP0]) ):
            target.vector[currentRowCount][1] = 1
         futureRowCount = futureRowCount + 1

      currentRowCount = currentRowCount + 1
      print "Processed row number " + str(currentRowCount) 

