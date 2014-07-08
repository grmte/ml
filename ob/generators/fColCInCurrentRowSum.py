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
   list_of_array = [ eval('colNumberOfData.'+args.c+'0') , eval('colNumberOfData.'+args.c+'1') ,eval('colNumberOfData.'+args.c+'2') , eval('colNumberOfData.'+args.c+'3') , eval('colNumberOfData.'+args.c+'4')  ]
   for dataRow in dataFile.matrix:
      qSum = float(dataRow[list_of_array[0]]) + float(dataRow[list_of_array[1]]) + \
                      float(dataRow[list_of_array[2]]) + float(dataRow[list_of_array[3]]) + float(dataRow[list_of_array[4]])
      attribute.aList[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount],colNumberOfData.TimeStamp)
      attribute.aList[currentRowCount][1] = qSum
      currentRowCount = currentRowCount + 1
      if (currentRowCount%10000==0):
         print "Processed row number " + str(currentRowCount)

   lNameOfFeaturePrinted = "fCol" + args.c + "InCurrentRowSum"
   return ["TimeStamp",lNameOfFeaturePrinted,"Zero1","Zero2"]
