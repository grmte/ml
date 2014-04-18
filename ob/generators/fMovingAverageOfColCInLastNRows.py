"""
This will generate features like:
1. fMovingAverageOfColAskP0InLast100Rows

"""
import dataFile
import colNumberOfData
import attribute
import common

from collections import deque

def extractAttributeFromDataMatrix(args):
   queueOfCellValueInLastNRows = deque()
   totalOfLastNRows = 0.0
   
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

   if(args.cType == "synthetic"):
      colNumberOfAttribute = 1
      colNumberOfTimeStamp = 0
   else:
      colNumberOfAttribute = eval("colNumberOfData."+ args.c )
      colNumberOfTimeStamp = colNumberOfData.TimeStamp

   for dataRow in dataFile.matrix:
      cellValue = float(dataFile.matrix[currentRowCount][colNumberOfAttribute])
      queueOfCellValueInLastNRows.append(cellValue)
      totalOfLastNRows += cellValue

      if (currentRowCount < N):
         attribute.aList[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount],colNumberOfTimeStamp,args.cType)
         attribute.aList[currentRowCount][1] = totalOfLastNRows/(currentRowCount+1) # in 1st iteration currentRowCount = 0
         currentRowCount = currentRowCount + 1
         continue     # Since we are going back 1 row from current we cannot get data from current row
      

      totalOfLastNRows -= queueOfCellValueInLastNRows.popleft()
     
      # In the next 2 rows we do not do -1 since this feature if for the current row.
      attribute.aList[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount],colNumberOfTimeStamp,args.cType)
      attribute.aList[currentRowCount][1] = totalOfLastNRows / N

      currentRowCount = currentRowCount + 1

      if (currentRowCount%10000==0):
         print "Processed row number " + str(currentRowCount)

