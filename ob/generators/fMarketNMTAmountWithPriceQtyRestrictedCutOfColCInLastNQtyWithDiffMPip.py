import sys, os, dataFile, colNumberOfData, attribute, common
from collections import deque

def extractAttributeFromDataMatrix(args):
   if args.n == None:
      N = 5
   else:
      N = int(args.n) 
   try:
      #Value of argument c can be taken as BidP0 and AskP0 
      args.c
   except:
      print "Since -c has not been specified I cannot proceed"
      os._exit()
   if args.m == None:
       M = 1
   else:
       M = int(args.m.split(".")[0])
       M1 = int(args.m.split(".")[1])
       print "Values of N and N1 are ", M, M1
     
   PIP_SIZE = 5
      
   colNumberOfAttribute = eval("colNumberOfData."+ args.c )
   colNumberOfOppositeAttribute = eval("colNumberOfData.BestBidP") if "ask" in args.c else eval("colNumberOfData.BestAskP")
   colNumberOfTimeStamp = colNumberOfData.TimeStamp
   if "ask" in args.c.lower():
      colAttributeRowNo = [colNumberOfData.BestAskP, colNumberOfData.BestAskP1]#, colNumberOfData.BestAskP2, colNumberOfData.BestAskP3, colNumberOfData.BestAskP4] 
      colAttributeRowNoBand = [colNumberOfData.AskP0, colNumberOfData.AskP1]
   else:
      colAttributeRowNo = [colNumberOfData.BestBidP, colNumberOfData.BestBidP1]#, colNumberOfData.BestBidP2, colNumberOfData.BestBidP3, colNumberOfData.BestBidP4]
      colAttributeRowNoBand = [colNumberOfData.BidP0, colNumberOfData.BidP1]
   numberOfRowsInLastNSecs = 0
   queueOfValuesInLastNQty = []
   lenQ = 0
   totalOfQty = 0.0
   currentRowNumberForWhichFeatureValueIsBeingCalculated = 0
   lengthOfDataMatrix = len(dataFile.matrix)
   while (currentRowNumberForWhichFeatureValueIsBeingCalculated < lengthOfDataMatrix):
      totalOfRowsInLastNQty = 0.0
      totalOfQtyInLastNQty = 0.0
      cellValueTotal = 0
      colAttributeRow = map(float, [dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][i] for i in colAttributeRowNo])
      colAttributeRowBand = map(float, [dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][i] for i in colAttributeRowNoBand])
      timeOfCurrentRow = common.convertTimeStampFromStringToFloat(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfTimeStamp],args.cType)
      oppositeAttribute = float(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfOppositeAttribute])
      if  currentRowNumberForWhichFeatureValueIsBeingCalculated != 0:
          previousRowPrice = float(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated - 1][colNumberOfAttribute])
      else:
          previousRowPrice = 0
      currentPrice = float(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfAttribute])
      currentLTP = float(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfData.LTP])
      currentMsgCode = dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfData.MsgCode]
      newQty = int(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfData.NewQ])
      newPrice = int(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfData.NewP])
      oldQty = int(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfData.OldQ])
      oldPrice = int(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfData.OldP])
      if ( currentMsgCode =='T' and (( oppositeAttribute <= currentLTP ) if "bid" in args.c.lower() else (oppositeAttribute >= currentLTP))):
          cellValueTotal = newQty * currentLTP
          totalOfQty += newQty
          cellValueQty = newQty
          queueOfValuesInLastNQty.append([cellValueTotal, cellValueQty, colAttributeRowBand[0]])
          lenQ += 1
      if ( currentMsgCode == 'M' and ( newPrice in colAttributeRow ) and ((newPrice > oldPrice) if "bid" in args.c.lower() else (newPrice < oldPrice))):
          cellValueTotal = newPrice * newQty
          totalOfQty += newQty
          cellValueQty = newQty
          queueOfValuesInLastNQty.append([cellValueTotal, cellValueQty, colAttributeRowBand[0]])
          lenQ += 1
      elif ( currentMsgCode == 'N' and ( newPrice in colAttributeRow )):
          cellValueTotal = newPrice * newQty
          totalOfQty += newQty
          cellValueQty = newQty
          queueOfValuesInLastNQty.append([cellValueTotal, cellValueQty, colAttributeRowBand[0]])
          lenQ += 1
          
      if totalOfQty > N:
          while totalOfQty > N:
              excess = totalOfQty - N
              if queueOfValuesInLastNQty[0][1] < excess:
                  totalOfQty -= queueOfValuesInLastNQty[0][1]
                  queueOfValuesInLastNQty = queueOfValuesInLastNQty[1:]
                  lenQ -= 1
              else:
                  totalOfQty -= excess
                  price = float(queueOfValuesInLastNQty[0][0]) / queueOfValuesInLastNQty[0][1]
                  queueOfValuesInLastNQty[0][0] = price * (queueOfValuesInLastNQty[0][1] - excess)
                  queueOfValuesInLastNQty[0][1] -= excess
      
      cell = lenQ - 1
      if cell >= 0:
          while ((queueOfValuesInLastNQty[cell][2] > colAttributeRowBand[0] - M * PIP_SIZE and colAttributeRowBand[0] > queueOfValuesInLastNQty[cell][2] - M1 * PIP_SIZE) and ("bid" in args.c.lower())) or ((queueOfValuesInLastNQty[cell][2] < colAttributeRowBand[0] + M * PIP_SIZE and colAttributeRowBand[0] < queueOfValuesInLastNQty[cell][2] + M1 * PIP_SIZE) and ("ask" in args.c.lower())):
              totalOfRowsInLastNQty += queueOfValuesInLastNQty[cell][0]
              totalOfQtyInLastNQty +=  queueOfValuesInLastNQty[cell][1]
              cell -= 1
              if cell < 0:
                  break
              
      exPrice = colAttributeRowBand[0] - M * PIP_SIZE if "bid" in args.c.lower() else colAttributeRowBand[0] + M * PIP_SIZE
      exQty = N - totalOfQtyInLastNQty
      wtdAvg = float(totalOfRowsInLastNQty + exQty * exPrice) / N
           
      attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][0] = common.convertTimeStampFromStringToDecimal(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfTimeStamp],args.cType)
      attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][1] = wtdAvg # in 1st iteration currentRowNumberForWhichFeatureValueIsBeingCalculated = 0
      attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][2] = str(currentPrice) + ";" + str(colAttributeRowBand[0]) + ";" + str(cellValueTotal) + ";" + str(currentMsgCode) + ";" + str(totalOfQtyInLastNQty) + ";" + str(totalOfRowsInLastNQty)
      currentRowNumberForWhichFeatureValueIsBeingCalculated += 1
      continue     # Since we are going back 1 row from current we cannot get data from current row
      print "Processed row number " + str(currentRowNumberForWhichFeatureValueIsBeingCalculated)
   
   lNameOfFeaturePrinted = "fMarketMNTSumOfCol" + args.c + "InLast" + str(args.n) + "Qty" + "WithDiff" + str(args.m) + "Pip"
   return [ "TimeStamp", lNameOfFeaturePrinted , args.c , "LTP" , "TradedQtyWhichIs"+ args.c , "MsgCode", "totalQty", "totalCellValue"]

