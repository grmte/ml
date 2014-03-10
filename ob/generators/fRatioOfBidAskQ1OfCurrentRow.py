import dataFile
import colNumberOfData
import feature
import common

def extractFeatureFromDataMatrix():
   currentRowCount = 0
   for dataRow in dataFile.matrix:
      bidQ1OfCurrentRow = float(dataFile.matrix[currentRowCount][colNumberOfData.BidQ1])
      AskQ1OfCurrentRow = float(dataFile.matrix[currentRowCount][colNumberOfData.AskQ1])
      feature.vector[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount])
      feature.vector[currentRowCount][1] = float(bidQ1OfCurrentRow)/AskQ1OfCurrentRow
      currentRowCount = currentRowCount + 1
      print "Processed row number " + str(currentRowCount)
