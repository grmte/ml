"""
This will generate features like:
1. fMovingAverageOfColAskP0InLast100Rows

"""
import dataFile
import colNumberOfData
import attribute
import common

from collections import deque

UpperCutoff = 4.0
LowerCutOff = 0.25
MidCutOff = 1.0

UpperValue = 1
MidValue = 0
LowerValue = -1

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
      currentTickValue = float(dataFile.matrix[currentRowCount][colNumberOfAttribute])
      attribute.aList[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount],colNumberOfTimeStamp,args.cType)
      if currentTickValue >= UpperCutoff:
          attribute.aList[currentRowCount][1] = UpperValue
      elif currentTickValue <= LowerCutOff:
          attribute.aList[currentRowCount][1] = LowerValue
      else:
          if currentRowCount == 0:
             attribute.aList[currentRowCount][1] = MidValue
          elif attribute.aList[currentRowCount-1][1] == LowerValue :
              if currentTickValue <= MidCutOff:
                 attribute.aList[currentRowCount][1] = LowerValue
              else:
                 attribute.aList[currentRowCount][1] = MidValue
          elif attribute.aList[currentRowCount-1][1] == UpperValue:
              if currentTickValue >= MidCutOff:
                 attribute.aList[currentRowCount][1] = UpperValue
              else:
                 attribute.aList[currentRowCount][1] = MidValue
          else:
              attribute.aList[currentRowCount][1] = MidValue    
      currentRowCount = currentRowCount + 1
      if (currentRowCount%10000==0):
         print "Processed row number " + str(currentRowCount)

   lNameOfFeaturePrinted = "fMovingAverageOfCol" + args.c + "InLast" + str(args.n) + "Rows"
   return ["TimeStamp",lNameOfFeaturePrinted,"Zero1","Zero2"]
