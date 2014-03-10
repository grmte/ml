import dataFile
import colNumberOfData
import feature
import common

def extractFeatureFromDataMatrix():
   currentRowCount = 0
   for dataRow in dataFile.matrix:
      bidQ4OfCurrentRow = float(dataFile.matrix[currentRowCount][colNumberOfData.BidQ4])
      AskQ4OfCurrentRow = float(dataFile.matrix[currentRowCount][colNumberOfData.AskQ4])
      feature.vector[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount])
      feature.vector[currentRowCount][1] = float(bidQ4OfCurrentRow)/AskQ4OfCurrentRow
      currentRowCount = currentRowCount + 1
      if(currentRowCount % 1000 == 0):
         print "Processed row number " + str(currentRowCount)
