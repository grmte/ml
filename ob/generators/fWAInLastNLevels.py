import sys, dataFile,os, colNumberOfData, attribute, common

def extractAttributeFromDataMatrix(args):
    currentRowCount = 0
    lAPL = [ colNumberOfData.AskP0 , colNumberOfData.AskP1 , colNumberOfData.AskP2 , colNumberOfData.AskP3 , colNumberOfData.AskP4  ]
    lAQL = [ colNumberOfData.AskQ0 , colNumberOfData.AskQ1 , colNumberOfData.AskQ2 , colNumberOfData.AskQ3 , colNumberOfData.AskQ4   ]
    lBPL = [ colNumberOfData.BidP0 , colNumberOfData.BidP1 , colNumberOfData.BidP2 , colNumberOfData.BidP3 , colNumberOfData.BidP4  ]
    lBQL = [ colNumberOfData.BidQ0 , colNumberOfData.BidQ1 , colNumberOfData.BidQ2 , colNumberOfData.BidQ3 , colNumberOfData.BidQ4   ]
    
    if args.n == None:
        print "Since -n has not been specified I cannot proceed"
        os._exit()        
    else:
        N = int(args.n) 
            
    for dataRow in dataFile.matrix:
        askp = []
        askq = []
        bidp = []
        bidq = []
        lPriceMulQtySum = 0
        lQtySum = 0
        for i in range(0,N):
            askp.append(float(dataRow[lAPL[i]]))
            askq.append(float(dataRow[lAQL[i]]))
            bidp.append(float(dataRow[lBPL[i]]))
            bidq.append(float(dataRow[lBQL[i]]))
             
        for price, qty in zip(askp[:N] + bidp[:N], askq[:N] + bidq[:N]):
            lPriceMulQtySum += float(price) * float(qty)
            lQtySum += float(qty) 

        qAverage = lPriceMulQtySum / lQtySum
        attribute.aList[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount],colNumberOfData.TimeStamp)
        attribute.aList[currentRowCount][1] = qAverage
        currentRowCount = currentRowCount + 1
        if (currentRowCount%10000==0):
            print "Processed row number " + str(currentRowCount)
    
    lNameOfFeaturePrinted = "fInverseWAInLast" + str(N) + "Levels"
    return ["TimeStamp",lNameOfFeaturePrinted,"Zero1","Zero2"]
