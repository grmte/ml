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
   numberOfFutureTrades = int(args.n)

   lTransactionCost = 0.000015
   lPipSize = 25000
   lMargin1 =  ( 1 * lPipSize ) 
   lMargin2 = lMargin1 + ( 2 * lPipSize )

   """ lets get the total of futureNrows"""
   futureTradesCount = 0
   currentRowIndex = 0
   lLastTradeIndex = 0
   lNoMoreTradesFound = 0
   while(futureTradesCount < numberOfFutureTrades):
      if dataFile.matrix[currentRowIndex][colNumberOfData.MsgCode].upper() == "T":
         cellValue = float(dataFile.matrix[currentRowIndex][colNumberOfData.LTP])
         queueOfCellValueInFutureNRows.append(cellValue)
         futureTradesCount = futureTradesCount + 1
      lLastTradeIndex = currentRowIndex
      currentRowIndex = currentRowIndex + 1

   currentRowCount = 0

   for dataRow in dataFile.matrix:

      attribute.aList[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount],colNumberOfData.TimeStamp)
      
      if (dataFile.matrix[currentRowCount][colNumberOfData.MsgCode].upper() == "T") :
          queueOfCellValueInFutureNRows.popleft()
          if (lNoMoreTradesFound == 0):
              startIndexToFindNextTrade = lLastTradeIndex + 1
              while( startIndexToFindNextTrade < len(dataFile.matrix)):
                 if dataFile.matrix[startIndexToFindNextTrade][colNumberOfData.MsgCode].upper() == "T":
                    futureCellValue = float(dataFile.matrix[startIndexToFindNextTrade][colNumberOfData.LTP])
                    queueOfCellValueInFutureNRows.append(futureCellValue)
                    lLastTradeIndex = startIndexToFindNextTrade
                    break
                 startIndexToFindNextTrade = startIndexToFindNextTrade + 1
              if startIndexToFindNextTrade == len(dataFile.matrix) :
                 lNoMoreTradesFound = 1

      currentBidP0 = float(dataFile.matrix[currentRowCount][colNumberOfData.BidP0])
      currentAskP0 = float(dataFile.matrix[currentRowCount][colNumberOfData.AskP0])
      currentLTP = float(dataFile.matrix[currentRowCount][colNumberOfData.LTP])
      currentMsgCode = dataFile.matrix[currentRowCount][colNumberOfData.MsgCode]
      lClassOfTargetVariable = []
      
      valueInCurrentRow = 0
      for LTP in queueOfCellValueInFutureNRows:
          lClassifiedInOneClass = 0
          if (LTP - (currentBidP0 + lPipSize)) > lMargin1 :
              if (LTP - (currentBidP0 + lPipSize)) > lMargin2:
                  lClassOfTargetVariable.append(2)
                  lClassifiedInOneClass = 1
              else:
                  lClassOfTargetVariable.append(1)
                  lClassifiedInOneClass = 1
          if ((currentAskP0 - lPipSize) - LTP ) > lMargin1 :
              if lClassifiedInOneClass == 1 :
                  lClassOfTargetVariable[-1] = 0
              elif ((currentAskP0 - lPipSize) - LTP ) > lMargin2 :
                  lClassOfTargetVariable.append(-2)
                  lClassifiedInOneClass = 1
              else:
                  lClassOfTargetVariable.append(-1)
                  lClassifiedInOneClass = 1
          if lClassifiedInOneClass == 0:
              lClassOfTargetVariable.append(0)
          if lClassOfTargetVariable[-1]==2 or lClassOfTargetVariable[-1]==-2 :
              break
      if len(queueOfCellValueInFutureNRows) == 0 :
          attribute.aList[currentRowCount][1] = 0
          attribute.aList[currentRowCount][2] = currentBidP0
          attribute.aList[currentRowCount][3] = ";".join([ str(currentAskP0) , str(currentLTP) , str(currentMsgCode) , "0" ,"0", "0" , str(LTP)])
      else:  
          lNumberTimesMarketIndicatedBuy  = 0
          lNumberTimesMarketIndicatedSell = 0
          lNumberTimesMarketIndicatedSame = 0
          if (lClassOfTargetVariable[-1] == 2) or (lClassOfTargetVariable[-1] == -2):   
             attribute.aList[currentRowCount][1] = lClassOfTargetVariable[-1]
          else:
             lNumberTimesMarketIndicatedBuy = lClassOfTargetVariable.count(1) 
             lNumberTimesMarketIndicatedSell = lClassOfTargetVariable.count(-1)
             lNumberTimesMarketIndicatedSame = lClassOfTargetVariable.count(0)
             if ( lNumberTimesMarketIndicatedBuy > lNumberTimesMarketIndicatedSell ) and (lNumberTimesMarketIndicatedBuy > lNumberTimesMarketIndicatedSame):
                 attribute.aList[currentRowCount][1] = 1
             elif ( lNumberTimesMarketIndicatedSell > lNumberTimesMarketIndicatedBuy ) and (lNumberTimesMarketIndicatedSell > lNumberTimesMarketIndicatedSame):
                 attribute.aList[currentRowCount][1] = -1
             else:
                 attribute.aList[currentRowCount][1] = 0
          
          attribute.aList[currentRowCount][2] = currentBidP0
          attribute.aList[currentRowCount][3] = ";".join([ str(currentAskP0) ,str(currentLTP) , str(currentMsgCode) , str(lNumberTimesMarketIndicatedBuy) , str(lNumberTimesMarketIndicatedSell) , str(lNumberTimesMarketIndicatedSame) , str(queueOfCellValueInFutureNRows[-1]) ]) 

      currentRowCount = currentRowCount + 1
      if(currentRowCount % 1000 == 0):
         print "Processed row number " + str(currentRowCount) 
         
   lNameOfTarget = "tClassOfTargetVariableInFuture"+ str(args.n) + "TradeTicks" 
   return ["TimeStamp",lNameOfTarget,"CurrentBid","CurrentAsk","CurrentLTP","CurrentMsgCode",\
           "NumberTimesMarketIndicatedBuy" , "NumberTimesMarketIndicatedSell" , "NumberTimesMarketIndicatedSame",\
           "ValueOfTargetVariableFromCurrentToNextNthTickTaken"]
