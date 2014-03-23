import dataFile
import colNumberOfData
import attribute
import common
import aGenArgs
import math

def extractAttributeFromDataMatrix():
   if aGenArgs.args.n == None:
      N = 5
   else:
      N = int(aGenArgs.args.n) 
   
   try:
      aGenArgs.args.c
   except:
      print "Since -c has not been specified I cannot proceed"
      os._exit()

   currentRowCount = 0

   
   eParam = math.pow((.5),(1.0 / N))

   for dataRow in dataFile.matrix:

      codeString = 'float(dataFile.matrix[currentRowCount][colNumberOfData.'+ aGenArgs.args.c + '])'
      cellValue = eval(codeString)

      if currentRowCount == 0:
         attribute.list[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount])
         attribute.list[currentRowCount][1] = cellValue
         currentRowCount = currentRowCount + 1
         continue

      attribute.list[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount])
      firstPart = float(attribute.list[currentRowCount - 1][1]) * eParam
      secondPart = (1- eParam) * cellValue
      attribute.list[currentRowCount][1] = firstPart + secondPart 

      currentRowCount = currentRowCount + 1

      if (currentRowCount%10000==0):
         print "Processed row number " + str(currentRowCount)

