"""
This can generate features like:
1. fWeightedAveragePriceOfColAskInLast100Qty
2. fWeightedAveragePriceOfColBidInLast10000Qty
"""
import dataFile, os, colNumberOfData, attribute, common
from collections import deque
def extractAttributeFromDataMatrix(args):
   try:
      args.n
   except:   
      print "Since -n has not been specified I cannot proceed"
      os._exit(-1)

   try:
      args.c
   except:
      print "Since -c has not been specified I cannot proceed"
      os._exit(-1)
   temp_list = []
   temp_list =  [[0 for x in xrange(2)] for x in xrange(len(dataFile.matrix))]
   queueOfCellValueInLastMRows = deque()
   totalOfLastMRows = 0
   M = 300
   currentRowCount = 0
   qtyForCalculatingWeightedAverage = float(args.n)
   levelOfDataAvailable = 4
   for dataRow in dataFile.matrix:
      qSum = 0
      totalPrice = 0
      totalPriceAtThisLevel = 0
      i = 0
      while(i <= levelOfDataAvailable and qSum < qtyForCalculatingWeightedAverage):
         codeStringForQ = 'float(dataFile.matrix['+str(currentRowCount)+'][colNumberOfData.'+args.c+'Q'+str(i)+'])'
         codeStringForP = 'float(dataFile.matrix['+str(currentRowCount)+'][colNumberOfData.'+args.c+'P'+str(i)+'])'
         priceAtThisLevel = eval(codeStringForP)
         qtyAtThisLevel = eval(codeStringForQ)
         qSum += qtyAtThisLevel
         if(qSum > qtyForCalculatingWeightedAverage):
            qtyToUseAtThisLevel = qtyAtThisLevel - (qSum - qtyForCalculatingWeightedAverage)
            totalPriceAtThisLevel = qtyToUseAtThisLevel * priceAtThisLevel
         else:
            totalPriceAtThisLevel = qtyAtThisLevel * priceAtThisLevel
         
         totalPrice += totalPriceAtThisLevel
         i = i + 1
         
      if(qSum < qtyForCalculatingWeightedAverage): # This implies that the current row does not have enough qty to fill our requirement.
         qtyToUseAtThisLevel =  qtyForCalculatingWeightedAverage - qSum
         totalPriceAtThisLevel = qtyToUseAtThisLevel * priceAtThisLevel
         totalPrice += totalPriceAtThisLevel
      cellValue = float(totalPrice)/qtyForCalculatingWeightedAverage
      queueOfCellValueInLastMRows.append(cellValue)
      totalOfLastMRows += cellValue
      if (currentRowCount < M):
          attribute.list[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount])
          attribute.list[currentRowCount][1] = totalOfLastMRows/(currentRowCount+1)
          currentRowCount = currentRowCount + 1
          continue  
      totalOfLastMRows -= queueOfCellValueInLastMRows.popleft()
      attribute.list[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount])
      attribute.list[currentRowCount][1] = totalOfLastMRows / M
      currentRowCount += 1
      if (currentRowCount%10000==0):
         print "Processed row number " + str(currentRowCount)
    
