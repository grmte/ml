import pdb
class liveSimStructure():
    def __init__(self):
        self.slno = 0
        self.instrument_name = ""
        self.mcode = ""
        self.AskQ=[0,0,0,0,0]
        self.AskP=[0.0,0.0,0.0,0.0,0.0]
        self.BidQ=[0,0,0,0,0]
        self.BidP=[0.0,0.0,0.0,0.0,0.0]
        self.msgType = ""
        self.type = ""
        self.new_qty = 0
        self.new_price = 0.0
        self.old_qty = 0
        self.old_price = 0.0
        self.featureBid = ""
        self.featureAsk = ""
        self.probabilityBuy = ""
        self.probabilitySell = ""
        self.simFileProbabilityBid = ""
        self.simFileProbabilityAsk = ""
        self.simFileFeatureBid = ""
        self.simFileFeatureAsk = ""
        self.simFileTargetBid = ""
        self.simFileTargetAsk = ""
        self.currentPositionLong = ""
        self.currentPositionShort = "" 
        self.enterTradeShort = ""
        self.enterTradeLong = ""
        self.reasonForTradingOrNotTradingShort = ""
        self.reasonForTradingOrNotTradingLong = ""
        self.currentTime = 0.0

class liveLogsStructures():
    def __init__(self):
        self.slno = 0
        self.instrument_name = ""
        self.mcode = ""
        self.currentTime = 0.0        
        self.our_id = 0
        self.OrderType = ''
        self.OrderQty = 0
        self.CRQ = 0
        self.LTQ = 0
        self.TTQ = 0
        self.OrderPrice = 0.0
        self.LTP = 0.0  
        self.status = ""
                  
