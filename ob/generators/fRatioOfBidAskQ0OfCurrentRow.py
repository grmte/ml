import dataFile
import colNumberOfData
import feature
import common

def extractFeatureFromDataMatrix():
   currentRowCount = 0
   for dataRow in dataFile.matrix:
      bidQ0OfCurrentRow = float(dataFile.matrix[currentRowCount][colNumberOfData.BidQ0])
      AskQ0OfCurrentRow = float(dataFile.matrix[currentRowCount][colNumberOfData.AskQ0])
      feature.vector[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount])
      feature.vector[currentRowCount][1] = float(bidQ0OfCurrentRow)/AskQ0OfCurrentRow
      currentRowCount = currentRowCount + 1
      if(currentRowCount % 1000 == 0):
         print "Processed row number " + str(currentRowCount)
