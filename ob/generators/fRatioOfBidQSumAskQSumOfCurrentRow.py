
import dataFile
import colNumberOfData
import feature
import common

def extractFeatureFromDataMatrix():
   currentRowCount = 0
   for dataRow in dataFile.matrix:
      print "Processed row number " + str(currentRowCount)
      BidQSum = float(dataFile.matrix[currentRowCount][colNumberOfData.BidQ0])+float(dataFile.matrix[currentRowCount][colNumberOfData.BidQ1])+float(dataFile.matrix[currentRowCount][colNumberOfData.BidQ2])+float(dataFile.matrix[currentRowCount][colNumberOfData.BidQ3])+float(dataFile.matrix[currentRowCount][colNumberOfData.BidQ4])
      AskQSum = float(dataFile.matrix[currentRowCount][colNumberOfData.AskQ0])+float(dataFile.matrix[currentRowCount][colNumberOfData.AskQ1])+float(dataFile.matrix[currentRowCount][colNumberOfData.AskQ2])+float(dataFile.matrix[currentRowCount][colNumberOfData.AskQ3])+float(dataFile.matrix[currentRowCount][colNumberOfData.AskQ4])
      feature.vector[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount])
      feature.vector[currentRowCount][1] = float(BidQSum)/AskQSum
      currentRowCount = currentRowCount + 1
#      if (currentRowCount%10000==0):

