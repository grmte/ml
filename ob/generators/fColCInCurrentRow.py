""" author = VK """
import dataFile
import colNumberOfData
import attribute
import common

def extractAttributeFromDataMatrix(args):
   currentRowCount = 0
   for dataRow in dataFile.matrix:
      codeString = "float(dataFile.matrix[currentRowCount][colNumberOfData."+args.c+"])"

      attribute.aList[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount])

      attribute.aList[currentRowCount][1] = eval(codeString)
      currentRowCount = currentRowCount + 1
      if(currentRowCount % 1000 == 0):
         print "Processed row number " + str(currentRowCount)
