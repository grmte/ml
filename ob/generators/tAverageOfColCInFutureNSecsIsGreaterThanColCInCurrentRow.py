import os, colNumberOfData, dataFile, aGenArgs, attribute, common
from collections import deque

def extractAttributeFromDataMatrix():
   if aGenArgs.args.n is None:
      print "N has not been specified"
      os._exit(-1)
   try:
      aGenArgs.args.c
      colNumberWeAreWorkingWith = eval('colNumberOfData.'+aGenArgs.args.c)
   except:
      print "C has not been specified"
      os._exit(-1)
   numberOfSecondsInFuture = int(aGenArgs.args.n)
   currentRowCount = 0
   totalNumberOfDataRows = len(dataFile.matrix)
   futureRowCount = 1  # Since we have a queue we do not need to initialize everytime inside the for loop
   totalOfRowsInFutureNSeconds = 0.0
   queue = deque()
   for dataRow in dataFile.matrix:
      timeOfCurrentRow = common.getTimeStamp(dataFile.matrix[currentRowCount])
      # lets remove all values from queue which have time <= timeOfCurrentRow
      if(len(queue) > 0): # When currentRowCount is 0 then there is nothing in the queue
         oldestElementinQueue = queue.popleft()
         while(oldestElementinQueue[0] < timeOfCurrentRow):
            oldestElementinQueue = queue.popleft()
            totalOfRowsInFutureNSeconds -= oldestElementinQueue[1]
      attribute.list[currentRowCount][0] = timeOfCurrentRow
      while True:
         if(currentRowCount + futureRowCount < totalNumberOfDataRows):   # If the totalNumberOfDataRows is 5 we can access index values 0 to 4.
            timeOfFutureRow = common.getTimeStamp(dataFile.matrix[currentRowCount + futureRowCount])
            if(timeOfFutureRow - timeOfCurrentRow < numberOfSecondsInFuture):
               cellValue = float(dataFile.matrix[currentRowCount + futureRowCount][colNumberWeAreWorkingWith])
               totalOfRowsInFutureNSeconds += cellValue
               futureRowCount = futureRowCount + 1
               # add the data to queue for future needs
               queue.append([timeOfFutureRow,cellValue])
            else:
               break
         else:
            break
      averageOfFutureRows = totalOfRowsInFutureNSeconds / futureRowCount
      currentCellValue = float(dataFile.matrix[currentRowCount][colNumberWeAreWorkingWith])
      if( averageOfFutureRows > currentCellValue):   
         attribute.list[currentRowCount][1] = 1
      else:
         attribute.list[currentRowCount][1] = 0

      attribute.list[currentRowCount][2] = totalOfRowsInFutureNSeconds
      attribute.list[currentRowCount][3] = float(dataFile.matrix[currentRowCount][colNumberOfData.LTP])

      currentRowCount = currentRowCount + 1

      if(currentRowCount % 1 == 0):
         print "Processed row number " + str(currentRowCount) 

