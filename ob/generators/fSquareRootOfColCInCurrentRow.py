import sys, dataFile,os, colNumberOfData, attribute, common
from collections import deque
from math import sqrt
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
    if(args.cType == "synthetic"):
        colNumberOfAttribute = colNumberOfData.SysFeature
    else:
        colNumberOfAttribute = eval("colNumberOfData."+ args.c )
    
    colNumberOfTimeStamp = colNumberOfData.TimeStamp
    currentRowNumber = 0 
    for dataRow in dataFile.matrix:
        cellValue = float(dataRow[colNumberOfAttribute])
        attribute.aList[currentRowNumber][0] = common.convertTimeStampFromStringToDecimal(dataRow[colNumberOfTimeStamp])
        attribute.aList[currentRowNumber][1] = sqrt(cellValue) # in 1st iteration currentRowNumber = 0
        currentRowNumber += 1
        if currentRowNumber%10000 == 0:
            print "Processed row number " + str(currentRowNumber)
    
    lNameOfFeaturePrinted = "fSquareRootOfCol" + args.c + "InCurrentRow"
    return [ "TimeStamp", lNameOfFeaturePrinted , "Zero1" , "Zero2"]

