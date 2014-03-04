import dataFile
import colNumberOfData
import feature

def extractFeatureFromDataMatrix():
   currentRowCount = 0
   for dataRow in dataFile.matrix:
      LTPOfCurrentRow = float(dataFile.matrix[currentRowCount][colNumberOfData.LTP])
      feature.vector[currentRowCount][0] = dataFile.matrix[currentRowCount][colNumberOfData.TimeStamp]
      feature.vector[currentRowCount][1] = LTPOfCurrentRow
      currentRowCount = currentRowCount + 1
      print "Processed row number " + str(currentRowCount)
