import dataFile
import colNumberOfData
import feature
import common
import fGenArgs
import math
from decimal import *

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

   
   codeString = 'float(dataFile.matrix[currentRowCount - i][colNumberOfData.'+ fGenArgs.args.c + ']) + ColSum'


   #eParam = Decimal(math.pow(Decimal(.5),Decimal(1 / N))) TODO
   eParam = .99861

   for dataRow in dataFile.matrix:

      if currentRowCount == 0:
         feature.vector[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount])
         feature.vector[currentRowCount][1] = dataFile.matrix[currentRowCount][colNumberOfData.BidP0]
         currentRowCount = currentRowCount + 1
         continue

      feature.vector[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount])
      firstPart = float(feature.vector[currentRowCount - 1][1]) * eParam
      secondPart = (1- eParam) * float(dataFile.matrix[currentRowCount][colNumberOfData.BidP0])
      feature.vector[currentRowCount][1] = firstPart + secondPart 

      currentRowCount = currentRowCount + 1

      if (currentRowCount%10000==0):
         print "Processed row number " + str(currentRowCount)

