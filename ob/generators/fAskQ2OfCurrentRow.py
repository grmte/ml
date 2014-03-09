import dataFile
import colNumberOfData
import feature

def extractFeatureFromDataMatrix():
   currentRowCount = 0
   for dataRow in dataFile.matrix:
      askQ2OfCurrentRow = float(dataFile.matrix[currentRowCount][colNumberOfData.AskQ2])
      feature.vector[currentRowCount][0] = dataFile.matrix[currentRowCount][colNumberOfData.TimeStamp]
      feature.vector[currentRowCount][1] = askQ2OfCurrentRow
      currentRowCount = currentRowCount + 1
      print "Processed row number " + str(currentRowCount)
