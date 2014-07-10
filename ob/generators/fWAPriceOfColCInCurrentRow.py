"""
Some e.g features that can be generated with this are:
1. fColBidQInCurrentRowSum
2. fColAskQInCurrentRowSum
3. fColAskPInCurrentRowSum
4. fColBidPInCurrentRowSum
"""

import dataFile
import colNumberOfData
import attribute
import common


def extractAttributeFromDataMatrix(args):
    currentRowCount = 0
    list_of_price_array = [ eval('colNumberOfData.'+args.c+'P0') , eval('colNumberOfData.'+args.c+'P1') ,\
                           eval('colNumberOfData.'+args.c+'P2') , eval('colNumberOfData.'+args.c+'P3') , eval('colNumberOfData.'+args.c+'P4')  ]
    list_of_qty_array = [ eval('colNumberOfData.'+args.c+'Q0') , eval('colNumberOfData.'+args.c+'Q1') ,\
                           eval('colNumberOfData.'+args.c+'Q2') , eval('colNumberOfData.'+args.c+'Q3') , eval('colNumberOfData.'+args.c+'Q4')  ]
    for dataRow in dataFile.matrix:
        qPriceSum = 0.0
        qQtySum = 0
        for i in range(5):
            qPriceSum += int(dataRow[list_of_qty_array[i]]) * float(dataRow[list_of_price_array[i]])
            qQtySum += int(dataRow[list_of_qty_array[i]])
        qAverage = qPriceSum / qQtySum
        attribute.aList[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount],colNumberOfData.TimeStamp)
        attribute.aList[currentRowCount][1] = qAverage
        currentRowCount = currentRowCount + 1
        if (currentRowCount%10000==0):
            print "Processed row number " + str(currentRowCount)
    
    lNameOfFeaturePrinted = "fCol" + args.c + "InCurrentRowAvg"
    return ["TimeStamp",lNameOfFeaturePrinted,"Zero1","Zero2"]
