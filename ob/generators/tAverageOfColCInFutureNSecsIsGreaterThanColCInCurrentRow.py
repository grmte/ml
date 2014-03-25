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
   numberOfSecondsInFuture = int(aGenArgs.args.n)
   """ lets get the total of futureNrows"""
   futureRowCount = 0   
   currentRowCount = 0   
   while(common.getTimeStamp(dataFile.matrix[futureRowCount]) - common.getTimeStamp(dataFile.matrix[currentRowCount])< numberOfSecondsInFuture):
      cellValue = float(dataFile.matrix[futureRowCount][colNumberOfData.LTP])
      queueOfValueInFutureNSecs.append(cellValue)
      totalOfRowsInFutureNSeconds += cellValue
      futureRowCount = futureRowCount + 1


   currentRowCount = 0


   for dataRow in dataFile.matrix:

      attribute.list[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount])
      futureCellValue = 0

      if(currentRowCount + numberOfSecondsInFuture < len(dataFile.matrix)):
         futureCellValue = float(dataFile.matrix[currentRowCount+numberOfSecondsInFuture][colNumberOfData.LTP])
         queueOfValueInFutureNSecs.append(futureCellValue)
         divisor = numberOfSecondsInFuture
      else:
         divisor = len(dataFile.matrix) - currentRowCount

      totalOfRowsInFutureNSeconds += futureCellValue
      totalOfRowsInFutureNSeconds -= queueOfValueInFutureNSecs.popleft()
  
      averageOfFutureRows = totalOfRowsInFutureNSeconds / float(divisor)

      if( averageOfFutureRows > float(dataFile.matrix[currentRowCount][colNumberOfData.LTP])):   
         attribute.list[currentRowCount][1] = 1
      else:
         attribute.list[currentRowCount][1] = 0

      attribute.list[currentRowCount][2] = totalOfRowsInFutureNSeconds
      attribute.list[currentRowCount][3] = float(dataFile.matrix[currentRowCount][colNumberOfData.LTP])

      currentRowCount = currentRowCount + 1
      if(currentRowCount % 1000 == 0):
         print "Processed row number " + str(currentRowCount) 

