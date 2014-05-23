"""
This will generate features like:
1. fOBAvgHistPriceOfColAskP0InLast100Rows

"""
import dataFile
import colNumberOfData
import attribute
import common

from collections import deque

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#Doc:Calculate Historical Weighted Ask
def calculate_historical_weighted_Ask():
    global g_filtered_object_list, g_no_of_ticks_tobe_considered, g_weight_list
    print "\nCalculate historical weighted Ask prices ....."
    
    l_index = g_no_of_ticks_tobe_considered -1
    while l_index < len(g_filtered_object_list):
        
        l_prev_index = l_index - 1
        l_window = 1
        l_flag_for_AskQ0 = False
        l_flag_for_AskQ1 = False
        l_flag_for_AskQ2 = False
        l_flag_for_AskQ3 = False
        l_flag_for_AskQ4 = False
        
        l_corresponding_AskQ0 = 0
        l_corresponding_AskQ1 = 0
        l_corresponding_AskQ2 = 0
        l_corresponding_AskQ3 = 0
        l_corresponding_AskQ4 = 0
        
        if (g_filtered_object_list[l_index - 1].AskP0 == g_filtered_object_list[l_index].AskP0) and (g_filtered_object_list[l_index - 1].AskP1 == g_filtered_object_list[l_index].AskP1) and \
        (g_filtered_object_list[l_index - 1].AskP2 == g_filtered_object_list[l_index].AskP2) and (g_filtered_object_list[l_index - 1].AskP3 == g_filtered_object_list[l_index].AskP3) and \
        (g_filtered_object_list[l_index - 1].AskP4 == g_filtered_object_list[l_index].AskP4) and l_index <> g_no_of_ticks_tobe_considered -1:
            g_filtered_object_list[l_index].sum_qty_for_avg_cal_Ask += (g_filtered_object_list[l_index - 1].sum_qty_for_avg_cal_Ask)
            g_filtered_object_list[l_index].window_Ask = g_filtered_object_list[l_index - 1].window_Ask + 1
        else:
            while True:   
                if (g_filtered_object_list[l_index].AskP1 >= g_filtered_object_list[l_prev_index].AskP0 and g_filtered_object_list[l_index].AskP3 <= g_filtered_object_list[l_prev_index].AskP4):
                    l_window += 1
                    
                    if l_flag_for_AskQ0 == False:
                        if g_filtered_object_list[l_index].AskP0 in g_filtered_object_list[l_prev_index].AskP_list:
                            l_index_for_AskP0 = g_filtered_object_list[l_prev_index].AskP_list.index(g_filtered_object_list[l_index].AskP0)
                            l_corresponding_AskQ0 = g_filtered_object_list[l_prev_index].AskQ_list[l_index_for_AskP0]
                            if l_corresponding_AskQ0 == 0:
                                l_index_for_AskP0 = g_filtered_object_list[l_prev_index + 1].AskP_list.index(g_filtered_object_list[l_index].AskP0)
                                l_corresponding_AskQ0 = g_filtered_object_list[l_prev_index + 1].AskQ_list[l_index_for_AskP0]
                                l_flag_for_AskQ0 = True
                        else:
                            if (l_index - l_prev_index) == 1:
                                l_corresponding_AskQ0 = g_filtered_object_list[l_index].AskQ0
                            l_flag_for_AskQ0 = True
                                
                    if l_flag_for_AskQ1 == False:
                        if g_filtered_object_list[l_index].AskP1 in g_filtered_object_list[l_prev_index].AskP_list:
                            l_index_for_AskP1 = g_filtered_object_list[l_prev_index].AskP_list.index(g_filtered_object_list[l_index].AskP1)
                            l_corresponding_AskQ1 = g_filtered_object_list[l_prev_index].AskQ_list[l_index_for_AskP1]
                            if l_corresponding_AskQ1 == 0:
                                l_index_for_AskP1 = g_filtered_object_list[l_prev_index + 1].AskP_list.index(g_filtered_object_list[l_index].AskP1)
                                l_corresponding_AskQ1 = g_filtered_object_list[l_prev_index + 1].AskQ_list[l_index_for_AskP1]
                                l_flag_for_AskQ1 = True
                                
                        else:
                            if (l_index - l_prev_index) == 1:
                                l_corresponding_AskQ1 = g_filtered_object_list[l_index].AskQ1
                            l_flag_for_AskQ1 = True
                            
                    if l_flag_for_AskQ2 == False:
                        if g_filtered_object_list[l_index].AskP2 in g_filtered_object_list[l_prev_index].AskP_list:
                            l_index_for_AskP2 = g_filtered_object_list[l_prev_index].AskP_list.index(g_filtered_object_list[l_index].AskP2)
                            l_corresponding_AskQ2 = g_filtered_object_list[l_prev_index].AskQ_list[l_index_for_AskP2]
                            if l_corresponding_AskQ2 == 0:
                                l_index_for_AskP2 = g_filtered_object_list[l_prev_index + 1].AskP_list.index(g_filtered_object_list[l_index].AskP2)
                                l_corresponding_AskQ2 = g_filtered_object_list[l_prev_index + 1].AskQ_list[l_index_for_AskP2]
                                l_flag_for_AskQ2 = True
                        else:
                            if (l_index - l_prev_index) == 1:
                                l_corresponding_AskQ2 = g_filtered_object_list[l_index].AskQ2
                            l_flag_for_AskQ2 = True
                            
                    if l_flag_for_AskQ3 == False:
                        if g_filtered_object_list[l_index].AskP3 in g_filtered_object_list[l_prev_index].AskP_list:
                            l_index_for_AskP3 = g_filtered_object_list[l_prev_index].AskP_list.index(g_filtered_object_list[l_index].AskP3)
                            l_corresponding_AskQ3 = g_filtered_object_list[l_prev_index].AskQ_list[l_index_for_AskP3]
                            if l_corresponding_AskQ3 == 0:
                                l_index_for_AskP3 = g_filtered_object_list[l_prev_index + 1].AskP_list.index(g_filtered_object_list[l_index].AskP3)
                                l_corresponding_AskQ3 = g_filtered_object_list[l_prev_index + 1].AskQ_list[l_index_for_AskP3]
                                l_flag_for_AskQ3 = True
                        else:
                            if (l_index - l_prev_index) == 1:
                                l_corresponding_AskQ3 = g_filtered_object_list[l_index].AskQ3
                            l_flag_for_AskQ3 = True
                            
                    if l_flag_for_AskQ4 == False:
                        if g_filtered_object_list[l_index].AskP4 in g_filtered_object_list[l_prev_index].AskP_list:
                            l_index_for_AskP4 = g_filtered_object_list[l_prev_index].AskP_list.index(g_filtered_object_list[l_index].AskP4)
                            l_corresponding_AskQ4 = g_filtered_object_list[l_prev_index].AskQ_list[l_index_for_AskP4]
                            if l_corresponding_AskQ4 == 0:
                                l_index_for_AskP4 = g_filtered_object_list[l_prev_index + 1].AskP_list.index(g_filtered_object_list[l_index].AskP4)
                                l_corresponding_AskQ4 = g_filtered_object_list[l_prev_index + 1].AskQ_list[l_index_for_AskP4]
                                l_flag_for_AskQ4 = True
                        else:
                            if (l_index - l_prev_index) == 1:
                                l_corresponding_AskQ4 = g_filtered_object_list[l_index].AskQ4
                            l_flag_for_AskQ4 = True
                     
                    g_filtered_object_list[l_index].sum_qty_for_avg_cal_Ask += (g_weight_list[0] * l_corresponding_AskQ0) + (g_weight_list[1] * l_corresponding_AskQ1) + (g_weight_list[2] * l_corresponding_AskQ2)+ (g_weight_list[3] * l_corresponding_AskQ3) + (g_weight_list[4] * l_corresponding_AskQ4)
                else:
                    break
                
                l_prev_index -= 1
            
            g_filtered_object_list[l_index].window_Ask = l_window
        
        l_index += 1
    return

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#Doc:Calculate Historical Weighted Bid
def calculate_historical_weighted_Bid():
    global g_filtered_object_list, g_no_of_ticks_tobe_considered, g_weight_list
    print "\nCalculate historical weighted Bid prices ..."
    
    l_index = g_no_of_ticks_tobe_considered -1
    while l_index< len(g_filtered_object_list):
        l_prev_index = l_index - 1
        l_window = 1
        
        l_flag_for_BidQ0 = False
        l_flag_for_BidQ1 = False
        l_flag_for_BidQ2 = False
        l_flag_for_BidQ3 = False
        l_flag_for_BidQ4 = False
        
        l_corresponding_BidQ0 = 0
        l_corresponding_BidQ1 = 0
        l_corresponding_BidQ2 = 0
        l_corresponding_BidQ3 = 0
        l_corresponding_BidQ4 = 0
        
        if (g_filtered_object_list[l_index - 1].BidP0 == g_filtered_object_list[l_index].BidP0) and (g_filtered_object_list[l_index - 1].BidP1 == g_filtered_object_list[l_index].BidP1) and \
        (g_filtered_object_list[l_index - 1].BidP2 == g_filtered_object_list[l_index].BidP2) and (g_filtered_object_list[l_index - 1].BidP3 == g_filtered_object_list[l_index].BidP3) and \
        (g_filtered_object_list[l_index - 1].BidP4 == g_filtered_object_list[l_index].BidP4) and l_index <> g_no_of_ticks_tobe_considered -1:
            g_filtered_object_list[l_index].sum_qty_for_avg_cal_Bid += (g_filtered_object_list[l_index - 1].sum_qty_for_avg_cal_Bid)
            g_filtered_object_list[l_index].window_Bid = g_filtered_object_list[l_index - 1].window_Bid + 1
        
        else:
            while True:   
                if (g_filtered_object_list[l_index].BidP1 <= g_filtered_object_list[l_prev_index].BidP0 and g_filtered_object_list[l_index].BidP3 >= g_filtered_object_list[l_prev_index].BidP4):
                    l_window += 1
                            
                    if l_flag_for_BidQ0 == False:
                        if g_filtered_object_list[l_index].BidP0 in g_filtered_object_list[l_prev_index].BidP_list:
                            l_index_for_BidP0 = g_filtered_object_list[l_prev_index].BidP_list.index(g_filtered_object_list[l_index].BidP0)
                            l_corresponding_BidQ0 = g_filtered_object_list[l_prev_index].BidQ_list[l_index_for_BidP0]
                            if l_corresponding_BidQ0 == 0:
                                l_index_for_BidP0 = g_filtered_object_list[l_prev_index + 1].BidP_list.index(g_filtered_object_list[l_index].BidP0)
                                l_corresponding_BidQ0 = g_filtered_object_list[l_prev_index + 1].BidQ_list[l_index_for_BidP0]
                                l_flag_for_BidQ0 = True
                                
                        else:
                            if (l_index - l_prev_index) == 1:
                                l_corresponding_BidQ0 = g_filtered_object_list[l_index].BidQ0
                            l_flag_for_BidQ0 = True
                            
                    if l_flag_for_BidQ1 == False:
                        if g_filtered_object_list[l_index].BidP1 in g_filtered_object_list[l_prev_index].BidP_list:
                            l_index_for_BidP1 = g_filtered_object_list[l_prev_index].BidP_list.index(g_filtered_object_list[l_index].BidP1)
                            l_corresponding_BidQ1 = g_filtered_object_list[l_prev_index].BidQ_list[l_index_for_BidP1]
                            if l_corresponding_BidQ1 == 0:
                                l_index_for_BidP1 = g_filtered_object_list[l_prev_index + 1].BidP_list.index(g_filtered_object_list[l_index].BidP1)
                                l_corresponding_BidQ1 = g_filtered_object_list[l_prev_index + 1].BidQ_list[l_index_for_BidP1]
                                l_flag_for_BidQ1 = True
                                
                        else:
                            if (l_index - l_prev_index) == 1:
                                l_corresponding_BidQ1 = g_filtered_object_list[l_index].BidQ1
                            l_flag_for_BidQ1 = True
                            
                    if l_flag_for_BidQ2 == False:
                        if g_filtered_object_list[l_index].BidP2 in g_filtered_object_list[l_prev_index].BidP_list:
                            l_index_for_BidP2 = g_filtered_object_list[l_prev_index].BidP_list.index(g_filtered_object_list[l_index].BidP2)
                            l_corresponding_BidQ2 = g_filtered_object_list[l_prev_index].BidQ_list[l_index_for_BidP2]
                            if l_corresponding_BidQ2 == 0:
                                l_index_for_BidP2 = g_filtered_object_list[l_prev_index + 1].BidP_list.index(g_filtered_object_list[l_index].BidP2)
                                l_corresponding_BidQ2 = g_filtered_object_list[l_prev_index + 1].BidQ_list[l_index_for_BidP2]
                                l_flag_for_BidQ2 = True
                        else:
                            if (l_index - l_prev_index) == 1:
                                l_corresponding_BidQ2 = g_filtered_object_list[l_index].BidQ2
                            l_flag_for_BidQ2 = True
                            
                    if l_flag_for_BidQ3 == False:
                        if g_filtered_object_list[l_index].BidP3 in g_filtered_object_list[l_prev_index].BidP_list:
                            l_index_for_BidP3 = g_filtered_object_list[l_prev_index].BidP_list.index(g_filtered_object_list[l_index].BidP3)
                            l_corresponding_BidQ3 = g_filtered_object_list[l_prev_index].BidQ_list[l_index_for_BidP3]
                            if l_corresponding_BidQ3 == 0:
                                l_index_for_BidP3 = g_filtered_object_list[l_prev_index + 1].BidP_list.index(g_filtered_object_list[l_index].BidP3)
                                l_corresponding_BidQ3 = g_filtered_object_list[l_prev_index + 1].BidQ_list[l_index_for_BidP3]
                                l_flag_for_BidQ3 = True
                        else:
                            if (l_index - l_prev_index) == 1:
                                l_corresponding_BidQ3 = g_filtered_object_list[l_index].BidQ3
                            l_flag_for_BidQ3 = True
                            
                    if l_flag_for_BidQ4 == False:
                        if g_filtered_object_list[l_index].BidP4 in g_filtered_object_list[l_prev_index].BidP_list:
                            l_index_for_BidP4 = g_filtered_object_list[l_prev_index].BidP_list.index(g_filtered_object_list[l_index].BidP4)
                            l_corresponding_BidQ4 = g_filtered_object_list[l_prev_index].BidQ_list[l_index_for_BidP4]
                            if l_corresponding_BidQ4 == 0:
                                l_index_for_BidP4 = g_filtered_object_list[l_prev_index + 1].BidP_list.index(g_filtered_object_list[l_index].BidP4)
                                l_corresponding_BidQ4 = g_filtered_object_list[l_prev_index + 1].BidQ_list[l_index_for_BidP4]
                                l_flag_for_BidQ4 = True
                        else:
                            if (l_index - l_prev_index) == 1:
                                l_corresponding_BidQ4 = g_filtered_object_list[l_index].BidQ4
                            l_flag_for_BidQ4 = True
    
                    g_filtered_object_list[l_index].sum_qty_for_avg_cal_Bid += (g_weight_list[0] * l_corresponding_BidQ0) + (g_weight_list[1] * l_corresponding_BidQ1) + (g_weight_list[2] * l_corresponding_BidQ2)+ (g_weight_list[3] * l_corresponding_BidQ3) + (g_weight_list[4] * l_corresponding_BidQ4)
    
                else:
                    break
                l_prev_index -= 1
                
            g_filtered_object_list[l_index].window_Bid = l_window
        
        l_index += 1
    return

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

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

   try:
      args.tickSize
   except:
      print "Since -tickSize has not been specified I cannot proceed"
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

   lNameOfFeaturePrinted = "fMovingAverageOfCol" + args.c + "InLast" + str(args.n) + "Rows"
   return ["TimeStamp",lNameOfFeaturePrinted,"Zero1","Zero2"]
