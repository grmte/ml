"""
This can generate features like:
1. fWAPriceOfColAskInLast100Qty
2. fWAPriceOfColBidInLast10000Qty
"""
import dataFile, os, colNumberOfData, attribute, common

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
   try:
      args.tickSize
   except:
      print "args.tickSize is required"
      os._exit(-1)

   tickSize = int(args.tickSize)
   list_of_price_array = [ eval('colNumberOfData.'+args.c+'P0') , eval('colNumberOfData.'+args.c+'P1') ]
   list_of_qty_array = [ eval('colNumberOfData.'+args.c+'Q0') , eval('colNumberOfData.'+args.c+'Q1') ]
   currentRowCount = 0
   qtyForCalculatingWeightedAverage = float(args.n)
   levelOfDataAvailable = 1

   for dataRow in dataFile.matrix:
      qSum = 0
      totalPrice = 0
      totalPriceAtThisLevel = 0
      i = 0
      while(i <= levelOfDataAvailable and qSum < qtyForCalculatingWeightedAverage):
         priceAtThisLevel = float(dataFile.matrix[currentRowCount][list_of_price_array[i]])
         qtyAtThisLevel = float(dataFile.matrix[currentRowCount][list_of_qty_array[i]])
         if i==1:
            if (priceAtThisLevel-float(dataFile.matrix[currentRowCount][list_of_price_array[0]]) ) != abs(float(tickSize)):
               if "AskP" in args.c:
                  priceAtThisLevel = float(dataFile.matrix[currentRowCount][list_of_price_array[0]]) + float(tickSize)
               else:
                  priceAtThisLevel = float(dataFile.matrix[currentRowCount][list_of_price_array[0]]) - float(tickSize)
               qtyAtThisLevel = 0
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

      attribute.aList[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount],colNumberOfData.TimeStamp)
      attribute.aList[currentRowCount][1] = float(totalPrice)/qtyForCalculatingWeightedAverage

      currentRowCount += 1
      if (currentRowCount%10000==0):
         print "Processed row number " + str(currentRowCount)
   
   lNameOfFeaturePrinted = "fWAPriceOfCol" + args.c + "In01PosInLast" + str(args.n) + "Qty"
   return ["TimeStamp",lNameOfFeaturePrinted,"Zero1","Zero2"]

