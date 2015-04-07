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
   try:
      M = int(args.m)
   except:
      print "-m wrong!!"
   colNumberOfAttribute = eval("colNumberOfData."+ args.c )
   colNumberOfOppositeAttribute = eval("colNumberOfData.BestBidP") if "ask" in args.c else eval("colNumberOfData.BestAskP")
   colNumberOfTimeStamp = colNumberOfData.TimeStamp
   if "ask" in args.c.lower():
      colAttributeRowNo = [colNumberOfData.AskP0, colNumberOfData.AskP1]#, colNumberOfData.AskP2, colNumberOfData.AskP3, colNumberOfData.AskP4] 
   else:
      colAttributeRowNo = [colNumberOfData.BidP0, colNumberOfData.BidP1]#, colNumberOfData.BidP2, colNumberOfData.BidP3, colNumberOfData.BidP4]
   numberOfRowsInLastNSecs = 0
   queueOfValuesInLastNSecsN = []
   queueOfValuesInLastNSecsX = []
   totalOfRowsInLastNSecsX = 0.0
   totalOfRowsInLastNSecsN = 0.0
   totalOfQtyInLastNSecsX = 0.0
   totalOfQtyInLastNSecsN = 0.0
   
   timeOfOldestRow = common.convertTimeStampFromStringToFloat(dataFile.matrix[0][colNumberOfTimeStamp],args.cType)
   currentRowNumberForWhichFeatureValueIsBeingCalculated = 0
   lengthOfDataMatrix = len(dataFile.matrix)
   while (currentRowNumberForWhichFeatureValueIsBeingCalculated < lengthOfDataMatrix):
      cellValueQtyN, cellValueQtyX, cellValueTotalN, cellValueTotalX = [0,0,0,0]
      colAttributeRow = map(float, [dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][i] for i in colAttributeRowNo])
      timeOfCurrentRow = common.convertTimeStampFromStringToFloat(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfTimeStamp],args.cType)
      if  currentRowNumberForWhichFeatureValueIsBeingCalculated != 0:
          previousRowPrice = float(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated - 1][colNumberOfAttribute])
          previousRowOppPrice = float(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated - 1][colNumberOfOppositeAttribute])
      else:
          previousRowPrice = 0
          previousRowOppPrice = 0
      currentPrice = float(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfAttribute])
      currentLTP = float(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfData.LTP])
      currentMsgCode = dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfData.MsgCode]
      newQty = int(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfData.NewQ])
      newPrice = int(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfData.NewP])
      oldQty = int(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfData.OldQ])
      oldPrice = int(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfData.OldP])
      if ( currentMsgCode =='T' and (( previousRowOppPrice <= currentLTP ) if "bid" in args.c.lower() else (previousRowOppPrice >= currentLTP))):
          totalOfRowsInLastNSecsN += newQty * currentLTP
          cellValueTotalN = newQty * currentLTP
          totalOfQtyInLastNSecsN += newQty
          cellValueQtyN = newQty
          queueOfValuesInLastNSecsN.append([cellValueTotalN,colAttributeRow[-1],cellValueQtyN,currentLTP,timeOfCurrentRow])
         
      elif currentMsgCode == 'M':
          if ("ask" in args.c.lower() and newPrice <= colAttributeRow[-1] and newPrice >= currentPrice) or ("bid" in args.c.lower() and newPrice >= colAttributeRow[-1] and newPrice <= currentPrice):
              check = True
          else:
              check = False
          totalOfRowsInLastNSecsN += (newPrice * newQty) if check else 0 
          cellValueTotalN = newPrice * newQty if check else 0
          totalOfQtyInLastNSecsN += newQty if check else 0
          cellValueQtyN = newQty if check else 0
          if check:
              queueOfValuesInLastNSecsN.append([cellValueTotalN,colAttributeRow[-1],cellValueQtyN,newPrice,timeOfCurrentRow])              
          
          if ("ask" in args.c.lower() and oldPrice <= colAttributeRow[-1] and oldPrice >= previousRowPrice) or ("bid" in args.c.lower() and oldPrice >= colAttributeRow[-1] and oldPrice <= previousRowPrice):
              check = True
          else:
              check = False
          totalOfRowsInLastNSecsX += oldPrice * oldQty if check else 0
          cellValueTotalX = oldPrice * oldQty if check else 0
          totalOfQtyInLastNSecsX += oldQty if check else 0
          cellValueQtyX = oldQty if check else 0
          if check:
              queueOfValuesInLastNSecsX.append([cellValueTotalX,colAttributeRow[-1],cellValueQtyX,oldPrice,timeOfCurrentRow])
        
      elif ( currentMsgCode == 'N'):
          if ("ask" in args.c.lower() and newPrice <= colAttributeRow[-1] and newPrice >= currentPrice) or ("bid" in args.c.lower() and newPrice >= colAttributeRow[-1] and newPrice <= currentPrice):
              check = True
          else:
              check = False
          totalOfRowsInLastNSecsN += newPrice * newQty if check else 0
          cellValueTotalN = newPrice * newQty if check else 0
          totalOfQtyInLastNSecsN += newQty if check else 0
          cellValueQtyN = newQty if check else 0
          if check:
              queueOfValuesInLastNSecsN.append([cellValueTotalN,colAttributeRow[-1],cellValueQtyN,newPrice,timeOfCurrentRow])
         
      elif ( currentMsgCode == 'X'):
          if ("ask" in args.c.lower() and newPrice <= colAttributeRow[-1] and newPrice >= previousRowPrice) or ("bid" in args.c.lower() and newPrice >= colAttributeRow[-1] and newPrice <= previousRowPrice):
              check = True
          else:
              check = False
          totalOfRowsInLastNSecsX += newPrice * newQty if check else 0
          cellValueTotalX = newPrice * newQty if check else 0
          totalOfQtyInLastNSecsX += newQty if check else 0
          cellValueQtyX = newQty if check else 0
          if check:
              queueOfValuesInLastNSecsX.append([cellValueTotalX,colAttributeRow[-1],cellValueQtyX,newPrice,timeOfCurrentRow])

      if(totalOfQtyInLastNSecsN) > N:
          while totalOfQtyInLastNSecsN > N:
              excess = totalOfQtyInLastNSecsN - N
              if queueOfValuesInLastNSecsN[0][2] <= excess:
                  totalOfQtyInLastNSecsN -= queueOfValuesInLastNSecsN[0][2]
                  totalOfRowsInLastNSecsN -= queueOfValuesInLastNSecsN[0][0]
                  queueOfValuesInLastNSecsN = queueOfValuesInLastNSecsN[1:]
              else:
                  totalOfQtyInLastNSecsN -= excess 
                  totalOfRowsInLastNSecsN -= excess * float(queueOfValuesInLastNSecsN[0][0]) / queueOfValuesInLastNSecsN[0][2]
                  queueOfValuesInLastNSecsN[0][2] -= excess
                  queueOfValuesInLastNSecsN[0][0] -= excess * queueOfValuesInLastNSecsN[0][3]

      if(totalOfQtyInLastNSecsX) > N:
          while totalOfQtyInLastNSecsX > N:
              excess = totalOfQtyInLastNSecsX - N
              if queueOfValuesInLastNSecsX[0][2] <= excess:
                  totalOfQtyInLastNSecsX -= queueOfValuesInLastNSecsX[0][2]
                  totalOfRowsInLastNSecsX -= queueOfValuesInLastNSecsX[0][0]
                  queueOfValuesInLastNSecsX = queueOfValuesInLastNSecsX[1:]
              else:
                  totalOfQtyInLastNSecsX -= excess 
                  totalOfRowsInLastNSecsX -= excess * float(queueOfValuesInLastNSecsX[0][0]) / queueOfValuesInLastNSecsX[0][2]
                  queueOfValuesInLastNSecsX[0][2] -= excess
                  queueOfValuesInLastNSecsX[0][0] -= excess * queueOfValuesInLastNSecsX[0][3]
                  
      if M == 1:
          exPrice = colAttributeRow[-1]
      elif M == 2:
          try:
              exPrice = queueOfValuesInLastNSecsN[0][1] if queueOfValuesInLastNSecsN[0][-1] < queueOfValuesInLastNSecsX[0][-1] else queueOfValuesInLastNSecsX[0][1]
          except:
              print("Warning!!!!")
              exPrice = colAttributeRow[-1]
      elif M == 3:
          try:
            exPrice = totalOfRowsInLastNSecsN / float(totalOfQtyInLastNSecsN)
          except:
            print("Warning!!!!")
            exPrice = colAttributeRow[-1]
      elif M == 4:
          try:
              exPrice = totalOfRowsInLastNSecsX / float(totalOfQtyInLastNSecsX)
          except:
              print("Warning!!!!")
              exPrice = colAttributeRow[-1]
      
      newSide = (float(totalOfRowsInLastNSecsN + (N - totalOfQtyInLastNSecsN) * exPrice) / N)
      cancelSide = (float(totalOfRowsInLastNSecsX + (N - totalOfQtyInLastNSecsX) * exPrice) / N)
      attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][0] = common.convertTimeStampFromStringToDecimal(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfTimeStamp],args.cType)
      attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][1] = (float(newSide) - cancelSide) # in 1st iteration currentRowNumberForWhichFeatureValueIsBeingCalculated = 0
      attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][2] = str(currentPrice) + ";" + str(cellValueQtyN) + ";" + str(cellValueQtyX) + ";" + str(cellValueTotalN) + ";" + str(cellValueTotalX) + ";" + str(currentMsgCode)
      numberOfRowsInLastNSecs += 1   # Every append gets a +1 
#      if currentRowNumberForWhichFeatureValueIsBeingCalculated == 164:
#          import pdb
#          pdb.set_trace()
      currentRowNumberForWhichFeatureValueIsBeingCalculated += 1
      continue     # Since we are going back 1 row from current we cannot get data from current row
      print "Processed row number " + str(currentRowNumberForWhichFeatureValueIsBeingCalculated)
   
   lNameOfFeaturePrinted = "fMarketModNewSumOfCol" + args.c + "InLast" + str(args.n) + "Secs"
   return [ "TimeStamp", lNameOfFeaturePrinted , args.c , "QtyForN" , "QtyForX", "AmountN" , "AmountX", "MsgCode"]

