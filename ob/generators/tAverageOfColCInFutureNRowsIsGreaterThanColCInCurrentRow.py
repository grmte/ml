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
      print "-n has not been specified"
      os._exit(-1)
   numberOfFutureRows = int(aGenArgs.args.n)

   try:
      aGenArgs.args.c 
   except:   
      print "-c has not been specified"
      os._exit(-1)
   
   """ lets get the total of futureNrows"""
   futureRowCount = 0   
   while(futureRowCount < numberOfFutureRows):
      codeString = 'float(dataFile.matrix[futureRowCount][colNumberOfData.'+aGenArgs.args.c+'])' 
      cellValue = eval(codeString)
      queueOfCellValueInFutureNRows.append(cellValue)
      totalOfFutureNRows += cellValue
      futureRowCount = futureRowCount + 1


   currentRowCount = 0


   for dataRow in dataFile.matrix:

      attribute.list[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount])
      futureCellValue = 0

      if(currentRowCount + numberOfFutureRows < len(dataFile.matrix)):
         codeString = 'float(dataFile.matrix[currentRowCount+numberOfFutureRows][colNumberOfData.'+aGenArgs.args.c+'])'
         futureCellValue = eval(codeString)
         queueOfCellValueInFutureNRows.append(futureCellValue)
         divisor = numberOfFutureRows
      else:
         divisor = len(dataFile.matrix) - currentRowCount

      totalOfFutureNRows += futureCellValue
      totalOfFutureNRows -= queueOfCellValueInFutureNRows.popleft()
  
      averageOfFutureRows = totalOfFutureNRows / float(divisor)


      codeString = 'float(dataFile.matrix[currentRowCount][colNumberOfData.'+aGenArgs.args.c+'])'
      valueInCurrentRow = eval(codeString)
      if( averageOfFutureRows > valueInCurrentRow):   
         attribute.list[currentRowCount][1] = 1
      else:
         attribute.list[currentRowCount][1] = 0

      attribute.list[currentRowCount][2] = totalOfFutureNRows
      attribute.list[currentRowCount][3] = valueInCurrentRow

      currentRowCount = currentRowCount + 1
      if(currentRowCount % 1000 == 0):
         print "Processed row number " + str(currentRowCount) 