def read_input_file_and_populate_object():
    lAskP = [2,4,6,8,10]
    lBidP = [12,14,16,18,20]
    lAskQ = [1,3,5,7,9]
    lBidQ = [11,13,15,17,19]
    lTTQ = 21
    lLTP = 22
    lSimBuyProb = 40
    lSimSellProb = 41
    lSimFeature = [42,43]
    lSimTarget = [44,45]
    lSimCurrenPosLong = 46
    lSimCurrentPosShort = 47
    lSimEnterTradeShort = 48
    lSimEnterTradeLong = 49
    lSimReasonForTradeHapOrNotShort = 50
    lSimReasonForTradeHapOrNotLong = 51
    lFlag = 0 
    count = 0
    l_list_of_objects = []
    l_list_of_lines_read = []
    print "\nReading Input Data ..."
    log_file = open("/home/vikas/ml/ob/data/ro/nsecur/20140620/log-for-programmer-for-pid-28448.txt","r")
    sim_python_file = open("/home/vikas/ml/ob/data/ro/nsecur/20140620/glmnet-td.20140528-dt.15-targetClass.binomial-f.30-wt.default-l.55-45-tq50.csv","r")
    output_file = open("/home/vikas/ml/ob/data/ro/nsecur/20140620/ML-Live-Sim-Comparison.csv","w")
    lListOfStringsToPrint = [ "slno" , "CurrentTime" , "mcode" , "AskP0;AskP1;AskP2;AskP3;AskP4" , "AskQ0;AskQ1;AskQ2;AskQ3;AskQ4" , "BidP0;BidP1;BidP2;BidP3;BidP4"\
                     , "BidQ0;BidQ1;BidQ2;BidQ3;BidQ4" , "TTQ" , "LTP" , "msgType" , "type" , "new_price" , "new_qty" , \
                     "old_price" , "old_qty" , "featureBid" , "featureAsk" , "probabilityBuy" , "probabilitySell" , \
                     "simFileFeatureBid" , "simFileFeatureAsk" , "simFileProbabilityBid" , "simFileProbabilityAsk" , "simFileTargetBid" , \
                     "simFileTargetAsk" , "currentPositionLong" , "currentPositionShort" , "enterTradeLong" , "enterTradeShort" , \
                     "reasonForTradingOrNotTradingShort" ,  "reasonForTradingOrNotTradingLong" , "OurId" , "OrderType" , "CRQ" , "LTQ" , "OrderPrice"]
    lStringToPrint = ";".join(lListOfStringsToPrint) 
    output_file.write("%s\n" %lStringToPrint)
    firstLine = sim_python_file.readline()
    for l_line_WC in log_file:
        l_line = l_line_WC.strip().replace(',',';')
        l_splitted_line = l_line.split(";")
        l_mcode = l_splitted_line[1]
        l_slno = (l_splitted_line[0].split("="))[1]
        if l_mcode == "MCODE=702":

            l_obj = liveSimStructure()
            l_obj.mcode = l_mcode.split("=")[1]
            l_obj.slno = int(l_slno)
            l_obj.AskP = [float(l_splitted_line[7].split("=")[1]),float(l_splitted_line[9].split("=")[1]),float(l_splitted_line[11].split("=")[1]),\
                           float(l_splitted_line[13].split("=")[1]),float(l_splitted_line[15].split("=")[1])]
            l_obj.AskQ = [int(float(l_splitted_line[8].split("=")[1])),int(float(l_splitted_line[10].split("=")[1])),int(float(l_splitted_line[12].split("=")[1])),\
                           int(float(l_splitted_line[14].split("=")[1])),int(float(l_splitted_line[16].split("=")[1]))]
            l_obj.BidP = [float(l_splitted_line[17].split("=")[1]),float(l_splitted_line[19].split("=")[1]),float(l_splitted_line[21].split("=")[1]),\
                           float(l_splitted_line[23].split("=")[1]),float(l_splitted_line[25].split("=")[1])]
            l_obj.BidQ = [int(float(l_splitted_line[18].split("=")[1])),int(float(l_splitted_line[20].split("=")[1])),int(float(l_splitted_line[22].split("=")[1])),\
                           int(float(l_splitted_line[24].split("=")[1])),int(float(l_splitted_line[26].split("=")[1]))]
            l_obj.TTQ = int(l_splitted_line[27].split("=")[1])
            l_obj.LTP = float(l_splitted_line[28].split("=")[1])
            l_obj.msgType = l_splitted_line[29].split("=")[1]
            l_obj.type = l_splitted_line[30].split("=")[1]
            l_obj.new_price = float(l_splitted_line[31].split("=")[1])
            l_obj.new_qty = int(l_splitted_line[32].split("=")[1])
            if l_obj.msgType == "M":
                l_obj.old_price = float(l_splitted_line[33].split("=")[1])
                l_obj.old_qty = int(l_splitted_line[34].split("=")[1])
            l_obj.featureBid = l_splitted_line[37].split("=")[1]
            l_obj.featureAsk = l_splitted_line[38].split("=")[1]
            l_obj.probabilityBuy = l_splitted_line[42].split("=")[1]
            l_obj.probabilitySell = l_splitted_line[43].split("=")[1]
            l_obj.currentTime = float(l_splitted_line[35].split("=")[1])
            while True:
                l_sim_file_line = sim_python_file.readline().strip()
                l_sim_splitted_line = l_sim_file_line.split(";")
                count = count + 1
                if (l_obj.AskP == [ float(l_sim_splitted_line[lAskP[0]]) , float(l_sim_splitted_line[lAskP[1]]) , float(l_sim_splitted_line[lAskP[2]]) , float(l_sim_splitted_line[lAskP[3]]) , float(l_sim_splitted_line[lAskP[4]]) ] ):
                    if (l_obj.BidP == [ float(l_sim_splitted_line[lBidP[0]]) , float(l_sim_splitted_line[lBidP[1]]) , float(l_sim_splitted_line[lBidP[2]]) , float(l_sim_splitted_line[lBidP[3]]) , float(l_sim_splitted_line[lBidP[4]]) ] ):                                                                                                                        
                        if (l_obj.AskQ == [ int(l_sim_splitted_line[lAskQ[0]]) , int(l_sim_splitted_line[lAskQ[1]]) , int(l_sim_splitted_line[lAskQ[2]]) , int(l_sim_splitted_line[lAskQ[3]]) , int(l_sim_splitted_line[lAskQ[4]]) ] ) :
                            if (l_obj.BidQ == [ int(l_sim_splitted_line[lBidQ[0]]) , int(l_sim_splitted_line[lBidQ[1]]) , int(l_sim_splitted_line[lBidQ[2]]) , int(l_sim_splitted_line[lBidQ[3]]) , int(l_sim_splitted_line[lBidQ[4]]) ] ) :
                                if ( l_obj.TTQ == int(l_sim_splitted_line[lTTQ]) ) and ( l_obj.LTP == float(l_sim_splitted_line[lLTP]) ):
                                    lFlag = 1
                                    print "Count of tbt data reached = " , count
                                    l_obj.simFileProbabilityBid = l_sim_splitted_line[lSimBuyProb]
                                    l_obj.simFileProbabilityAsk = l_sim_splitted_line[lSimSellProb]
                                    l_obj.simFileFeatureBid = l_sim_splitted_line[lSimFeature[0]]
                                    l_obj.simFileFeatureAsk = l_sim_splitted_line[lSimFeature[1]]
                                    l_obj.simFileTargetBid = l_sim_splitted_line[lSimTarget[0]]
                                    l_obj.simFileTargetAsk = l_sim_splitted_line[lSimTarget[1]]
                                    if ("%6f" %float(l_obj.simFileFeatureBid)) != ("%6f" %float(l_obj.featureBid)):
                                        pdb.set_trace()
                                    if ("%6f" %float(l_obj.simFileFeatureAsk)) != ("%6f" %float(l_obj.featureAsk)):
                                        pdb.set_trace()   
