"""
This will generate features like:
1. fOBAvgHistPriceOfColAskInRows

"""
import dataFile
import colNumberOfData
import attribute
import common

from collections import deque

#------------------------Declaration of global variables-------------------------------------
g_filtered_object_list = []

#++++++++++++++++++++++++++++++++Global Constant Used+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
g_weight_list = [0.2,0.2,0.2,0.2,0.2]
g_no_of_ticks_tobe_considered = 300


class parameters_for_calculating_historical_weighted_bid_or_ask(object):
    
    def __init__(self,timestamp = ""):
        self.timestamp = timestamp
        self.AskQ0=0
        self.AskP0=0.0
        self.AskQ1=0
        self.AskP1=0.0
        self.AskQ2=0
        self.AskP2=0.0
        self.AskQ3=0
        self.AskP3=0.0
        self.AskQ4=0
        self.AskP4=0.0
        self.BidQ0=0
        self.BidP0=0.0
        self.BidQ1=0
        self.BidP1=0.0
        self.BidQ2=0
        self.BidP2=0.0
        self.BidQ3=0
        self.BidP3=0.0
        self.BidQ4=0
        self.BidP4=0.0
        self.sum_qty_for_avg_cal_Ask = 0.0
        self.window_Ask = 1
        self.sum_qty_for_avg_cal_Bid = 0.0
        self.window_Bid = 1
        self.AskP_list = []
        self.AskQ_list = []
        self.BidP_list = []
        self.BidQ_list = []


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
            if l_prev_index == -1:
              l_corresponding_AskQ0 = g_filtered_object_list[l_index].AskQ0
              l_corresponding_AskQ1 = g_filtered_object_list[l_index].AskQ1
              l_corresponding_AskQ2 = g_filtered_object_list[l_index].AskQ2                        
              l_corresponding_AskQ3 = g_filtered_object_list[l_index].AskQ3            
              l_corresponding_AskQ4 = g_filtered_object_list[l_index].AskQ4
              g_filtered_object_list[l_index].sum_qty_for_avg_cal_Ask += (g_weight_list[0] * l_corresponding_AskQ0) + (g_weight_list[1] * l_corresponding_AskQ1) + (g_weight_list[2] * l_corresponding_AskQ2)+ (g_weight_list[3] * l_corresponding_AskQ3) + (g_weight_list[4] * l_corresponding_AskQ4)                        
            while l_prev_index>=0:   
                if (g_filtered_object_list[l_index].AskP1 >= g_filtered_object_list[l_prev_index].AskP0 and g_filtered_object_list[l_index].AskP3 <= g_filtered_object_list[l_prev_index].AskP4):
                    l_window += 1
                    
                    if l_flag_for_AskQ0 == False:
                        if g_filtered_object_list[l_index].AskP0 in g_filtered_object_list[l_prev_index].AskP_list:
                            l_index_for_AskP0 = g_filtered_object_list[l_prev_index].AskP_list.index(g_filtered_object_list[l_index].AskP0)
                            l_corresponding_AskQ0 = g_filtered_object_list[l_prev_index].AskQ_list[l_index_for_AskP0]
                        else:
                            l_index_for_AskP0 = g_filtered_object_list[l_prev_index + 1].AskP_list.index(g_filtered_object_list[l_index].AskP0)
                            l_corresponding_AskQ0 = g_filtered_object_list[l_prev_index + 1].AskQ_list[l_index_for_AskP0]
                            l_flag_for_AskQ0 = True
                                
                    if l_flag_for_AskQ1 == False:
                        if g_filtered_object_list[l_index].AskP1 in g_filtered_object_list[l_prev_index].AskP_list:
                            l_index_for_AskP1 = g_filtered_object_list[l_prev_index].AskP_list.index(g_filtered_object_list[l_index].AskP1)
                            l_corresponding_AskQ1 = g_filtered_object_list[l_prev_index].AskQ_list[l_index_for_AskP1]
                        else:
                            l_index_for_AskP1 = g_filtered_object_list[l_prev_index + 1].AskP_list.index(g_filtered_object_list[l_index].AskP1)
                            l_corresponding_AskQ1 = g_filtered_object_list[l_prev_index + 1].AskQ_list[l_index_for_AskP1]
                            l_flag_for_AskQ1 = True
                            
                    if l_flag_for_AskQ2 == False:
                        if g_filtered_object_list[l_index].AskP2 in g_filtered_object_list[l_prev_index].AskP_list:
                            l_index_for_AskP2 = g_filtered_object_list[l_prev_index].AskP_list.index(g_filtered_object_list[l_index].AskP2)
                            l_corresponding_AskQ2 = g_filtered_object_list[l_prev_index].AskQ_list[l_index_for_AskP2]
                        else:
                            l_index_for_AskP2 = g_filtered_object_list[l_prev_index + 1].AskP_list.index(g_filtered_object_list[l_index].AskP2)
                            l_corresponding_AskQ2 = g_filtered_object_list[l_prev_index + 1].AskQ_list[l_index_for_AskP2]
                            l_flag_for_AskQ2 = True
                            
                    if l_flag_for_AskQ3 == False:
                        if g_filtered_object_list[l_index].AskP3 in g_filtered_object_list[l_prev_index].AskP_list:
                            l_index_for_AskP3 = g_filtered_object_list[l_prev_index].AskP_list.index(g_filtered_object_list[l_index].AskP3)
                            l_corresponding_AskQ3 = g_filtered_object_list[l_prev_index].AskQ_list[l_index_for_AskP3]
                        else:
                            l_index_for_AskP3 = g_filtered_object_list[l_prev_index + 1].AskP_list.index(g_filtered_object_list[l_index].AskP3)
                            l_corresponding_AskQ3 = g_filtered_object_list[l_prev_index + 1].AskQ_list[l_index_for_AskP3]
                            l_flag_for_AskQ3 = True
                            
                    if l_flag_for_AskQ4 == False:
                        if g_filtered_object_list[l_index].AskP4 in g_filtered_object_list[l_prev_index].AskP_list:
                            l_index_for_AskP4 = g_filtered_object_list[l_prev_index].AskP_list.index(g_filtered_object_list[l_index].AskP4)
                            l_corresponding_AskQ4 = g_filtered_object_list[l_prev_index].AskQ_list[l_index_for_AskP4]
                        else:
                            l_index_for_AskP4 = g_filtered_object_list[l_prev_index + 1].AskP_list.index(g_filtered_object_list[l_index].AskP4)
                            l_corresponding_AskQ4 = g_filtered_object_list[l_prev_index + 1].AskQ_list[l_index_for_AskP4]
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
            if l_prev_index == -1:
              l_corresponding_BidQ0 = g_filtered_object_list[l_index].BidQ0
              l_corresponding_BidQ1 = g_filtered_object_list[l_index].BidQ1
              l_corresponding_BidQ2 = g_filtered_object_list[l_index].BidQ2                        
              l_corresponding_BidQ3 = g_filtered_object_list[l_index].BidQ3            
              l_corresponding_BidQ4 = g_filtered_object_list[l_index].BidQ4
              g_filtered_object_list[l_index].sum_qty_for_avg_cal_Ask += (g_weight_list[0] * l_corresponding_AskQ0) + (g_weight_list[1] * l_corresponding_AskQ1) + (g_weight_list[2] * l_corresponding_AskQ2)+ (g_weight_list[3] * l_corresponding_AskQ3) + (g_weight_list[4] * l_corresponding_AskQ4)                                    
            while l_prev_index>=0:   
                if (g_filtered_object_list[l_index].BidP1 <= g_filtered_object_list[l_prev_index].BidP0 and g_filtered_object_list[l_index].BidP3 >= g_filtered_object_list[l_prev_index].BidP4):
                    l_window += 1
                            
                    if l_flag_for_BidQ0 == False:
                        if g_filtered_object_list[l_index].BidP0 in g_filtered_object_list[l_prev_index].BidP_list:
                            l_index_for_BidP0 = g_filtered_object_list[l_prev_index].BidP_list.index(g_filtered_object_list[l_index].BidP0)
                            l_corresponding_BidQ0 = g_filtered_object_list[l_prev_index].BidQ_list[l_index_for_BidP0]
                        else:
                            l_index_for_BidP0 = g_filtered_object_list[l_prev_index + 1].BidP_list.index(g_filtered_object_list[l_index].BidP0)
                            l_corresponding_BidQ0 = g_filtered_object_list[l_prev_index + 1].BidQ_list[l_index_for_BidP0]
                            l_flag_for_BidQ0 = True
                            
                    if l_flag_for_BidQ1 == False:
                        if g_filtered_object_list[l_index].BidP1 in g_filtered_object_list[l_prev_index].BidP_list:
                            l_index_for_BidP1 = g_filtered_object_list[l_prev_index].BidP_list.index(g_filtered_object_list[l_index].BidP1)
                            l_corresponding_BidQ1 = g_filtered_object_list[l_prev_index].BidQ_list[l_index_for_BidP1]
                        else:
                            l_index_for_BidP1 = g_filtered_object_list[l_prev_index + 1].BidP_list.index(g_filtered_object_list[l_index].BidP1)
                            l_corresponding_BidQ1 = g_filtered_object_list[l_prev_index + 1].BidQ_list[l_index_for_BidP1]
                            l_flag_for_BidQ1 = True
                            
                    if l_flag_for_BidQ2 == False:
                        if g_filtered_object_list[l_index].BidP2 in g_filtered_object_list[l_prev_index].BidP_list:
                            l_index_for_BidP2 = g_filtered_object_list[l_prev_index].BidP_list.index(g_filtered_object_list[l_index].BidP2)
                            l_corresponding_BidQ2 = g_filtered_object_list[l_prev_index].BidQ_list[l_index_for_BidP2]
                        else:
                            l_index_for_BidP2 = g_filtered_object_list[l_prev_index + 1].BidP_list.index(g_filtered_object_list[l_index].BidP2)
                            l_corresponding_BidQ2 = g_filtered_object_list[l_prev_index + 1].BidQ_list[l_index_for_BidP2]
                            l_flag_for_BidQ2 = True
                            
                    if l_flag_for_BidQ3 == False:
                        if g_filtered_object_list[l_index].BidP3 in g_filtered_object_list[l_prev_index].BidP_list:
                            l_index_for_BidP3 = g_filtered_object_list[l_prev_index].BidP_list.index(g_filtered_object_list[l_index].BidP3)
                            l_corresponding_BidQ3 = g_filtered_object_list[l_prev_index].BidQ_list[l_index_for_BidP3]
                        else:
                            l_index_for_BidP3 = g_filtered_object_list[l_prev_index + 1].BidP_list.index(g_filtered_object_list[l_index].BidP3)
                            l_corresponding_BidQ3 = g_filtered_object_list[l_prev_index + 1].BidQ_list[l_index_for_BidP3]
                            l_flag_for_BidQ3 = True
                            
                    if l_flag_for_BidQ4 == False:
                        if g_filtered_object_list[l_index].BidP4 in g_filtered_object_list[l_prev_index].BidP_list:
                            l_index_for_BidP4 = g_filtered_object_list[l_prev_index].BidP_list.index(g_filtered_object_list[l_index].BidP4)
                            l_corresponding_BidQ4 = g_filtered_object_list[l_prev_index].BidQ_list[l_index_for_BidP4]
                        else:
                            l_index_for_BidP4 = g_filtered_object_list[l_prev_index + 1].BidP_list.index(g_filtered_object_list[l_index].BidP4)
                            l_corresponding_BidQ4 = g_filtered_object_list[l_prev_index + 1].BidQ_list[l_index_for_BidP4]
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
    
   currentRowCount = 0     
   try:
      args.c
   except:
      print "Since -c has not been specified I cannot proceed"
      os._exit()

   colNumberOfPrice0 = eval("colNumberOfData."+ args.c + "P0" )
   colNumberOfQty0 = eval("colNumberOfData."+ args.c + "Q0")
 
   colNumberOfPrice1 = colNumberOfPrice0 + 2
   colNumberOfQty1 = colNumberOfQty0 + 2
   
   colNumberOfPrice2 = colNumberOfPrice0 + 4
   colNumberOfQty2 = colNumberOfQty0 + 4
   
   colNumberOfPrice3 = colNumberOfPrice0 + 6
   colNumberOfQty3 = colNumberOfQty0 + 6
   
   colNumberOfPrice4 = colNumberOfPrice0 + 8
   colNumberOfQty4 = colNumberOfQty0 + 8       
      
   colNumberOfTimeStamp = colNumberOfData.TimeStamp

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ Reading prices +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

   for dataRow in dataFile.matrix:
      l_obj = parameters_for_calculating_historical_weighted_bid_or_ask(dataRow[colNumberOfTimeStamp])
      if args.c == "Ask": 
        l_obj.AskQ0 = int(dataRow[colNumberOfQty0])
        l_obj.AskP0 = float(dataRow[colNumberOfPrice0])
        l_obj.AskQ1 = int(dataRow[colNumberOfQty1])
        l_obj.AskP1 = float(dataRow[colNumberOfPrice1])
        l_obj.AskQ2 = int(dataRow[colNumberOfQty2])
        l_obj.AskP2 = float(dataRow[colNumberOfPrice2])
        l_obj.AskQ3 = int(dataRow[colNumberOfQty3])
        l_obj.AskP3 = float(dataRow[colNumberOfPrice3])
        l_obj.AskQ4 = int(dataRow[colNumberOfQty4])
        l_obj.AskP4 = float(dataRow[colNumberOfPrice4])
        l_obj.AskP_list = [l_obj.AskP0,l_obj.AskP1,l_obj.AskP2,l_obj.AskP3,l_obj.AskP4]
        l_obj.AskQ_list = [l_obj.AskQ0,l_obj.AskQ1,l_obj.AskQ2,l_obj.AskQ3,l_obj.AskQ4]
        l_obj.sum_qty_for_avg_cal_Ask = ((g_weight_list[0] * l_obj.AskQ0) + (g_weight_list[1] * l_obj.AskQ1) + (g_weight_list[2] * l_obj.AskQ2) + (g_weight_list[3] * l_obj.AskQ3) + (g_weight_list[4] * l_obj.AskQ4))
      else: 
        l_obj.BidQ0 = int(dataRow[colNumberOfQty0])
        l_obj.BidP0 = float(dataRow[colNumberOfPrice0])
        l_obj.BidQ1 = int(dataRow[colNumberOfQty1])
        l_obj.BidP1 = float(dataRow[colNumberOfPrice1])
        l_obj.BidQ2 = int(dataRow[colNumberOfQty2])
        l_obj.BidP2 = float(dataRow[colNumberOfPrice2])
        l_obj.BidQ3 = int(dataRow[colNumberOfQty3])
        l_obj.BidP3 = float(dataRow[colNumberOfPrice3])
        l_obj.BidQ4 = int(dataRow[colNumberOfQty4])
        l_obj.BidP4 = float(dataRow[colNumberOfPrice4])
        l_obj.BidP_list = [l_obj.BidP0,l_obj.BidP1,l_obj.BidP2,l_obj.BidP3,l_obj.BidP4]
        l_obj.BidQ_list = [l_obj.BidQ0,l_obj.BidQ1,l_obj.BidQ2,l_obj.BidQ3,l_obj.BidQ4]        
        l_obj.sum_qty_for_avg_cal_Bid = ((g_weight_list[0] * l_obj.BidQ0) + (g_weight_list[1] * l_obj.BidQ1) + (g_weight_list[2] * l_obj.BidQ2) + (g_weight_list[3] * l_obj.BidQ3) + (g_weight_list[4] * l_obj.BidQ4))
      g_filtered_object_list.append(l_obj)

#++++++++++++++++++++++++++++++++++++++++++++++++++++++ Calculating ratio ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

   if args.c == "Ask": 
     calculate_historical_weighted_Ask()
   else:
     calculate_historical_weighted_Bid()

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ Storing results ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
   
   for dataRow in dataFile.matrix:     
      # In the next 2 rows we do not do -1 since this feature if for the current row.
      attribute.aList[currentRowCount][0] = common.getTimeStamp(dataFile.matrix[currentRowCount],colNumberOfTimeStamp,args.cType)
      if args.c == "Ask":
        attribute.aList[currentRowCount][1] = g_filtered_object_list[currentRowCount].sum_qty_for_avg_cal_Ask
      else:
        attribute.aList[currentRowCount][1] = g_filtered_object_list[currentRowCount].sum_qty_for_avg_cal_Bid    

      currentRowCount = currentRowCount + 1

      if (currentRowCount%10000==0):
         print "Processed row number " + str(currentRowCount)

   lNameOfFeaturePrinted = "fOBAvgHistPriceOfCol" + args.c + "InRows"
   return ["TimeStamp",lNameOfFeaturePrinted,"Zero1","Zero2"]
