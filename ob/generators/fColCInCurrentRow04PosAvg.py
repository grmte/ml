
import dataFile
import colNumberOfData
import attribute
import common


def extractAttributeFromDataMatrix(args):
    currentRowCount = 0
    list_of_array = [ eval('colNumberOfData.'+args.c+'0') , eval('colNumberOfData.'+args.c+'4')  ]
    for dataRow in dataFile.matrix:
        qSum = float(dataRow[list_of_array[0]]) + float(dataRow[list_of_array[1]])
        qAverage = qSum / 2
        attribute.aList[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount],colNumberOfData.TimeStamp)
        attribute.aList[currentRowCount][1] = qAverage
        currentRowCount = currentRowCount + 1
        if (currentRowCount%10000==0):
            print "Processed row number " + str(currentRowCount)
    
    lNameOfFeaturePrinted = "fCol" + args.c + "InCurrentRowAvg"
    return ["TimeStamp",lNameOfFeaturePrinted,"Zero1","Zero2"]
