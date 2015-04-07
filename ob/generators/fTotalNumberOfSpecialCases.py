""" author = VK """
import dataFile
import colNumberOfData
import attribute
import common
from math import fabs

def extractAttributeFromDataMatrix(args):
    
    colNumberOfTimeStamp = colNumberOfData.TimeStamp
    currentRowCount = 0
    lPipSize = int(args.tickSize)
    colOfCurrentBid = colNumberOfData.BestBidP
    colOfCurrentAsk = colNumberOfData.BestAskP
    
    currentAsk = 0
    previousAsk = 0
    currentBid = 0
    previousBid = 0
    bidSideCases = 0
    askSideCases = 0
    bidSideFlag = 0
    askSideFlag = 0
    lAskSideAskP = 0
    lAskSideBidP = 0
    lBidSideAskP = 0
    lBidSideBidP = 0
    for dataRow in dataFile.matrix:
        
        attribute.aList[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount],colNumberOfTimeStamp)
        
        currentBid = float(dataFile.matrix[currentRowCount][colOfCurrentBid])
        currentAsk = float(dataFile.matrix[currentRowCount][colOfCurrentAsk])
        
        if (lAskSideAskP!=currentAsk and askSideFlag==1) or (lAskSideBidP!=currentBid and askSideFlag==1):
            askSideFlag = 0
        if (lBidSideAskP!=currentAsk and askSideFlag==1) or (lBidSideBidP!=currentBid and bidSideFlag==1):
            bidSideFlag = 0
        if (currentAsk - currentBid) == lPipSize  :
            if (previousAsk-currentAsk)>lPipSize or askSideFlag==1 :
                askSideCases += 1
                askSideFlag = 1
                lAskSideAskP = currentAsk
                lAskSideBidP = currentBid
                
            if (currentBid-previousBid)>lPipSize or bidSideFlag==1 :
                bidSideCases += 1
                bidSideFlag = 1
                lBidSideAskP = currentAsk
                lBidSideBidP = currentBid
                
                
        attribute.aList[currentRowCount][1] = askSideFlag
        attribute.aList[currentRowCount][2] = bidSideFlag
        attribute.aList[currentRowCount][3] = ";".join(map(str,[currentBid,currentAsk,previousBid,previousAsk]))
        
        currentRowCount = currentRowCount + 1
#         if(currentRowCount % 1000 == 0):
#             print "Processed row number " + str(currentRowCount)
        
        if previousBid==0 or  previousBid!=currentBid :
            previousBid = currentBid
            
        if previousAsk==0 or previousAsk!=currentAsk :
            previousAsk = currentAsk
            
    print "Number of bid side cases = " , bidSideCases , "Percentage of Bid side cases = " , (float(bidSideCases)/currentRowCount)*100
    print "Number of ask side cases = " , askSideCases , "Percentage of Ask side cases = " , (float(askSideCases)/currentRowCount)*100
    
    lNameOfFeaturePrinted = "BidSideCases"
    return ["TimeStamp",lNameOfFeaturePrinted,"AskSideCases","CurrentBid","CurrentAsk","PreviousBid","PreviousAsk"]
