import dataFile
import colNumberOfData
import feature
import common
import fGenArgs
import math

def extractFeatureFromDataMatrix():
   if fGenArgs.args.n == None:
      N = 5
   else:
      N = int(fGenArgs.args.n) 
   
   try:
      fGenArgs.args.c
   except:
      print "Since -c has not been specified I cannot proceed"
      os._exit()

   currentRowCount = 0

   
   eParam = math.pow((.5),(1.0 / N))

   for dataRow in dataFile.matrix:

      codeString = 'float(dataFile.matrix[currentRowCount][colNumberOfData.'+ fGenArgs.args.c + '])'
      cellValue = eval(codeString)

      if currentRowCount == 0:
         feature.vector[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount])
         feature.vector[currentRowCount][1] = cellValue
         currentRowCount = currentRowCount + 1
         continue

      feature.vector[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount])
      firstPart = float(feature.vector[currentRowCount - 1][1]) * eParam
      secondPart = (1- eParam) * cellValue
      feature.vector[currentRowCount][1] = firstPart + secondPart 

      currentRowCount = currentRowCount + 1

      if (currentRowCount%10000==0):
         print "Processed row number " + str(currentRowCount)

