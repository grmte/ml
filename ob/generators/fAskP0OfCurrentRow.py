""" author = VK """
import dataFile
import colNumberOfData
import feature
import common

def extractFeatureFromDataMatrix():
   currentRowCount = 0
   for dataRow in dataFile.matrix:
      askP0OfCurrentRow = float(dataFile.matrix[currentRowCount][colNumberOfData.AskP0])

      feature.vector[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount])

      feature.vector[currentRowCount][1] = askP0OfCurrentRow
      currentRowCount = currentRowCount + 1
      if(currentRowCount % 1000 == 0):
         print "Processed row number " + str(currentRowCount)
