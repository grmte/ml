import os
import colNumberOfData
import dataFile

import attribute
import common
from collections import deque

def extractAttributeFromDataMatrix(args):
    if args.n is None:
        print "-n has not been specified"
        os._exit(-1)
    totalOfLastLTQQty = int(args.n)
    
    colNumberOfLTP = colNumberOfData.NiftyLTP
    colNumberOfTTQ = colNumberOfData.NiftyTTQ
    
    prev_ttq = 0
    ltq_ltp_list = []
    sum_ltq = 0
    prod_sum = 0
    currentRowCount = 0
    for dataRow in dataFile.matrix:
        
        ttq, ltp = (int(dataRow[colNumberOfTTQ]), float(dataRow[colNumberOfLTP]))
        
        attribute.aList[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount],colNumberOfData.TimeStamp)
        if ttq > prev_ttq:
            ltq = ttq - prev_ttq
            ltq_ltp_list.append([ltq, ltp])
            prod_sum += ltq * ltp
            sum_ltq += ltq
            if sum_ltq > totalOfLastLTQQty:
                
                index = 0
                while sum_ltq <> totalOfLastLTQQty:
                     if ltq_ltp_list[index][0] > sum_ltq - totalOfLastLTQQty:
                         ltq_ltp_list[index][0] -= sum_ltq - totalOfLastLTQQty
                         prod_sum -= (sum_ltq - totalOfLastLTQQty) * ltq_ltp_list[index][1]
                         sum_ltq = totalOfLastLTQQty
                         
                     else:
                         sum_ltq -= ltq_ltp_list[index][0]
                         prod_sum -= (ltq_ltp_list[index][0] * ltq_ltp_list[index][1])
                         ltq_ltp_list = ltq_ltp_list[1:]
                
        wtd_ltp = prod_sum / (max(sum_ltq,1))
        prev_ttq = ttq
        
        attribute.aList[currentRowCount][1] = max(wtd_ltp, 1)
        currentRowCount = currentRowCount + 1
        if(currentRowCount % 1000 == 0):
           print "Processed row number " + str(currentRowCount) 

    lNameOfFeature = "fWALTPInLast" + str(args.n) + "Qty" 
    return ["TimeStamp",lNameOfFeature,"0", "1"]
