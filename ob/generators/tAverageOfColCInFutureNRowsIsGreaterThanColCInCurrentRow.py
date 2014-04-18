import os
import colNumberOfData
import dataFile

import attribute
import common
from collections import deque

def extractAttributeFromDataMatrix(args):
   queueOfCellValueInFutureNRows = deque()
   totalOfFutureNRows = 0.0
   if args.n is None:
      print "-n has not been specified"
      os._exit(-1)
   numberOfFutureRows = int(args.n)

   try:
      args.c 
   except:   
      print "-c has not been specified"
      os._exit(-1)
   
   """ lets get the total of futureNrows"""
   futureRowCount = 0   
   while(futureRowCount < numberOfFutureRows):
      codeString = 'float(dataFile.matrix[futureRowCount][colNumberOfData.'+args.c+'])' 
      cellValue = eval(codeString)
      queueOfCellValueInFutureNRows.append(cellValue)
      totalOfFutureNRows += cellValue
      futureRowCount = futureRowCount + 1


   currentRowCount = 0


   for dataRow in dataFile.matrix:

      attribute.aList[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount],colNumberOfData.TimeStamp)
      futureCellValue = 0

      if(currentRowCount + numberOfFutureRows < len(dataFile.matrix)):
         codeString = 'float(dataFile.matrix[currentRowCount+numberOfFutureRows][colNumberOfData.'+args.c+'])'
         futureCellValue = eval(codeString)
         queueOfCellValueInFutureNRows.append(futureCellValue)
         divisor = numberOfFutureRows
      else:
         divisor = len(dataFile.matrix) - currentRowCount

      totalOfFutureNRows += futureCellValue
      totalOfFutureNRows -= queueOfCellValueInFutureNRows.popleft()
  
      averageOfFutureRows = totalOfFutureNRows / float(divisor)


      codeString = 'float(dataFile.matrix[currentRowCount][colNumberOfData.'+args.c+'])'
      valueInCurrentRow = eval(codeString)
      if( averageOfFutureRows > valueInCurrentRow):   
         attribute.aList[currentRowCount][1] = 1
      else:
         attribute.aList[currentRowCount][1] = 0

      attribute.aList[currentRowCount][2] = totalOfFutureNRows
      attribute.aList[currentRowCount][3] = valueInCurrentRow

      currentRowCount = currentRowCount + 1
      if(currentRowCount % 1000 == 0):
         print "Processed row number " + str(currentRowCount) 

