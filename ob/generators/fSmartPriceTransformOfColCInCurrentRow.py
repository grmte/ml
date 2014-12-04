import sys, dataFile, colNumberOfData, attribute, common

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
    colNumberOfExchangeStamp = colNumberOfData.ExchangeTS
        
    currentRowNumberForWhichFeatureValueIsBeingCalculated = 0
    for dataRow in dataFile.matrix:
        lSmartFeatureValue = float(dataRow[colNumberOfAttribute])
        lAskP0 = float(colNumberOfAttribute.AskP0)
        lBidP0 = float(colNumberOfAttribute.BidP0)
        lMidPrice = (lAskP0+lBidP0) / 2
        
        if lSmartFeatureValue > lMidPrice:
            lSmartFeatureValueTransform = -lSmartFeatureValue / lAskP0
        else:
            lSmartFeatureValueTransform = lBidP0 / lSmartFeatureValue
        attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][0] = common.convertTimeStampFromStringToDecimal(dataRow[colNumberOfTimeStamp],args.cType)
        attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][1] = lSmartFeatureValueTransform
        attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][2] = lAskP0
        attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][3] = str(lBidP0) + ";" + str(lSmartFeatureValue)
        currentRowNumberForWhichFeatureValueIsBeingCalculated += 1
        if (currentRowNumberForWhichFeatureValueIsBeingCalculated%10000==0):
            print "Processed row number " + str(currentRowNumberForWhichFeatureValueIsBeingCalculated)

    lNameOfFeaturePrinted = "fSmartPriceTransformOfCol" + args.c + "InCurrentRow"
    return [ "TimeStamp", lNameOfFeaturePrinted , "AskP0" , "BidP0" , "lPreviussmartPrice" ]
         
