import os
import colNumberOfData
import dataFile

import attribute
import common
from collections import deque

def extractAttributeFromDataMatrix(args):
   queueOfCellValueInFutureNLTQs = deque()
   totalOfFutureNRows = 0.0
   if args.n is None:
       print "-n has not been specified"
       os._exit(-1)
   totalOfFutureLTQQty = int(args.n)

   lPipSize = int(args.tickSize)
   lMargin1 =  ( 1 * lPipSize ) 
   lMargin2 = lMargin1 + ( 2 * lPipSize )

   """ lets get the total of futureNrows"""
   futureLTQSum = 0
   currentRowIndex = 0
   lLastTradeIndex = 0
   lNoMoreTradesFound = 0
   currentLTPValue = 0.0
   currentLTQValue = 0
   WeightedLTPSum = 0.0
   totalLTPQty = totalOfFutureLTQQty
   while(futureLTQSum < totalOfFutureLTQQty):
      if dataFile.matrix[currentRowIndex][colNumberOfData.MsgCode].upper() == "T":
         currentLTPValue = float(dataFile.matrix[currentRowIndex][colNumberOfData.LTP])
         currentLTQValue = int(dataFile.matrix[currentRowIndex][colNumberOfData.NewQ])
         queueOfCellValueInFutureNLTQs.append( [ (currentLTPValue * currentLTQValue) , currentLTQValue , currentLTPValue , 0 ]  )
         futureLTQSum = futureLTQSum + currentLTQValue
         WeightedLTPSum = WeightedLTPSum + queueOfCellValueInFutureNLTQs[-1][0] 
      lLastTradeIndex = currentRowIndex
      currentRowIndex = currentRowIndex + 1
   if futureLTQSum > totalOfFutureLTQQty :
      currentLTQValueToBeUsed = currentLTQValue - ( futureLTQSum - totalOfFutureLTQQty ) 
      currentTickPriceToBeAdded  = currentLTPValue * currentLTQValueToBeUsed 
      LTQValueNotAdded = ( futureLTQSum - totalOfFutureLTQQty )
      WeightedLTPSum = WeightedLTPSum - queueOfCellValueInFutureNLTQs[-1][0] + currentTickPriceToBeAdded
      queueOfCellValueInFutureNLTQs[-1] = [ currentTickPriceToBeAdded , currentLTQValueToBeUsed , currentLTPValue , LTQValueNotAdded ]
   currentRowCount = 0

   for dataRow in dataFile.matrix:

      attribute.aList[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount],colNumberOfData.TimeStamp)
      
      if (dataFile.matrix[currentRowCount][colNumberOfData.MsgCode].upper() == "T") :
          currentWtLTQToBeSubtracted = queueOfCellValueInFutureNLTQs.popleft()
          WeightedLTPSum = WeightedLTPSum - currentWtLTQToBeSubtracted[0]
          LTQSubtracted = currentWtLTQToBeSubtracted[1]
          if len(queueOfCellValueInFutureNLTQs) != 0:
              LTQWhichCanBeAddedWithoutNewTradeMessage = queueOfCellValueInFutureNLTQs[-1][3]
              LTQAddedWithoutNewTradeMessage = min( LTQSubtracted , LTQWhichCanBeAddedWithoutNewTradeMessage)
              currentTickPriceToBeAdded = ( LTQAddedWithoutNewTradeMessage * queueOfCellValueInFutureNLTQs[-1][2] ) + queueOfCellValueInFutureNLTQs[-1][0]
              LTQValueNotAddedInLastElementOfQueue = queueOfCellValueInFutureNLTQs[-1][3] - LTQAddedWithoutNewTradeMessage
              WeightedLTPSum = WeightedLTPSum - queueOfCellValueInFutureNLTQs[-1][0] + currentTickPriceToBeAdded
              queueOfCellValueInFutureNLTQs[-1][0] =  currentTickPriceToBeAdded
              queueOfCellValueInFutureNLTQs[-1][1] = queueOfCellValueInFutureNLTQs[-1][1] + LTQAddedWithoutNewTradeMessage
              queueOfCellValueInFutureNLTQs[-1][3] = LTQValueNotAddedInLastElementOfQueue
          else:
              LTQAddedWithoutNewTradeMessage = 0
              print "Last element in queue = " , currentWtLTQToBeSubtracted
          if LTQSubtracted >  LTQAddedWithoutNewTradeMessage:
              LTQToBeAddedFromNewTrade = LTQSubtracted - LTQAddedWithoutNewTradeMessage
              if (lNoMoreTradesFound == 0):
                  startIndexToFindNextTrade = lLastTradeIndex + 1
                  while( startIndexToFindNextTrade < len(dataFile.matrix)):
                     if dataFile.matrix[startIndexToFindNextTrade][colNumberOfData.MsgCode].upper() == "T":
                        lLastTradeIndex = startIndexToFindNextTrade 
                        futureLTPValue = float(dataFile.matrix[startIndexToFindNextTrade][colNumberOfData.LTP])
                        futureLTQValue = int(dataFile.matrix[startIndexToFindNextTrade][colNumberOfData.NewQ])
                        queueOfCellValueInFutureNLTQs.append( [ (futureLTPValue * futureLTQValue) , futureLTQValue , futureLTPValue , 0 ]  )
                        LTQToBeAddedFromNewTrade = LTQToBeAddedFromNewTrade - futureLTQValue
                        WeightedLTPSum = WeightedLTPSum + queueOfCellValueInFutureNLTQs[-1][0] 
                        
                        if LTQToBeAddedFromNewTrade <= 0 :
                            if LTQToBeAddedFromNewTrade < 0 :
                                LTQValueToBeUsed = futureLTQValue + LTQToBeAddedFromNewTrade
                                currentTickPriceToBeAdded  = LTQValueToBeUsed * futureLTPValue 
                                LTQValueNotAdded = -1 * LTQToBeAddedFromNewTrade
                                WeightedLTPSum = WeightedLTPSum - queueOfCellValueInFutureNLTQs[-1][0] + currentTickPriceToBeAdded
                                queueOfCellValueInFutureNLTQs[-1] = [ currentTickPriceToBeAdded , LTQValueToBeUsed , futureLTPValue , LTQValueNotAdded ]
                               
                            break
                     startIndexToFindNextTrade = startIndexToFindNextTrade + 1
                  if startIndexToFindNextTrade == len(dataFile.matrix):
                     if LTQToBeAddedFromNewTrade > 0 :
                         totalLTPQty = totalLTPQty - LTQToBeAddedFromNewTrade 
                     lNoMoreTradesFound = 1
              else:
                  totalLTPQty = totalLTPQty - LTQToBeAddedFromNewTrade 
      currentBidP0 = float(dataFile.matrix[currentRowCount][colNumberOfData.BidP0])
      currentAskP0 = float(dataFile.matrix[currentRowCount][colNumberOfData.AskP0])
      currentLTP = float(dataFile.matrix[currentRowCount][colNumberOfData.LTP])
      currentMsgCode = dataFile.matrix[currentRowCount][colNumberOfData.MsgCode]
      currentLTQ = int(dataFile.matrix[currentRowCount][colNumberOfData.NewQ])

      lClassOfTargetVariable = 0
      valueInCurrentRow = 0
      lClassifiedInOneClass = 0
      if totalLTPQty != 0:
          WALTPOfFutureNQty = WeightedLTPSum / totalLTPQty
      if (WALTPOfFutureNQty - (currentBidP0 + lPipSize)) > lMargin1 :
          if (WALTPOfFutureNQty - (currentBidP0 + lPipSize)) > lMargin2:
              lClassOfTargetVariable = 2
              lClassifiedInOneClass = 1
          else:
              lClassOfTargetVariable = 1
              lClassifiedInOneClass = 1
      if ((currentAskP0 - lPipSize) - WALTPOfFutureNQty ) > lMargin1 :
          if lClassifiedInOneClass == 1 :
              lClassOfTargetVariable = 0
          elif ((currentAskP0 - lPipSize) - WALTPOfFutureNQty ) > lMargin2 :
              lClassOfTargetVariable = -2
              lClassifiedInOneClass = 1
          else:
              lClassOfTargetVariable = -1
              lClassifiedInOneClass = 1
      attribute.aList[currentRowCount][1] = lClassOfTargetVariable
      attribute.aList[currentRowCount][2] = currentBidP0
      attribute.aList[currentRowCount][3] = ";".join([ str(currentAskP0) , str(WALTPOfFutureNQty) , str(currentLTP) , str(currentLTQ) ,\
                                                       str(currentMsgCode) , str(WeightedLTPSum) , str(totalLTPQty)
                                                        ])

      currentRowCount = currentRowCount + 1
      if(currentRowCount % 1000 == 0):
         print "Processed row number " + str(currentRowCount) 
         
   lNameOfTarget = "tClassOfTargetVariableInFuture"+ str(args.n) + "TradeTicks" 
   return ["TimeStamp",lNameOfTarget,"CurrentBid","CurrentAsk","ValueOfTargetVariableFromCurrentToNextNthTickTaken","CurrentLTP","CurrentLTQ","CurrentMsgCode"\
           "WeightedLTPSum" , "totalLTPQtys"]
