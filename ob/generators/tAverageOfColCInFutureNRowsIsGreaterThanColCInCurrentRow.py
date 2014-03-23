import os
import colNumberOfData
import dataFile
import aGenArgs
import attribute
import common
from collections import deque

def extractAttributeFromDataMatrix():
   queueOfCellValueInFutureNRows = deque()
   totalOfFutureNRows = 0.0
   if aGenArgs.args.n is None:
      print "N has not been specified"
      os._exit(-1)
   numberOfFutureRows = int(aGenArgs.args.n)
   """ lets get the total of futureNrows"""
   futureRowCount = 0   
   while(futureRowCount < numberOfFutureRows):
      cellValue = float(dataFile.matrix[futureRowCount][colNumberOfData.LTP])
      queueOfCellValueInFutureNRows.append(cellValue)
      totalOfFutureNRows += cellValue
      futureRowCount = futureRowCount + 1


   currentRowCount = 0


   for dataRow in dataFile.matrix:

      attribute.list[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount])
      futureCellValue = 0

      if(currentRowCount + numberOfFutureRows < len(dataFile.matrix)):
         futureCellValue = float(dataFile.matrix[currentRowCount+numberOfFutureRows][colNumberOfData.LTP])
         queueOfCellValueInFutureNRows.append(futureCellValue)
         divisor = numberOfFutureRows
      else:
         divisor = len(dataFile.matrix) - currentRowCount

      totalOfFutureNRows += futureCellValue
      totalOfFutureNRows -= queueOfCellValueInFutureNRows.popleft()
  
      averageOfFutureRows = totalOfFutureNRows / float(divisor)

      if( averageOfFutureRows > float(dataFile.matrix[currentRowCount][colNumberOfData.LTP])):   
         attribute.list[currentRowCount][1] = 1
      else:
         attribute.list[currentRowCount][1] = 0

      attribute.list[currentRowCount][2] = totalOfFutureNRows
      attribute.list[currentRowCount][3] = float(dataFile.matrix[currentRowCount][colNumberOfData.LTP])

      currentRowCount = currentRowCount + 1
      if(currentRowCount % 1000 == 0):
         print "Processed row number " + str(currentRowCount) 

