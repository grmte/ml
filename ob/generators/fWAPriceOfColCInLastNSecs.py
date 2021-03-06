#This program will take ColC qty to take wt avg of the prices ..C has be made keeping in mind that C would be synthetic feature name 
# C = fMovingAverageOfCol_fColCInCurrentRowAvg_InLastNSecs
import dataFile, os, colNumberOfData, attribute, common

def extractAttributeFromDataMatrix(args):
    try:
        args.n
    except:   
        print "Since -n has not been specified I cannot proceed"
        os._exit(-1)
    
    try:
        args.c
        '''
        if args.n not in args.c:
            print "Something wrong in design file "
            print "moving average of last N secs we will taking as qty , so N should be there in sysnthetic fetaure also"
        '''
    except:
        print "Since -c has not been specified I cannot proceed"
        os._exit(-1)
    wt = float(args.n)
    if(args.cType == "synthetic"):
        colNumberOfAttribute = colNumberOfData.SysFeature
    else:
        colNumberOfAttribute = eval("colNumberOfData."+ args.c )

    colNumberOfTimeStamp = colNumberOfData.TimeStamp
    colNumberOfExchangeStamp = colNumberOfData.ExchangeTS

    if "Bid" in args.c:
        side = "Bid"
    elif "Ask" in args.c:
        side = "Ask"
    list_of_price_array = [ eval('colNumberOfData.'+side+'P0') , eval('colNumberOfData.'+side+'P1') ,\
                            eval('colNumberOfData.'+side+'P2') , eval('colNumberOfData.'+side+'P3') , eval('colNumberOfData.'+side+'P4')  ]
    list_of_qty_array = [ eval('colNumberOfData.'+side+'Q0') , eval('colNumberOfData.'+side+'Q1') ,\
                            eval('colNumberOfData.'+side+'Q2') , eval('colNumberOfData.'+side+'Q3') , eval('colNumberOfData.'+side+'Q4')  ]
    currentRowCount = 0
    
    levelOfDataAvailable = 4
    print "data File length"+ str(len(dataFile.matrix))
    for dataRow in dataFile.matrix:
        qSum = 0
        totalPrice = 0
        totalPriceAtThisLevel = 0
        i = 0
        try:
            qtyForCalculatingWeightedAverage = wt * float(dataRow[colNumberOfAttribute])
        except:
            print "Error"
            print dataRow
            print dataRow[colNumberOfAttribute]
            os._exit(1)
        while(i <= levelOfDataAvailable and qSum < qtyForCalculatingWeightedAverage):
            priceAtThisLevel = float(dataFile.matrix[currentRowCount][list_of_price_array[i]])
            qtyAtThisLevel = float(dataFile.matrix[currentRowCount][list_of_qty_array[i]])
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
    
        attribute.aList[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount],colNumberOfTimeStamp)
#        print currentRowCount,qtyForCalculatingWeightedAverage
        attribute.aList[currentRowCount][1] = float(totalPrice)/qtyForCalculatingWeightedAverage
        attribute.aList[currentRowCount][2] = qtyForCalculatingWeightedAverage
        attribute.aList[currentRowCount][3] = totalPrice
        
        currentRowCount += 1
        if (currentRowCount%10000==0):
            print "Processed row number " + str(currentRowCount)
    
    lNameOfFeaturePrinted = "fWAPriceOfCol" + side + "InLast" + str(args.n) + "Qty"
    return ["TimeStamp",lNameOfFeaturePrinted,"QtyUsedForCalWtAvg","TotalPriceCalculatedAtCurrRow"]

