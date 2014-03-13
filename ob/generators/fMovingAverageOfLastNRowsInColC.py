import dataFile
import colNumberOfData
import feature
import common
import fGenArgs

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
   for dataRow in dataFile.matrix:

      if (currentRowCount < N):
         feature.vector[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount])
         feature.vector[currentRowCount][1] = 0 # TODO: Figure out how to put NA here.
         currentRowCount = currentRowCount + 1
         continue     # Since we are going back 1 row from current we cannot get data from current row
      
      ColSum = 0
      i = 0
      while i < N:
         ColSum = eval(codeString)
         i = i+1

      # In the next 2 rows we do not do -1 since this feature if for the current row.
      feature.vector[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount])
      feature.vector[currentRowCount][1] = float(ColSum)/ N

      currentRowCount = currentRowCount + 1

      if (currentRowCount%10000==0):
         print "Processed row number " + str(currentRowCount)