#                                    if ("%6f" %float(l_obj.simFileProbabilityBid)) != ("%6f" %float(l_obj.probabilityBuy)):
#                                        pdb.set_trace()   
#                                    if ("%6f" %float(l_obj.simFileProbabilityAsk)) != ("%6f" %float(l_obj.probabilitySell)):
#                                        pdb.set_trace()                                
                                    l_obj.currentPositionLong = l_sim_splitted_line[lSimCurrenPosLong]
                                    l_obj.currentPositionShort = l_sim_splitted_line[lSimCurrentPosShort]
                                    l_obj.enterTradeLong = l_sim_splitted_line[lSimEnterTradeShort]
                                    l_obj.enterTradeShort = l_sim_splitted_line[lSimEnterTradeLong]
                                    l_obj.reasonForTradingOrNotTradingShort = l_sim_splitted_line[lSimReasonForTradeHapOrNotLong]
                                    l_obj.reasonForTradingOrNotTradingLong = l_sim_splitted_line[lSimReasonForTradeHapOrNotShort]    
                                    break
                if lFlag == 1:
                    pdb.set_trace()
#             l_list_of_lines_read.append(l_sim_file_line)
            lListOfStringsToPrint = [ str(l_obj.slno) , str(l_obj.currentTime) ,str(l_obj.mcode) , ";".join(map(str,l_obj.AskP)) , ";".join(map(str,l_obj.AskQ)) , ";".join(map(str,l_obj.BidP))\
                             , ";".join(map(str,l_obj.BidQ)) , str(l_obj.TTQ) , str(l_obj.LTP) , l_obj.msgType , l_obj.type , str(l_obj.new_price) , str(l_obj.new_qty) , \
                             str(l_obj.old_price) , str(l_obj.old_qty) ,("%6f" %float(l_obj.featureBid)) , ("%6f" %float(l_obj.featureAsk)) , ("%6f" %float(l_obj.probabilityBuy))\
                             , ("%6f" %float(l_obj.probabilitySell)) , ("%6f" %float(l_obj.simFileFeatureBid)) , ("%6f" %float(l_obj.simFileFeatureAsk)) , ("%6f" %float(l_obj.simFileProbabilityBid)) , ("%6f" %float(l_obj.simFileProbabilityAsk)) , l_obj.simFileTargetBid , \
                             l_obj.simFileTargetAsk , l_obj.currentPositionLong , l_obj.currentPositionShort , l_obj.enterTradeLong , l_obj.enterTradeShort , \
                             l_obj.reasonForTradingOrNotTradingShort ,  l_obj.reasonForTradingOrNotTradingLong ]
            
