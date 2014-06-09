"""
Some e.g features that can be generated with this are:
1. fColBidQInCurrentRowSum
2. fColAskQInCurrentRowSum
3. fColAskPInCurrentRowSum
4. fColBidPInCurrentRowSum
"""

import dataFile
import colNumberOfData
import attribute
import common


def extractAttributeFromDataMatrix(args):
   currentRowCount = 0
   for dataRow in dataFile.matrix:
      codeString = 'float(dataFile.matrix[currentRowCount][colNumberOfData.'+args.c+'0])+float(dataFile.matrix[currentRowCount][colNumberOfData.'+args.c+'1])+float(dataFile.matrix[currentRowCount][colNumberOfData.'+args.c+'2])+float(dataFile.matrix[currentRowCount][colNumberOfData.'+args.c+'3])+float(dataFile.matrix[currentRowCount][colNumberOfData.'+args.c+'4])'
      qSum = eval(codeString)
      attribute.aList[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount],colNumberOfData.TimeStamp)
      attribute.aList[currentRowCount][1] = qSum
      currentRowCount = currentRowCount + 1
      if (currentRowCount%10000==0):
         print "Processed row number " + str(currentRowCount)

   lNameOfFeaturePrinted = "fCol" + args.c + "InCurrentRowSum"
   return ["TimeStamp",lNameOfFeaturePrinted,"Zero1","Zero2"]
