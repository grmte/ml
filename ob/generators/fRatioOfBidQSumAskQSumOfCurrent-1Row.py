import dataFile
import colNumberOfData
import feature
import common

def extractFeatureFromDataMatrix():
   currentRowCount = 0
   for dataRow in dataFile.matrix:

      if (currentRowCount == 0):
         currentRowCount = currentRowCount + 1
         continue     # Since we are going back 1 row from current we cannot get data from current row
      
      BidQSum = float(dataFile.matrix[currentRowCount - 1][colNumberOfData.BidQ0])+float(dataFile.matrix[currentRowCount - 1][colNumberOfData.BidQ1])+float(dataFile.matrix[currentRowCount - 1][colNumberOfData.BidQ2])+float(dataFile.matrix[currentRowCount - 1][colNumberOfData.BidQ3])+float(dataFile.matrix[currentRowCount - 1][colNumberOfData.BidQ4])
      AskQSum = float(dataFile.matrix[currentRowCount - 1][colNumberOfData.AskQ0])+float(dataFile.matrix[currentRowCount - 1][colNumberOfData.AskQ1])+float(dataFile.matrix[currentRowCount - 1][colNumberOfData.AskQ2])+float(dataFile.matrix[currentRowCount - 1][colNumberOfData.AskQ3])+float(dataFile.matrix[currentRowCount - 1][colNumberOfData.AskQ4])
      feature.vector[currentRowCount - 1][0] = common.getTimeStamp(dataFile.matrix[currentRowCount - 1])
      feature.vector[currentRowCount - 1][1] = float(BidQSum)/AskQSum

      currentRowCount = currentRowCount + 1

      if (currentRowCount%10000==0):
         print "Processed row number " + str(currentRowCount)