#             l_list_of_objects.append(l_obj)
            lStringToPrint = ";".join(lListOfStringsToPrint)
            output_file.write("%s\n" %lStringToPrint)
            
        if l_mcode == "MCODE=416":
            l_obj = liveLogsStructures()
            l_obj.mcode = l_mcode.split("=")[1]
            l_obj.slno = int(l_slno)
            l_obj.currentTime = float(l_splitted_line[7].split("=")[1])
            l_obj.OrderQty = int(l_splitted_line[9].split("=")[1])
            l_obj.OrderPrice = float(l_splitted_line[10].split("=")[1])
            l_obj.OrderType = l_splitted_line[11].split("=")[1]
            l_obj.our_id =int(l_splitted_line[12].split("=")[1])
            l_obj.status = l_splitted_line[13].split("=")[1]
            l_obj.LTP = float(l_splitted_line[14].split("=")[1])
            l_obj.LTQ = int(l_splitted_line[15].split("=")[1])
            lListOfStringsToPrint = [ str(l_obj.slno) , str(l_obj.currentTime) ,str(l_obj.mcode) , ";".join(map(str,[0,0,0,0,0])) , ";".join(map(str,[0,0,0,0,0])) , ";".join(map(str,[0,0,0,0,0]))\
                             , ";".join(map(str,[0,0,0,0,0])) , str(l_obj.TTQ) , str(l_obj.LTP) , str(0) , str(0) , str(0.0) , str(0) , \
                             str(0.0) , str(0) , "" , "" , "" , "" , "" , "" , "" , "" , "" , "" , "" , "" , "", "" , \
                             "" ,  "" , str(l_obj.our_id) , str(l_obj.OrderType) , str(l_obj.CRQ) , str(l_obj.LTQ) , str(l_obj.OrderPrice) ] 
#             l_list_of_objects.append(l_obj)
            lStringToPrint = ";".join(lListOfStringsToPrint)
            output_file.write("%s\n" %lStringToPrint)
            
        elif l_mcode == "MCODE=421" or l_mcode == "MCODE=422" or l_mcode == "MCODE=423":
            l_obj = liveLogsStructures()
            l_obj.mcode = l_mcode.split("=")[1]
            l_obj.slno = int(l_slno)
            l_obj.currentTime = float(l_splitted_line[7].split("=")[1])
            l_obj.our_id = int(l_splitted_line[9].split("=")[1])
            l_obj.OrderType = l_splitted_line[10].split("=")[1]
            l_obj.OrderQty = int(l_splitted_line[14].split("=")[1])
            l_obj.CRQ = int(l_splitted_line[15].split("=")[1])
            l_obj.LTQ = int(l_splitted_line[16].split("=")[1])
            l_obj.TTQ = int(l_splitted_line[17].split("=")[1])
            l_obj.OrderPrice = float(l_splitted_line[18].split("=")[1])
            l_obj.LTP = float(l_splitted_line[19].split("=")[1])

            if l_mcode == "MCODE=421":
                l_obj.status = "ORDER_NEW"
            elif l_mcode == "MCODE=422":
                l_obj.status = "ORDER_MODIFY_REQUESTED"
            else:
                l_obj.status = "ORDER_CANCEL_REQUESTED"
 
            lListOfStringsToPrint = [ str(l_obj.slno) , str(l_obj.currentTime) ,str(l_obj.mcode) , ";".join(map(str,[0,0,0,0,0])) , ";".join(map(str,[0,0,0,0,0])) , ";".join(map(str,[0,0,0,0,0]))\
                             , ";".join(map(str,[0,0,0,0,0])) , str(l_obj.TTQ) , str(l_obj.LTP) , str(0) , str(0) , str(0.0) , str(0) , \
                             str(0.0) , str(0) , "" , "" , "" , "" , "" , "" , "" , "" , "" , \
                             "" , "" , "" , "" , "" , "" ,  "" , str(l_obj.our_id) , str(l_obj.OrderType) , str(l_obj.CRQ) , str(l_obj.LTQ) , str(l_obj.OrderPrice) ]            
#             l_list_of_objects.append(l_obj)
            
            lStringToPrint = ";".join(lListOfStringsToPrint)
            output_file.write("%s\n" %lStringToPrint)
        
    return


read_input_file_and_populate_object()
