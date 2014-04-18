import dataFile
import colNumberOfData
import attribute
import common

import math

def extractAttributeFromDataMatrix(args):
   if args.n == None:
      N = 5
   else:
      N = int(args.n) 
   
   try:
      args.c
   except:
      print "Since -c has not been specified I cannot proceed"
      os._exit()

   currentRowCount = 0

   
   eParam = math.pow((.5),(1.0 / N))

   for dataRow in dataFile.matrix:

      codeString = 'float(dataFile.matrix[currentRowCount][colNumberOfData.'+ args.c + '])'
      cellValue = eval(codeString)

      if currentRowCount == 0:
         attribute.aList[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount])
         attribute.aList[currentRowCount][1] = cellValue
         currentRowCount = currentRowCount + 1
         continue

      attribute.aList[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount])
      firstPart = float(attribute.aList[currentRowCount - 1][1]) * eParam
      secondPart = (1- eParam) * cellValue
      attribute.aList[currentRowCount][1] = firstPart + secondPart 

      currentRowCount = currentRowCount + 1

      if (currentRowCount%10000==0):
         print "Processed row number " + str(currentRowCount)

