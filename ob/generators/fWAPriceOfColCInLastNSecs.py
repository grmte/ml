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
        if args.n not in args.c:
            print "Something wrong in design file "
            print "moving average of last N secs we will taking as qty , so N should be there in sysnthetic fetaure also"
    except:
        print "Since -c has not been specified I cannot proceed"
        os._exit(-1)

    if(args.cType == "synthetic"):
        colNumberOfAttribute = colNumberOfData.SysFeature
    else:
        colNumberOfAttribute = eval("colNumberOfData."+ args.c )

    colNumberOfTimeStamp = colNumberOfData.TimeStamp
    colNumberOfExchangeStamp = colNumberOfData.ExchangeTS
    
    list_of_price_array = [ eval('colNumberOfData.'+args.c+'P0') , eval('colNumberOfData.'+args.c+'P1') ,\
                            eval('colNumberOfData.'+args.c+'P2') , eval('colNumberOfData.'+args.c+'P3') , eval('colNumberOfData.'+args.c+'P4')  ]
    list_of_qty_array = [ eval('colNumberOfData.'+args.c+'Q0') , eval('colNumberOfData.'+args.c+'Q1') ,\
                            eval('colNumberOfData.'+args.c+'Q2') , eval('colNumberOfData.'+args.c+'Q3') , eval('colNumberOfData.'+args.c+'Q4')  ]
    currentRowCount = 0
    
    levelOfDataAvailable = 4
    for dataRow in dataFile.matrix:
        qSum = 0
        totalPrice = 0
        totalPriceAtThisLevel = 0
        i = 0
        qtyForCalculatingWeightedAverage = float(dataRow[colNumberOfAttribute])
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
        attribute.aList[currentRowCount][1] = float(totalPrice)/qtyForCalculatingWeightedAverage
        attribute.aList[currentRowCount][2] = qtyForCalculatingWeightedAverage
        attribute.aList[currentRowCount][3] = totalPrice
        
        currentRowCount += 1
        if (currentRowCount%10000==0):
            print "Processed row number " + str(currentRowCount)
    
    lNameOfFeaturePrinted = "fWAPriceOfCol" + args.c + "InLast" + str(args.n) + "Qty"
    return ["TimeStamp",lNameOfFeaturePrinted,"QtyUsedForCalWtAvg","TotalPriceCalculatedAtCurrRow"]

