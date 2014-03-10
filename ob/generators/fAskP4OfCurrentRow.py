""" author = VK """
import dataFile
import colNumberOfData
import feature
import common

def extractFeatureFromDataMatrix():
   currentRowCount = 0
   for dataRow in dataFile.matrix:
      askP4OfCurrentRow = float(dataFile.matrix[currentRowCount][colNumberOfData.AskP4])
      feature.vector[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount])
      feature.vector[currentRowCount][1] = askP4OfCurrentRow
      currentRowCount = currentRowCount + 1
      if(currentRowCount % 1000 == 0):
         print "Processed row number " + str(currentRowCount)
