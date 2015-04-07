import sys, dataFile, colNumberOfData, attribute, common
from collections import deque

def extractAttributeFromDataMatrix(args):
    if args.n == None:
        N = 5
    else:
        N = int(args.n) 
    try:
        args.c
    except:
        print "Since -c has not been specified I cannot proceed"
        os._exit()
    colNumberOfLTP = colNumberOfData.LTP
    colNumberOfTTQ = colNumberOfData.TTQ
    
    colNumberOfTimeStamp = colNumberOfData.TimeStamp
    colNumberOfExchangeStamp = colNumberOfData.ExchangeTS
    numberOfRowsInLastNSecs = 0
    queueOfValuesInLastNSecs = deque()
    totalOfRowsInLastNSecs = 0.0
    timeOfOldestRow = common.convertTimeStampFromStringToFloat(dataFile.matrix[0][colNumberOfExchangeStamp],"synthetic")
    currentRowNumberForWhichFeatureValueIsBeingCalculated = 0
    l_sum_LtQ = 0
    prevTTQ = 0
    lengthOfDataMatrix = len(dataFile.matrix)
    print "lengthOfDataMatrix",lengthOfDataMatrix
    while (currentRowNumberForWhichFeatureValueIsBeingCalculated < lengthOfDataMatrix):
        timeOfCurrentRow = common.convertTimeStampFromStringToFloat(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfExchangeStamp],"synthetic")
        timeElapsed = timeOfCurrentRow - timeOfOldestRow
        TtqOfCurrentRow = int(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfTTQ])
        LtpCurrentRow = float(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfLTP])
        if (timeElapsed < N):
            l_diff_TTQ = TtqOfCurrentRow-prevTTQ
            cellValue = LtpCurrentRow * l_diff_TTQ
            totalOfRowsInLastNSecs += cellValue
            l_sum_LtQ += l_diff_TTQ
            attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][0] = common.convertTimeStampFromStringToDecimal(dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated][colNumberOfTimeStamp])
            if l_sum_LtQ != 0:
                attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][1] = totalOfRowsInLastNSecs/(l_sum_LtQ) # in 1st iteration currentRowNumberForWhichFeatureValueIsBeingCalculated = 0
            else:
                attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][1] = 1
            attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][2] = str(totalOfRowsInLastNSecs)
            attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][3] = str(l_sum_LtQ) + ";" + str(TtqOfCurrentRow) + ";"+str(LtpCurrentRow) + ";" + str(timeElapsed) + ";" + str(timeOfCurrentRow)
            queueOfValuesInLastNSecs.append([l_diff_TTQ,cellValue,timeOfCurrentRow])
            prevTTQ = TtqOfCurrentRow
            numberOfRowsInLastNSecs +=1
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
                    LtqValueInOldRow =  oldestElementInQueue[0]
                    colValueInOldestElementInQueue = oldestElementInQueue[1]
                    totalOfRowsInLastNSecs -= colValueInOldestElementInQueue
                    l_sum_LtQ -= LtqValueInOldRow
                    if len(queueOfValuesInLastNSecs) == 0:
                        timeElapsed = 0
                        timeOfOldestRow = timeOfCurrentRow
                    else:
                        timeOfOldestRow = queueOfValuesInLastNSecs[0][2]
                    numberOfRowsInLastNSecs -= 1 # every pop from the queue gets a -1
                    timeElapsed = timeOfCurrentRow - timeOfOldestRow
                    if(len(queueOfValuesInLastNSecs) != numberOfRowsInLastNSecs):
                        print "Sanity check: This condition is not possible logically. There has been an unknown error"
                        sys.exit(-1)
        
        print "Processed row number " + str(currentRowNumberForWhichFeatureValueIsBeingCalculated)
    
    lNameOfFeaturePrinted = "fWALTPInLast" + str(args.n) + "Secs"
    return [ "TimeStamp", lNameOfFeaturePrinted , "totalValueOfRowsInLastNSecs" , "LtqSum" ,"TTQ", "LTP", "TimeElapsed" ,"ExTimeStamp"]
    
