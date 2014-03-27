import os
import colNumberOfData
import dataFile
import aGenArgs
import attribute
import common
from collections import deque

def extractAttributeFromDataMatrix():
   queueOfValueInFutureNSecs = deque()
   totalOfRowsInFutureNSeconds = 0.0
   if aGenArgs.args.n is None:
      print "N has not been specified"
      os._exit(-1)
   try:
      aGenArgs.args.c
   except:
      print "C has not been specified"
      os._exit(-1)
   numberOfSecondsInFuture = int(aGenArgs.args.n)
   currentRowCount = 0
   for dataRow in dataFile.matrix:
      timeOfCurrentRow = common.getTimeStamp(dataFile.matrix[currentRowCount])
      attribute.list[currentRowCount][0] = timeOfCurrentRow
      futureRowCount = 1  
      totalOfRowsInFutureNSeconds = 0
      while True:
         if(currentRowCount + futureRowCount >= len(dataFile.matrix)):
            timeOfFutureRow = common.getTimeStamp(dataFile.matrix[currentRowCount + futureRowCount])
            if(timeOfFutureRow - timeOfCurrentRow < numberOfSecondsInFuture):
               codeString = 'float(dataFile.matrix[currentRowCount + futureRowCount][colNumberOfData.'+aGenArgs.args.c+'])'
               cellValue = eval(codeString)
               cellTimeStamp = common.getTimeStamp(dataFile.matrix[currentRowCount + futureRowCount])
               queueOfValueInFutureNSecs.append([cellValue,cellTimeStamp])
               totalOfRowsInFutureNSeconds += cellValue
               futureRowCount = futureRowCount + 1
            else:
               break
         else:
            break
      averageOfFutureRows = totalOfRowsInFutureNSeconds / futureRowCount
      if( averageOfFutureRows > float(dataFile.matrix[currentRowCount][colNumberOfData.LTP])):   
         attribute.list[currentRowCount][1] = 1
      else:
         attribute.list[currentRowCount][1] = 0

      attribute.list[currentRowCount][2] = totalOfRowsInFutureNSeconds
      attribute.list[currentRowCount][3] = float(dataFile.matrix[currentRowCount][colNumberOfData.LTP])

      currentRowCount = currentRowCount + 1

      if(currentRowCount % 1000 == 0):
         print "Processed row number " + str(currentRowCount) 

