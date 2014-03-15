""" author = VK """
import dataFile
import colNumberOfData
import feature
import common
import fGenArgs

def extractFeatureFromDataMatrix():

   try:
      fGenArgs.args.c
   except:
      print "Since -c has not been specified I cannot proceed"
      os._exit()


   currentRowCount = 0
   for dataRow in dataFile.matrix:
      codeString = "float(dataFile.matrix[currentRowCount][colNumberOfData."+fGenArgs.args.c+"])"

      feature.vector[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount])

      feature.vector[currentRowCount][1] = eval(codeString)
      currentRowCount = currentRowCount + 1
      if(currentRowCount % 1000 == 0):
         print "Processed row number " + str(currentRowCount)
