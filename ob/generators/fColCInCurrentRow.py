""" author = VK """
import dataFile
import colNumberOfData
import attribute
import common

def extractAttributeFromDataMatrix(args):
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
    currentRowCount = 0
    for dataRow in dataFile.matrix:
        
        attribute.aList[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount],colNumberOfTimeStamp)
        
        attribute.aList[currentRowCount][1] = float(dataFile.matrix[currentRowCount][colNumberOfAttribute])
        currentRowCount = currentRowCount + 1
        if(currentRowCount % 1000 == 0):
            print "Processed row number " + str(currentRowCount)
    
    lNameOfFeaturePrinted = "fCol" + args.c + "InCurrentRow"
    return ["TimeStamp",lNameOfFeaturePrinted,"Zero1","Zero2"]
