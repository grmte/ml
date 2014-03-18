import os
import colNumberOfData
import dataFile
import tGenArgs
import target
import common
from collections import deque

def extractTargetFromDataMatrix():
   queueOfCellValueInFutureNRows = deque()
   totalOfFutureNRows = 0.0
   numberOfFutureRows = int(tGenArgs.args.n)
   """ lets get the total of futureNrows"""
   futureRowCount = 0   
   while(futureRowCount < numberOfFutureRows):
      cellValue = float(dataFile.matrix[futureRowCount][colNumberOfData.LTP])
      queueOfCellValueInFutureNRows.append(cellValue)
      totalOfFutureNRows += cellValue
      futureRowCount = futureRowCount + 1


   currentRowCount = 0


   for dataRow in dataFile.matrix:

      target.vector[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount])
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
         target.vector[currentRowCount][1] = 1
      else:
         target.vector[currentRowCount][1] = 0

      target.vector[currentRowCount][2] = totalOfFutureNRows
      target.vector[currentRowCount][3] = float(dataFile.matrix[currentRowCount][colNumberOfData.LTP])

      currentRowCount = currentRowCount + 1
      if(currentRowCount % 1000 == 0):
         print "Processed row number " + str(currentRowCount) 

