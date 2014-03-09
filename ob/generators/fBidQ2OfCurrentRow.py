import dataFile
import colNumberOfData
import feature
import common

def extractFeatureFromDataMatrix():
   currentRowCount = 0
   for dataRow in dataFile.matrix:
      bidQ2OfCurrentRow = float(dataFile.matrix[currentRowCount][colNumberOfData.BidQ2])
      feature.vector[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount])
      feature.vector[currentRowCount][1] = bidQ2OfCurrentRow
      currentRowCount = currentRowCount + 1
      print "Processed row number " + str(currentRowCount)
