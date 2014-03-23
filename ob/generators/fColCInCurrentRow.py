""" author = VK """
import dataFile
import colNumberOfData
import attribute
import common
import aGenArgs

def extractAttributeFromDataMatrix():

   try:
      aGenArgs.args.c
   except:
      print "Since -c has not been specified I cannot proceed"
      os._exit()


   currentRowCount = 0
   for dataRow in dataFile.matrix:
      codeString = "float(dataFile.matrix[currentRowCount][colNumberOfData."+aGenArgs.args.c+"])"

      attribute.list[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount])

      attribute.list[currentRowCount][1] = eval(codeString)
      currentRowCount = currentRowCount + 1
      if(currentRowCount % 1000 == 0):
         print "Processed row number " + str(currentRowCount)
