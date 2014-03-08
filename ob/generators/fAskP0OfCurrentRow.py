import dataFile
import colNumberOfData
import feature

def extractFeatureFromDataMatrix():
   currentRowCount = 0
   for dataRow in dataFile.matrix:
      bidP0OfCurrentRow = float(dataFile.matrix[currentRowCount][colNumberOfData.AskP0])
      feature.vector[currentRowCount][0] = dataFile.matrix[currentRowCount][colNumberOfData.TimeStamp]
      feature.vector[currentRowCount][1] = bidP0OfCurrentRow
      currentRowCount = currentRowCount + 1
      print "Processed row number " + str(currentRowCount)
