import sys, dataFile, colNumberOfData, attribute, common, aGenArgs
from collections import deque

def extractAttributeFromDataMatrix():
   if aGenArgs.args.n == None:
      N = 5
   else:
      N = int(aGenArgs.args.n) 
   try:
      aGenArgs.args.c
   except:
      print "Since -c has not been specified I cannot proceed"
      os._exit()

   numberOfRowsInLastNSecs = 0
   queueOfValuesInLastNSecs = deque()
   totalOfRowsInLastNSecs = 0.0
   timeOfOldestRow = common.convertTimeStampFromStringToFloat(dataFile.matrix[0][colNumberOfData.TimeStamp])
   currentRowNumberForWhichFeatureValueIsBeingCalculated = 0

   while (currentRowNumberForWhichFeatureValueIsBeingCalculated < len(dataFile.matrix)):
      timeOfCurrentRow = common.convertTimeStampFromStringToFloat(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfData.TimeStamp])
      timeElapsed = timeOfCurrentRow - timeOfOldestRow
      if (timeElapsed < N):
         codeString = 'float(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfData.'+ aGenArgs.args.c + '])'
         cellValue = eval(codeString)
         totalOfRowsInLastNSecs += cellValue
         attribute.list[currentRowNumberForWhichFeatureValueIsBeingCalculated][0] = common.convertTimeStampFromStringToDecimal(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfData.TimeStamp])
         attribute.list[currentRowNumberForWhichFeatureValueIsBeingCalculated][1] = totalOfRowsInLastNSecs/(numberOfRowsInLastNSecs+1) # in 1st iteration currentRowNumberForWhichFeatureValueIsBeingCalculated = 0
         attribute.list[currentRowNumberForWhichFeatureValueIsBeingCalculated][2] = str(totalOfRowsInLastNSecs) + "," + str(numberOfRowsInLastNSecs) + "," + str(timeElapsed)
         queueOfValuesInLastNSecs.append([cellValue,timeOfCurrentRow])
         numberOfRowsInLastNSecs += 1   # Every append gets a +1 
         currentRowNumberForWhichFeatureValueIsBeingCalculated += 1
         continue     # Since we are going back 1 row from current we cannot get data from current row
      else:
         # We need to reset the timeOfOldestRow since timeElapsed has exceeded N seconds
         while(timeElapsed >= N):
            if(len(queueOfValuesInLastNSecs) == 0):
               timeOfOldestRow = timeOfCurrentRow
               timeElapsed = 0
               if(numberOfRowsInLastNSecs != 0):
                  print "Sanity check: This condition is not possible logically. numberOfRowsInLastNSecs should been 0. There has been an unknown error"
                  sys.exit(-1)
               if(totalOfRowsInLastNSecs != 0):
                  print "Sanity check: This condition is not possible logically. totalOfRowsInLastNSecs should have been 0. There has been an unknown error"
                  sys.exit(-1)   
            else:   
               oldestElementInQueue = queueOfValuesInLastNSecs.popleft()
               colValueInOldestElementInQueue = oldestElementInQueue[0]
               colTimeStampInOldestElementInQueue = oldestElementInQueue[1]
               totalOfRowsInLastNSecs -= colValueInOldestElementInQueue
               timeOfOldestRow = colTimeStampInOldestElementInQueue
               numberOfRowsInLastNSecs -= 1 # every pop from the queue gets a -1
               timeElapsed = timeOfCurrentRow - timeOfOldestRow
               if(len(queueOfValuesInLastNSecs) != numberOfRowsInLastNSecs):
                  print "Sanity check: This condition is not possible logically. There has been an unknown error"
                  sys.exit(-1)
 
      print "Processed row number " + str(currentRowNumberForWhichFeatureValueIsBeingCalculated)

