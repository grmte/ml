import sys, dataFile, colNumberOfData, attribute, common
from collections import deque
from math import exp

g_dictionary_of_values_to_be_logged = {
                                       "NEW_WITH_PRICE_CHANGE" : 1,
                                       "NEW_WITHOUT_PRICE_CHANGE" :1,
                                       "CANCEL_WITH_PRICE_CHANGE":1,
                                       "CANCEL_WITHOUT_PRICE_CHANGE":1,
                                       "TRADE_WITH_PRICE_CHANGE":1,
                                       "TRADE_WITHOUT_PRICE_CHANGE":1,
                                       "MOD_CANCEL_CASE1":1,
                                       "MOD_CANCEL_CASE2":1,
                                       "MOD_NEW_CASE1":1,
                                       "MOD_NEW_CASE2":1,
                                       "MOD_NEW_CASE3":1,
                                       "NORMAL_MODIFICATION":1
                                       }

class logs_to_be_made(object):
    def __init__(self):
        self.new_price_qty_sum = [ 0 , 0 , 0 , 0 , 0 ]
        self.new_price_sum = [ 0.0 , 0.0 , 0.0 , 0.0 ,0.0 ]
        self.old_price_qty_sum = [ 0 , 0 , 0 , 0 , 0 ]
        self.old_price_sum = [0.0 , 0.0 , 0.0 , 0.0 , 0.0 ]
        self.new_price_sum_for_all_levels = 0.0
        self.new_qty_sum_for_all_levels = 0
        self.old_price_sum_for_all_levels = 0.0
        self.old_qty_sum_for_all_levels = 0
        self.distance_between_new_price_old_price_sum = 0.0
        self.count = 0
        
        
        
class ticks_values_to_be_stored(object):
    def __init__(self):
        self.PriceList = [ 0.0 , 0.0 , 0.0 , 0.0 , 0.0 ]
        self.QtyList = [ 0 , 0 , 0 , 0 , 0 ]
        self.MsgCode = ''
        self.OrderType = ''
        self.NewP = 0.0
        self.NewQ = 0
        self.OldP = 0.0
        self.OldQ = 0
        self.type_of_case = ''
        self.new_price_index = -1
        self.old_price_index = -1

class data_file_values_to_be_stored(object):
    def __init__(self):
        self.mod_new_case1 = logs_to_be_made()
        self.mod_new_case2 = logs_to_be_made()
        self.mod_new_case3 = logs_to_be_made()
        self.mod_cancel_case1 = logs_to_be_made()
        self.mod_cancel_case2 = logs_to_be_made()
        self.mod_case_normal = logs_to_be_made()

        self.new_price_change = logs_to_be_made()
        self.new_without_price_change = logs_to_be_made()
        
        self.cancel_price_change = logs_to_be_made()
        self.cancel_without_price_change = logs_to_be_made()
        
        self.trade_without_price_change = logs_to_be_made()
        self.trade_with_price_change = logs_to_be_made()
        
def updateCurrentTickAdditionToQueue( pCurrentTickObject, pPreviousTickObject , pBuyOrSellSide , pTickSize , pDataFileObject ):

    if ((pBuyOrSellSide == "ask") and (pCurrentTickObject.MsgCode == "N" and pCurrentTickObject.OrderType == "S")) or ( (pBuyOrSellSide == "bid") and (pCurrentTickObject.MsgCode == "N" and pCurrentTickObject.OrderType == "B")):  
        if pCurrentTickObject.NewP not in pPreviousTickObject.PriceList :  # New price in Order Book
            pCurrentTickObject.type_of_case = "NEW_WITH_PRICE_CHANGE"
            pDataFileObject.new_price_change.count += 1  
            pDataFileObject.new_price_change.new_price_sum_for_all_levels += pCurrentTickObject.NewP
            pDataFileObject.new_price_change.new_qty_sum_for_all_levels += pCurrentTickObject.NewQ
            lIndexOfNewPrice = pCurrentTickObject.PriceList.index(pCurrentTickObject.NewP)
            pCurrentTickObject.new_price_index = lIndexOfNewPrice
            pDataFileObject.new_price_change.new_price_qty_sum[lIndexOfNewPrice] += pCurrentTickObject.NewQ
            pDataFileObject.new_price_change.new_price_sum[lIndexOfNewPrice] += pCurrentTickObject.NewP
        else:
            pCurrentTickObject.type_of_case = "NEW_WITHOUT_PRICE_CHANGE"
            pDataFileObject.new_without_price_change.count += 1  
            pDataFileObject.new_without_price_change.new_price_sum_for_all_levels += pCurrentTickObject.NewP
            pDataFileObject.new_without_price_change.new_qty_sum_for_all_levels += pCurrentTickObject.NewQ
            lIndexOfNewPrice = pCurrentTickObject.PriceList.index(pCurrentTickObject.NewP)
            pCurrentTickObject.new_price_index = lIndexOfNewPrice
            pDataFileObject.new_without_price_change.new_price_qty_sum[lIndexOfNewPrice] += pCurrentTickObject.NewQ
            pDataFileObject.new_without_price_change.new_price_sum[lIndexOfNewPrice] += pCurrentTickObject.NewP     
            
    if ((pBuyOrSellSide == "ask") and (pCurrentTickObject.MsgCode == "X" and pCurrentTickObject.OrderType == "S")) or ( (pBuyOrSellSide == "bid") and (pCurrentTickObject.MsgCode == "X" and pCurrentTickObject.OrderType == "B")):     
        l_cancel_price = pCurrentTickObject.NewP
        if l_cancel_price not in pCurrentTickObject.PriceList : 
            pCurrentTickObject.type_of_case = "CANCEL_WITH_PRICE_CHANGE"
            pDataFileObject.cancel_price_change.count += 1  
            pDataFileObject.cancel_price_change.new_price_sum_for_all_levels += pCurrentTickObject.NewP
            pDataFileObject.cancel_price_change.new_qty_sum_for_all_levels += pCurrentTickObject.NewQ
            lIndexOfNewPrice = pPreviousTickObject.PriceList.index(pCurrentTickObject.NewP)
            pCurrentTickObject.new_price_index = lIndexOfNewPrice
            pDataFileObject.cancel_price_change.new_price_qty_sum[lIndexOfNewPrice] += pCurrentTickObject.NewQ
            pDataFileObject.cancel_price_change.new_price_sum[lIndexOfNewPrice] += pCurrentTickObject.NewP
        else:
            pCurrentTickObject.type_of_case = "CANCEL_WITHOUT_PRICE_CHANGE"
            pDataFileObject.cancel_without_price_change.count += 1  
            pDataFileObject.cancel_without_price_change.new_price_sum_for_all_levels += pCurrentTickObject.NewP
            pDataFileObject.cancel_without_price_change.new_qty_sum_for_all_levels += pCurrentTickObject.NewQ
            lIndexOfNewPrice = pPreviousTickObject.PriceList.index(pCurrentTickObject.NewP)
            pCurrentTickObject.new_price_index = lIndexOfNewPrice
            pDataFileObject.cancel_without_price_change.new_price_qty_sum[lIndexOfNewPrice] += pCurrentTickObject.NewQ
            pDataFileObject.cancel_without_price_change.new_price_sum[lIndexOfNewPrice] += pCurrentTickObject.NewP                      

    if pCurrentTickObject.MsgCode == "T":
        if  pCurrentTickObject.NewP in pPreviousTickObject.PriceList:
            l_traded_price = pCurrentTickObject.NewP
            l_traded_qty = pCurrentTickObject.NewQ
            lIndexOfTradePrice = pPreviousTickObject.PriceList.index(l_traded_price)
            if l_traded_qty == pPreviousTickObject.QtyList[lIndexOfTradePrice]:
                pCurrentTickObject.type_of_case = "TRADE_WITH_PRICE_CHANGE"
                pDataFileObject.trade_with_price_change.count += 1  
                pDataFileObject.trade_with_price_change.new_price_sum_for_all_levels += pCurrentTickObject.NewP
                pDataFileObject.trade_with_price_change.new_qty_sum_for_all_levels += pCurrentTickObject.NewQ
                lIndexOfNewPrice = pPreviousTickObject.PriceList.index(pCurrentTickObject.NewP)
                pCurrentTickObject.new_price_index = lIndexOfNewPrice
                pDataFileObject.trade_with_price_change.new_price_qty_sum[lIndexOfNewPrice] += pCurrentTickObject.NewQ
                pDataFileObject.trade_with_price_change.new_price_sum[lIndexOfNewPrice] += pCurrentTickObject.NewP                 
            else:
                pCurrentTickObject.type_of_case = "TRADE_WITHOUT_PRICE_CHANGE"
                pDataFileObject.trade_without_price_change.count += 1  
                pDataFileObject.trade_without_price_change.new_price_sum_for_all_levels += pCurrentTickObject.NewP
                pDataFileObject.trade_without_price_change.new_qty_sum_for_all_levels += pCurrentTickObject.NewQ
                lIndexOfNewPrice = pPreviousTickObject.PriceList.index(pCurrentTickObject.NewP)
                pCurrentTickObject.new_price_index = lIndexOfNewPrice
                pDataFileObject.trade_without_price_change.new_price_qty_sum[lIndexOfNewPrice] += pCurrentTickObject.NewQ
                pDataFileObject.trade_without_price_change.new_price_sum[lIndexOfNewPrice] += pCurrentTickObject.NewP 

    if ((pBuyOrSellSide == "ask") and (pCurrentTickObject.MsgCode == "M" and pCurrentTickObject.OrderType == "S")) or ( (pBuyOrSellSide == "bid") and (pCurrentTickObject.MsgCode == "M" and pCurrentTickObject.OrderType == "B")):
        #-----------------------------------------------MOD Cancel-------------------------------------------------------------------------------------------------------------------
        #Modify Case 1----------------------------------------------------------------------------------------------------------------------------------------------------------------
        if (pCurrentTickObject.OldP in pPreviousTickObject.PriceList and pCurrentTickObject.OldP not in pCurrentTickObject.PriceList) and (pCurrentTickObject.NewP in pCurrentTickObject.PriceList and pCurrentTickObject.NewP in pPreviousTickObject.PriceList):
            pCurrentTickObject.type_of_case = "MOD_CANCEL_CASE1"
            pDataFileObject.mod_cancel_case1.count += 1  
            pDataFileObject.mod_cancel_case1.new_price_sum_for_all_levels += pCurrentTickObject.NewP
            pDataFileObject.mod_cancel_case1.new_qty_sum_for_all_levels += pCurrentTickObject.NewQ
            pDataFileObject.mod_cancel_case1.old_price_sum_for_all_levels += pCurrentTickObject.OldP
            pDataFileObject.mod_cancel_case1.old_qty_sum_for_all_levels += pCurrentTickObject.OldQ
            lIndexOfNewPrice = pCurrentTickObject.PriceList.index(pCurrentTickObject.NewP)
            pCurrentTickObject.new_price_index = lIndexOfNewPrice
            pDataFileObject.mod_cancel_case1.new_price_qty_sum[lIndexOfNewPrice] += pCurrentTickObject.NewQ
            pDataFileObject.mod_cancel_case1.new_price_sum[lIndexOfNewPrice] += pCurrentTickObject.NewP 
            lIndexOfOldPrice =  pPreviousTickObject.PriceList.index(pCurrentTickObject.OldP) 
            pCurrentTickObject.old_price_index = lIndexOfOldPrice  
            pDataFileObject.mod_cancel_case1.old_price_qty_sum[lIndexOfOldPrice] += pCurrentTickObject.OldQ
            pDataFileObject.mod_cancel_case1.old_price_sum[lIndexOfOldPrice] += pCurrentTickObject.OldP   
            pDataFileObject.mod_cancel_case1.distance_between_new_price_old_price_sum  +=  abs(pCurrentTickObject.NewP  - pCurrentTickObject.OldP)  /   pTickSize 
        #Modify Case 2---------------------------------------------------------------------------------------------------------------------------------------------------------------- 
        elif (pCurrentTickObject.NewP not in pPreviousTickObject.PriceList and pCurrentTickObject.NewP not in pCurrentTickObject.PriceList) and (pCurrentTickObject.OldP not in pCurrentTickObject.PriceList and pCurrentTickObject.OldP in pPreviousTickObject.PriceList):
            pCurrentTickObject.type_of_case = "MOD_CANCEL_CASE2"
            pDataFileObject.mod_cancel_case2.count += 1  
            pDataFileObject.mod_cancel_case2.old_price_sum_for_all_levels += pCurrentTickObject.OldP
            pDataFileObject.mod_cancel_case2.old_qty_sum_for_all_levels += pCurrentTickObject.OldQ
            lIndexOfOldPrice =  pPreviousTickObject.PriceList.index(pCurrentTickObject.OldP)   
            pCurrentTickObject.old_price_index = lIndexOfOldPrice 
            pDataFileObject.mod_cancel_case2.old_price_qty_sum[lIndexOfOldPrice] += pCurrentTickObject.OldQ
            pDataFileObject.mod_cancel_case2.old_price_sum[lIndexOfOldPrice] += pCurrentTickObject.OldP     
            pDataFileObject.mod_cancel_case2.distance_between_new_price_old_price_sum  +=  abs(pCurrentTickObject.NewP  - pCurrentTickObject.OldP) / pTickSize
        #Modify Case 3---------------------------------------------------------------------------------------------------------------------------------------------------------------
        elif (pCurrentTickObject.NewP in pCurrentTickObject.PriceList and pCurrentTickObject.NewP not in pPreviousTickObject.PriceList) and (pCurrentTickObject.OldP in pCurrentTickObject.PriceList and pCurrentTickObject.OldP in pPreviousTickObject.PriceList):
            pCurrentTickObject.type_of_case = "MOD_NEW_CASE1"
            pDataFileObject.mod_new_case1.count += 1  
            pDataFileObject.mod_new_case1.new_price_sum_for_all_levels += pCurrentTickObject.NewP
            pDataFileObject.mod_new_case1.new_qty_sum_for_all_levels += pCurrentTickObject.NewQ
            pDataFileObject.mod_new_case1.old_price_sum_for_all_levels += pCurrentTickObject.OldP
            pDataFileObject.mod_new_case1.old_qty_sum_for_all_levels += pCurrentTickObject.OldQ
            lIndexOfNewPrice = pCurrentTickObject.PriceList.index(pCurrentTickObject.NewP)
            pCurrentTickObject.new_price_index = lIndexOfNewPrice
            pDataFileObject.mod_new_case1.new_price_qty_sum[lIndexOfNewPrice] += pCurrentTickObject.NewQ
            pDataFileObject.mod_new_case1.new_price_sum[lIndexOfNewPrice] += pCurrentTickObject.NewP 
            lIndexOfOldPrice =  pPreviousTickObject.PriceList.index(pCurrentTickObject.OldP) 
            pCurrentTickObject.old_price_index = lIndexOfOldPrice  
            pDataFileObject.mod_new_case1.old_price_qty_sum[lIndexOfOldPrice] += pCurrentTickObject.OldQ
            pDataFileObject.mod_new_case1.old_price_sum[lIndexOfOldPrice] += pCurrentTickObject.OldP   
            pDataFileObject.mod_new_case1.distance_between_new_price_old_price_sum  +=  abs(pCurrentTickObject.NewP  - pCurrentTickObject.OldP) / pTickSize
            
        #Modify Case 4---------------------------------------------------------------------------------------------------------------------------------------------------------------   
        elif (pCurrentTickObject.OldP not in pPreviousTickObject.PriceList) and (pCurrentTickObject.NewP in pCurrentTickObject.PriceList and pCurrentTickObject.NewP not in pPreviousTickObject.PriceList) :
            pCurrentTickObject.type_of_case = "MOD_NEW_CASE2"
            pDataFileObject.mod_new_case2.count += 1  
            pDataFileObject.mod_new_case2.new_price_sum_for_all_levels += pCurrentTickObject.NewP
            pDataFileObject.mod_new_case2.new_qty_sum_for_all_levels += pCurrentTickObject.NewQ
            lIndexOfNewPrice = pCurrentTickObject.PriceList.index(pCurrentTickObject.NewP)
            pCurrentTickObject.new_price_index = lIndexOfNewPrice
            pDataFileObject.mod_new_case2.new_price_qty_sum[lIndexOfNewPrice] += pCurrentTickObject.NewQ
            pDataFileObject.mod_new_case2.new_price_sum[lIndexOfNewPrice] += pCurrentTickObject.NewP 
            pDataFileObject.mod_new_case2.distance_between_new_price_old_price_sum  +=  abs(pCurrentTickObject.NewP  - pCurrentTickObject.OldP) /  pTickSize         

        #Modify Case 5----------------------------------------------------------------------------------------------------------------------------------------------------------------
        elif (pCurrentTickObject.OldP in pPreviousTickObject.PriceList and pCurrentTickObject.OldP not in pCurrentTickObject.PriceList) and (pCurrentTickObject.NewP in pCurrentTickObject.PriceList and pCurrentTickObject.NewP not in pPreviousTickObject.PriceList):
            pCurrentTickObject.type_of_case = "MOD_NEW_CASE3"
            pDataFileObject.mod_new_case3.count += 1  
            pDataFileObject.mod_new_case3.new_price_sum_for_all_levels += pCurrentTickObject.NewP
            pDataFileObject.mod_new_case3.new_qty_sum_for_all_levels += pCurrentTickObject.NewQ
            pDataFileObject.mod_new_case3.old_price_sum_for_all_levels += pCurrentTickObject.OldP
            pDataFileObject.mod_new_case3.old_qty_sum_for_all_levels += pCurrentTickObject.OldQ
            lIndexOfNewPrice = pCurrentTickObject.PriceList.index(pCurrentTickObject.NewP)
            pCurrentTickObject.new_price_index = lIndexOfNewPrice
            pDataFileObject.mod_new_case3.new_price_qty_sum[lIndexOfNewPrice] += pCurrentTickObject.NewQ
            pDataFileObject.mod_new_case3.new_price_sum[lIndexOfNewPrice] += pCurrentTickObject.NewP 
            lIndexOfOldPrice =  pPreviousTickObject.PriceList.index(pCurrentTickObject.OldP)   
            pCurrentTickObject.old_price_index = lIndexOfOldPrice
            pDataFileObject.mod_new_case3.old_price_qty_sum[lIndexOfOldPrice] += pCurrentTickObject.OldQ
            pDataFileObject.mod_new_case3.old_price_sum[lIndexOfOldPrice] += pCurrentTickObject.OldP   
            pDataFileObject.mod_new_case3.distance_between_new_price_old_price_sum  +=  abs(pCurrentTickObject.NewP  - pCurrentTickObject.OldP) / pTickSize
            
        else:
            pCurrentTickObject.type_of_case = "NORMAL_MODIFICATION"
            pDataFileObject.mod_case_normal.count += 1  
            try:
                lIndexOfNewPrice = pCurrentTickObject.PriceList.index(pCurrentTickObject.NewP)
                pDataFileObject.mod_case_normal.new_price_sum_for_all_levels += pCurrentTickObject.NewP
                pDataFileObject.mod_case_normal.new_qty_sum_for_all_levels += pCurrentTickObject.NewQ
                pCurrentTickObject.new_price_index = lIndexOfNewPrice
                pDataFileObject.mod_case_normal.new_price_qty_sum[lIndexOfNewPrice] += pCurrentTickObject.NewQ
                pDataFileObject.mod_case_normal.new_price_sum[lIndexOfNewPrice] += pCurrentTickObject.NewP 
            except:
                pass
            try:
                lIndexOfOldPrice =  pPreviousTickObject.PriceList.index(pCurrentTickObject.OldP)  
                pDataFileObject.mod_case_normal.old_price_sum_for_all_levels += pCurrentTickObject.OldP
                pDataFileObject.mod_case_normal.old_qty_sum_for_all_levels += pCurrentTickObject.OldQ
                pCurrentTickObject.old_price_index = lIndexOfOldPrice 
                pDataFileObject.mod_case_normal.old_price_qty_sum[lIndexOfOldPrice] += pCurrentTickObject.OldQ
                pDataFileObject.mod_case_normal.old_price_sum[lIndexOfOldPrice] += pCurrentTickObject.OldP   
                pDataFileObject.mod_case_normal.distance_between_new_price_old_price_sum  +=  abs(pCurrentTickObject.NewP  - pCurrentTickObject.OldP) / pTickSize    
            except:
                pass  
            
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

                                           
def updateTickDeletionFromQueue(pObjectToBeDeleted , pBuyOrSellSide , pTickSize , pDataFileObject ):
    if ((pBuyOrSellSide == "ask") and (pObjectToBeDeleted.MsgCode == "N" and pObjectToBeDeleted.OrderType == "S")) or ( (pBuyOrSellSide == "bid") and (pObjectToBeDeleted.MsgCode == "N" and pObjectToBeDeleted.OrderType == "B")):  
        if pObjectToBeDeleted.type_of_case == "NEW_WITH_PRICE_CHANGE":  # New price in Order Book

            pDataFileObject.new_price_change.count -= 1  
            pDataFileObject.new_price_change.new_price_sum_for_all_levels -= pObjectToBeDeleted.NewP
            pDataFileObject.new_price_change.new_qty_sum_for_all_levels -= pObjectToBeDeleted.NewQ
            lIndexOfNewPrice = pObjectToBeDeleted.new_price_index
            pDataFileObject.new_price_change.new_price_qty_sum[lIndexOfNewPrice] -= pObjectToBeDeleted.NewQ
            pDataFileObject.new_price_change.new_price_sum[lIndexOfNewPrice] -= pObjectToBeDeleted.NewP

        elif pObjectToBeDeleted.type_of_case == "NEW_WITHOUT_PRICE_CHANGE":
            
            pDataFileObject.new_without_price_change.count -= 1  
            pDataFileObject.new_without_price_change.new_price_sum_for_all_levels -= pObjectToBeDeleted.NewP
            pDataFileObject.new_without_price_change.new_qty_sum_for_all_levels -= pObjectToBeDeleted.NewQ
            lIndexOfNewPrice = pObjectToBeDeleted.new_price_index
            pDataFileObject.new_without_price_change.new_price_qty_sum[lIndexOfNewPrice] -= pObjectToBeDeleted.NewQ
            pDataFileObject.new_without_price_change.new_price_sum[lIndexOfNewPrice] -= pObjectToBeDeleted.NewP     
            
    if ((pBuyOrSellSide == "ask") and (pObjectToBeDeleted.MsgCode == "X" and pObjectToBeDeleted.OrderType == "S")) or ( (pBuyOrSellSide == "bid") and (pObjectToBeDeleted.MsgCode == "X" and pObjectToBeDeleted.OrderType == "B")):     
        if pObjectToBeDeleted.type_of_case == "CANCEL_WITH_PRICE_CHANGE": 

            pDataFileObject.cancel_price_change.count -= 1  
            pDataFileObject.cancel_price_change.new_price_sum_for_all_levels -= pObjectToBeDeleted.NewP
            pDataFileObject.cancel_price_change.new_qty_sum_for_all_levels -= pObjectToBeDeleted.NewQ
            lIndexOfNewPrice = pObjectToBeDeleted.new_price_index
            pDataFileObject.cancel_price_change.new_price_qty_sum[lIndexOfNewPrice] -= pObjectToBeDeleted.NewQ
            pDataFileObject.cancel_price_change.new_price_sum[lIndexOfNewPrice] -= pObjectToBeDeleted.NewP

        elif pObjectToBeDeleted.type_of_case == "CANCEL_WITHOUT_PRICE_CHANGE":

            pDataFileObject.cancel_without_price_change.count -= 1  
            pDataFileObject.cancel_without_price_change.new_price_sum_for_all_levels -= pObjectToBeDeleted.NewP
            pDataFileObject.cancel_without_price_change.new_qty_sum_for_all_levels -= pObjectToBeDeleted.NewQ
            lIndexOfNewPrice = pObjectToBeDeleted.new_price_index
            pDataFileObject.cancel_without_price_change.new_price_qty_sum[lIndexOfNewPrice] -= pObjectToBeDeleted.NewQ
            pDataFileObject.cancel_without_price_change.new_price_sum[lIndexOfNewPrice] -= pObjectToBeDeleted.NewP                      

    if pObjectToBeDeleted.MsgCode == "T":

        if  pObjectToBeDeleted.type_of_case == "TRADE_WITH_PRICE_CHANGE":

            pDataFileObject.trade_with_price_change.count -= 1  
            pDataFileObject.trade_with_price_change.new_price_sum_for_all_levels -= pObjectToBeDeleted.NewP
            pDataFileObject.trade_with_price_change.new_qty_sum_for_all_levels -= pObjectToBeDeleted.NewQ
            lIndexOfNewPrice = pObjectToBeDeleted.new_price_index 
            pDataFileObject.trade_with_price_change.new_price_qty_sum[lIndexOfNewPrice] -= pObjectToBeDeleted.NewQ
            pDataFileObject.trade_with_price_change.new_price_sum[lIndexOfNewPrice] -= pObjectToBeDeleted.NewP                 

        elif pObjectToBeDeleted.type_of_case == "TRADE_WITHOUT_PRICE_CHANGE":
            
            pDataFileObject.trade_without_price_change.count -= 1  
            pDataFileObject.trade_without_price_change.new_price_sum_for_all_levels -= pObjectToBeDeleted.NewP
            pDataFileObject.trade_without_price_change.new_qty_sum_for_all_levels -= pObjectToBeDeleted.NewQ
            lIndexOfNewPrice = pObjectToBeDeleted.new_price_index
            pDataFileObject.trade_without_price_change.new_price_qty_sum[lIndexOfNewPrice] -= pObjectToBeDeleted.NewQ
            pDataFileObject.trade_without_price_change.new_price_sum[lIndexOfNewPrice] -= pObjectToBeDeleted.NewP 

    if ((pBuyOrSellSide == "ask") and (pObjectToBeDeleted.MsgCode == "M" and pObjectToBeDeleted.OrderType == "S")) or ( (pBuyOrSellSide == "bid") and (pObjectToBeDeleted.MsgCode == "M" and pObjectToBeDeleted.OrderType == "B")):
        #-----------------------------------------------MOD Cancel-------------------------------------------------------------------------------------------------------------------
        #Modify Case 1----------------------------------------------------------------------------------------------------------------------------------------------------------------
        if pObjectToBeDeleted.type_of_case == "MOD_CANCEL_CASE1":

            pDataFileObject.mod_cancel_case1.count -= 1  
            pDataFileObject.mod_cancel_case1.new_price_sum_for_all_levels -= pObjectToBeDeleted.NewP
            pDataFileObject.mod_cancel_case1.new_qty_sum_for_all_levels -= pObjectToBeDeleted.NewQ
            pDataFileObject.mod_cancel_case1.old_price_sum_for_all_levels -= pObjectToBeDeleted.OldP
            pDataFileObject.mod_cancel_case1.old_qty_sum_for_all_levels -= pObjectToBeDeleted.OldQ
            lIndexOfNewPrice = pObjectToBeDeleted.new_price_index 
            pDataFileObject.mod_cancel_case1.new_price_qty_sum[lIndexOfNewPrice] -= pObjectToBeDeleted.NewQ
            pDataFileObject.mod_cancel_case1.new_price_sum[lIndexOfNewPrice] -= pObjectToBeDeleted.NewP 
            lIndexOfOldPrice =  pObjectToBeDeleted.old_price_index 
            pDataFileObject.mod_cancel_case1.old_price_qty_sum[lIndexOfOldPrice] -= pObjectToBeDeleted.OldQ
            pDataFileObject.mod_cancel_case1.old_price_sum[lIndexOfOldPrice] -= pObjectToBeDeleted.OldP   
            pDataFileObject.mod_cancel_case1.distance_between_new_price_old_price_sum  -=  abs(pObjectToBeDeleted.NewP  - pObjectToBeDeleted.OldP)  /   pTickSize 

        #Modify Case 2---------------------------------------------------------------------------------------------------------------------------------------------------------------- 
        elif pObjectToBeDeleted.type_of_case == "MOD_CANCEL_CASE2":
            
            pDataFileObject.mod_cancel_case2.count -= 1  
            pDataFileObject.mod_cancel_case2.old_price_sum_for_all_levels -= pObjectToBeDeleted.OldP
            pDataFileObject.mod_cancel_case2.old_qty_sum_for_all_levels -= pObjectToBeDeleted.OldQ
            lIndexOfOldPrice =  pObjectToBeDeleted.old_price_index   
            pDataFileObject.mod_cancel_case2.old_price_qty_sum[lIndexOfOldPrice] -= pObjectToBeDeleted.OldQ
            pDataFileObject.mod_cancel_case2.old_price_sum[lIndexOfOldPrice] -= pObjectToBeDeleted.OldP     
            pDataFileObject.mod_cancel_case2.distance_between_new_price_old_price_sum  -=  abs(pObjectToBeDeleted.NewP  - pObjectToBeDeleted.OldP) / pTickSize

        #Modify Case 3---------------------------------------------------------------------------------------------------------------------------------------------------------------
        elif  pObjectToBeDeleted.type_of_case == "MOD_NEW_CASE1":
           
            pDataFileObject.mod_new_case1.count -= 1  
            pDataFileObject.mod_new_case1.new_price_sum_for_all_levels -= pObjectToBeDeleted.NewP
            pDataFileObject.mod_new_case1.new_qty_sum_for_all_levels -= pObjectToBeDeleted.NewQ
            pDataFileObject.mod_new_case1.old_price_sum_for_all_levels -= pObjectToBeDeleted.OldP
            pDataFileObject.mod_new_case1.old_qty_sum_for_all_levels -= pObjectToBeDeleted.OldQ
            lIndexOfNewPrice = pObjectToBeDeleted.new_price_index
            pDataFileObject.mod_new_case1.new_price_qty_sum[lIndexOfNewPrice] -= pObjectToBeDeleted.NewQ
            pDataFileObject.mod_new_case1.new_price_sum[lIndexOfNewPrice] -= pObjectToBeDeleted.NewP 
            lIndexOfOldPrice =  pObjectToBeDeleted.old_price_index
            pDataFileObject.mod_new_case1.old_price_qty_sum[lIndexOfOldPrice] -= pObjectToBeDeleted.OldQ
            pDataFileObject.mod_new_case1.old_price_sum[lIndexOfOldPrice] -= pObjectToBeDeleted.OldP   
            pDataFileObject.mod_new_case1.distance_between_new_price_old_price_sum  -=  abs(pObjectToBeDeleted.NewP  - pObjectToBeDeleted.OldP) / pTickSize
            
        #Modify Case 4---------------------------------------------------------------------------------------------------------------------------------------------------------------   
        elif pObjectToBeDeleted.type_of_case == "MOD_NEW_CASE2":
            
            pDataFileObject.mod_new_case2.count -= 1  
            pDataFileObject.mod_new_case2.new_price_sum_for_all_levels -= pObjectToBeDeleted.NewP
            pDataFileObject.mod_new_case2.new_qty_sum_for_all_levels -= pObjectToBeDeleted.NewQ
            lIndexOfNewPrice = pObjectToBeDeleted.new_price_index
            pDataFileObject.mod_new_case2.new_price_qty_sum[lIndexOfNewPrice] -= pObjectToBeDeleted.NewQ
            pDataFileObject.mod_new_case2.new_price_sum[lIndexOfNewPrice] -= pObjectToBeDeleted.NewP 
            pDataFileObject.mod_new_case2.distance_between_new_price_old_price_sum  -=  abs(pObjectToBeDeleted.NewP  - pObjectToBeDeleted.OldP) /  pTickSize         

        #Modify Case 5----------------------------------------------------------------------------------------------------------------------------------------------------------------
        elif pObjectToBeDeleted.type_of_case == "MOD_NEW_CASE3":
            
            pDataFileObject.mod_new_case3.count -= 1  
            pDataFileObject.mod_new_case3.new_price_sum_for_all_levels -= pObjectToBeDeleted.NewP
            pDataFileObject.mod_new_case3.new_qty_sum_for_all_levels -= pObjectToBeDeleted.NewQ
            pDataFileObject.mod_new_case3.old_price_sum_for_all_levels -= pObjectToBeDeleted.OldP
            pDataFileObject.mod_new_case3.old_qty_sum_for_all_levels -= pObjectToBeDeleted.OldQ
            lIndexOfNewPrice = pObjectToBeDeleted.new_price_index
            pDataFileObject.mod_new_case3.new_price_qty_sum[lIndexOfNewPrice] -= pObjectToBeDeleted.NewQ
            pDataFileObject.mod_new_case3.new_price_sum[lIndexOfNewPrice] -= pObjectToBeDeleted.NewP 
            lIndexOfOldPrice =  pObjectToBeDeleted.old_price_index   
            pDataFileObject.mod_new_case3.old_price_qty_sum[lIndexOfOldPrice] -= pObjectToBeDeleted.OldQ
            pDataFileObject.mod_new_case3.old_price_sum[lIndexOfOldPrice] -= pObjectToBeDeleted.OldP   
            pDataFileObject.mod_new_case3.distance_between_new_price_old_price_sum  -=  abs(pObjectToBeDeleted.NewP  - pObjectToBeDeleted.OldP) / pTickSize
            
        elif pObjectToBeDeleted.type_of_case == "NORMAL_MODIFICATION":
            
            pDataFileObject.mod_case_normal.count -= 1  
            if pObjectToBeDeleted.new_price_index != -1:

                pDataFileObject.mod_case_normal.new_price_sum_for_all_levels -= pObjectToBeDeleted.NewP
                pDataFileObject.mod_case_normal.new_qty_sum_for_all_levels -= pObjectToBeDeleted.NewQ
                lIndexOfNewPrice = pObjectToBeDeleted.new_price_index
                pDataFileObject.mod_case_normal.new_price_qty_sum[lIndexOfNewPrice] -= pObjectToBeDeleted.NewQ
                pDataFileObject.mod_case_normal.new_price_sum[lIndexOfNewPrice] -= pObjectToBeDeleted.NewP 

            if pObjectToBeDeleted.old_price_index != -1 :

                pDataFileObject.mod_case_normal.old_price_sum_for_all_levels -= pObjectToBeDeleted.OldP
                pDataFileObject.mod_case_normal.old_qty_sum_for_all_levels -= pObjectToBeDeleted.OldQ
                pDataFileObject =  pObjectToBeDeleted.old_price_index  
                pDataFileObject.mod_case_normal.old_price_qty_sum[lIndexOfOldPrice] -= pObjectToBeDeleted.OldQ
                pDataFileObject.mod_case_normal.old_price_sum[lIndexOfOldPrice] -= pObjectToBeDeleted.OldP   

            pDataFileObject.mod_case_normal.distance_between_new_price_old_price_sum  -=  abs(pObjectToBeDeleted.NewP  - pObjectToBeDeleted.OldP) / pTickSize            
            
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
          
def extractAttributeFromDataMatrix(args):
    N = 5
    if args.n == None:
        N = 5
    else:
        int(args.n) 
    
    try:
        args.c
    except:
        import os
        print "Since -c has not been specified I cannot proceed"
        os._exit()
       
    colNumberOfTimeStamp = colNumberOfData.TimeStamp
    tickSize = int(args.tickSize)
    buyOrSellSide = args.c.lower()
    numberOfRowsInLastNSecs = 0
    queueOfValuesInLastNSecs = deque()
    timeOfOldestRow = common.convertTimeStampFromStringToFloat(dataFile.matrix[0][colNumberOfTimeStamp])
    currentRowNumberForWhichFeatureValueIsBeingCalculated = 0
    lengthOfDataMatrix = len(dataFile.matrix)
    g_data_file_values_to_be_stored = data_file_values_to_be_stored()
    while (currentRowNumberForWhichFeatureValueIsBeingCalculated < lengthOfDataMatrix):
        lCurrentTickObject = ticks_values_to_be_stored()
        lCurrentDataRow = dataFile.matrix[currentRowNumberForWhichFeatureValueIsBeingCalculated]
        timeOfCurrentRow = common.convertTimeStampFromStringToFloat(lCurrentDataRow[colNumberOfTimeStamp],args.cType)
        if len(queueOfValuesInLastNSecs) != 0:
            lPreviousTickObject = queueOfValuesInLastNSecs[-1][0]
        timeElapsed = timeOfCurrentRow - timeOfOldestRow
        if (timeElapsed < N):
            lCurrentTickObject.MsgCode = lCurrentDataRow[colNumberOfData.MsgCode]
            lCurrentTickObject.OrderType = lCurrentDataRow[colNumberOfData.OrderType]
            lCurrentTickObject.NewP = float(lCurrentDataRow[colNumberOfData.NewP])
            lCurrentTickObject.NewQ = int(lCurrentDataRow[colNumberOfData.NewQ])
            if lCurrentTickObject.MsgCode == "M":
                lCurrentTickObject.OldP = float(lCurrentDataRow[colNumberOfData.OldP])
                lCurrentTickObject.OldQ = int(lCurrentDataRow[colNumberOfData.OldQ])
            if buyOrSellSide == "ask" :
                lCurrentTickObject.QtyList = [ int(lCurrentDataRow[colNumberOfData.AskQ0]) , int(lCurrentDataRow[colNumberOfData.AskQ1]) , int(lCurrentDataRow[colNumberOfData.AskQ2]) , int(lCurrentDataRow[colNumberOfData.AskQ3]) , int(lCurrentDataRow[colNumberOfData.AskQ4]) ]
            else:
                lCurrentTickObject.QtyList = [ int(lCurrentDataRow[colNumberOfData.BidQ0]) , int(lCurrentDataRow[colNumberOfData.BidQ1]) , int(lCurrentDataRow[colNumberOfData.BidQ2]) , int(lCurrentDataRow[colNumberOfData.BidQ3]) , int(lCurrentDataRow[colNumberOfData.BidQ4]) ]        
            if buyOrSellSide == "ask" :
                lCurrentTickObject.PriceList = [ float(lCurrentDataRow[colNumberOfData.AskP0]) , float(lCurrentDataRow[colNumberOfData.AskP1]) , float(lCurrentDataRow[colNumberOfData.AskP2]) , float(lCurrentDataRow[colNumberOfData.AskP3]) , float(lCurrentDataRow[colNumberOfData.AskP4]) ]
            else:
                lCurrentTickObject.PriceList = [ float(lCurrentDataRow[colNumberOfData.BidP0]) , float(lCurrentDataRow[colNumberOfData.BidP1]) , float(lCurrentDataRow[colNumberOfData.BidP2]) , float(lCurrentDataRow[colNumberOfData.BidP3]) , float(lCurrentDataRow[colNumberOfData.BidP4]) ]

            if len(queueOfValuesInLastNSecs) != 0:
                updateCurrentTickAdditionToQueue(lCurrentTickObject,lPreviousTickObject , buyOrSellSide , tickSize , g_data_file_values_to_be_stored)
            attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][0] = common.convertTimeStampFromStringToDecimal(lCurrentDataRow[colNumberOfTimeStamp])
            attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][1] = str(timeElapsed) 
            lListOfValuesToPrintForTheTick = [";".join(map(str,lCurrentTickObject.PriceList)) , ";".join(map(str,lCurrentTickObject.PriceList)) , lCurrentTickObject.MsgCode , \
                                    lCurrentTickObject.OrderType , lCurrentTickObject.NewP , lCurrentTickObject.NewQ , lCurrentTickObject.OldP , lCurrentTickObject.OldQ , lCurrentTickObject.type_of_case ,\
                                    lCurrentTickObject.new_price_change.count, lCurrentTickObject.new_price_change.new_price_sum_for_all_levels , lCurrentTickObject.new_price_change.new_qty_sum_for_all_levels ,\
                                    lCurrentTickObject.new_price_index , lCurrentTickObject.old_price_index]
            
            l_new_price_change_list = [lCurrentTickObject.new_price_change.new_price_sum[0]  ,lCurrentTickObject.new_price_change.new_price_qty_sum[0] , lCurrentTickObject.new_price_change.new_price_sum[1]  ,lCurrentTickObject.new_price_change.new_price_qty_sum[1],\
                                    lCurrentTickObject.new_price_change.new_price_sum[2]  ,lCurrentTickObject.new_price_change.new_price_qty_sum[2],lCurrentTickObject.new_price_change.new_price_sum[3]  ,lCurrentTickObject.new_price_change.new_price_qty_sum[3],\
                                    lCurrentTickObject.new_price_change.new_price_sum[4]  ,lCurrentTickObject.new_price_change.new_price_qty_sum[4]]
            
            l_new_without_price_change_list = [lCurrentTickObject.new_without_price_change.count, lCurrentTickObject.new_without_price_change.new_price_sum_for_all_levels , lCurrentTickObject.new_without_price_change.new_qty_sum_for_all_levels ,\
                                    lCurrentTickObject.new_without_price_change.new_price_sum[0]  ,lCurrentTickObject.new_without_price_change.new_price_qty_sum[0] , lCurrentTickObject.new_without_price_change.new_price_sum[1]  ,lCurrentTickObject.new_without_price_change.new_price_qty_sum[1],\
                                    lCurrentTickObject.new_without_price_change.new_price_sum[2]  ,lCurrentTickObject.new_without_price_change.new_price_qty_sum[2],lCurrentTickObject.new_without_price_change.new_price_sum[3]  ,lCurrentTickObject.new_without_price_change.new_price_qty_sum[3],\
                                    lCurrentTickObject.new_without_price_change.new_price_sum[4]  ,lCurrentTickObject.new_without_price_change.new_price_qty_sum[4]]
            
            l_new_price_change_list = [ lCurrentTickObject.cancel_price_change.count, lCurrentTickObject.cancel_price_change.new_price_sum_for_all_levels , lCurrentTickObject.cancel_price_change.new_qty_sum_for_all_levels ,\
                                    lCurrentTickObject.cancel_price_change.new_price_sum[0]  ,lCurrentTickObject.cancel_price_change.new_price_qty_sum[0] , lCurrentTickObject.cancel_price_change.new_price_sum[1]  ,lCurrentTickObject.cancel_price_change.new_price_qty_sum[1],\
                                    lCurrentTickObject.cancel_price_change.new_price_sum[2]  ,lCurrentTickObject.cancel_price_change.new_price_qty_sum[2],lCurrentTickObject.cancel_price_change.new_price_sum[3]  ,lCurrentTickObject.cancel_price_change.new_price_qty_sum[3],\
                                    lCurrentTickObject.cancel_price_change.new_price_sum[4]  ,lCurrentTickObject.cancel_price_change.new_price_qty_sum[4],
                                   lCurrentTickObject.cancel_without_price_change.count, lCurrentTickObject.cancel_without_price_change.new_price_sum_for_all_levels , lCurrentTickObject.cancel_without_price_change.new_qty_sum_for_all_levels ,\
                                    lCurrentTickObject.cancel_without_price_change.new_price_sum[0]  ,lCurrentTickObject.cancel_without_price_change.new_price_qty_sum[0] , lCurrentTickObject.cancel_without_price_change.new_price_sum[1]  ,lCurrentTickObject.cancel_without_price_change.new_price_qty_sum[1],\
                                    lCurrentTickObject.cancel_without_price_change.new_price_sum[2]  ,lCurrentTickObject.cancel_without_price_change.new_price_qty_sum[2],lCurrentTickObject.cancel_without_price_change.new_price_sum[3]  ,lCurrentTickObject.cancel_without_price_change.new_price_qty_sum[3],\
                                    lCurrentTickObject.cancel_without_price_change.new_price_sum[4]  ,lCurrentTickObject.cancel_without_price_change.new_price_qty_sum[4],
                                   lCurrentTickObject.trade_with_price_change.count, lCurrentTickObject.trade_with_price_change.new_price_sum_for_all_levels , lCurrentTickObject.trade_with_price_change.new_qty_sum_for_all_levels ,\
                                    lCurrentTickObject.trade_with_price_change.new_price_sum[0]  ,lCurrentTickObject.trade_with_price_change.new_price_qty_sum[0] , lCurrentTickObject.trade_with_price_change.new_price_sum[1]  ,lCurrentTickObject.trade_with_price_change.new_price_qty_sum[1],\
                                    lCurrentTickObject.trade_with_price_change.new_price_sum[2]  ,lCurrentTickObject.trade_with_price_change.new_price_qty_sum[2],lCurrentTickObject.trade_with_price_change.new_price_sum[3]  ,lCurrentTickObject.trade_with_price_change.new_price_qty_sum[3],\
                                    lCurrentTickObject.trade_with_price_change.new_price_sum[4]  ,lCurrentTickObject.trade_with_price_change.new_price_qty_sum[4],
                                   lCurrentTickObject.trade_without_price_change.count, lCurrentTickObject.trade_without_price_change.new_price_sum_for_all_levels , lCurrentTickObject.trade_without_price_change.new_qty_sum_for_all_levels ,\
                                    lCurrentTickObject.trade_without_price_change.new_price_sum[0]  ,lCurrentTickObject.trade_without_price_change.new_price_qty_sum[0] , lCurrentTickObject.trade_without_price_change.new_price_sum[1]  ,lCurrentTickObject.trade_without_price_change.new_price_qty_sum[1],\
                                    lCurrentTickObject.trade_without_price_change.new_price_sum[2]  ,lCurrentTickObject.trade_without_price_change.new_price_qty_sum[2],lCurrentTickObject.trade_without_price_change.new_price_sum[3]  ,lCurrentTickObject.trade_without_price_change.new_price_qty_sum[3],\
                                    lCurrentTickObject.trade_without_price_change.new_price_sum[4]  ,lCurrentTickObject.trade_without_price_change.new_price_qty_sum[4],
                                   lCurrentTickObject.mod_new_case1.count, lCurrentTickObject.mod_new_case1.new_price_sum_for_all_levels , lCurrentTickObject.mod_new_case1.new_qty_sum_for_all_levels ,lCurrentTickObject.mod_new_case1.old_price_sum_for_all_levels , lCurrentTickObject.mod_new_case1.old_qty_sum_for_all_levels , lCurrentTickObject.mod_new_case1.distance_between_new_price_old_price_sum ,\
                                    lCurrentTickObject.mod_cancel_case1.count, lCurrentTickObject.mod_cancel_case1.new_price_sum_for_all_levels , lCurrentTickObject.mod_cancel_case1.new_qty_sum_for_all_levels ,lCurrentTickObject.mod_cancel_case1.old_price_sum_for_all_levels , lCurrentTickObject.mod_cancel_case1.old_qty_sum_for_all_levels , lCurrentTickObject.mod_cancel_case1.distance_between_new_price_old_price_sum ,\
                                    lCurrentTickObject.mod_cancel_case1.new_price_sum[0]  ,lCurrentTickObject.mod_cancel_case1.new_price_qty_sum[0] , lCurrentTickObject.mod_cancel_case1.new_price_sum[1]  ,lCurrentTickObject.mod_cancel_case1.new_price_qty_sum[1],\
                                    lCurrentTickObject.mod_cancel_case1.new_price_sum[2]  ,lCurrentTickObject.mod_cancel_case1.new_price_qty_sum[2],lCurrentTickObject.mod_cancel_case1.new_price_sum[3]  ,lCurrentTickObject.mod_cancel_case1.new_price_qty_sum[3],\
                                    lCurrentTickObject.mod_cancel_case1.new_price_sum[4]  ,lCurrentTickObject.mod_cancel_case1.new_price_qty_sum[4],
                                    lCurrentTickObject.mod_cancel_case1.old_price_sum[0]  ,lCurrentTickObject.mod_cancel_case1.old_price_qty_sum[0] , lCurrentTickObject.mod_cancel_case1.old_price_sum[1]  ,lCurrentTickObject.mod_cancel_case1.old_price_qty_sum[1],\
                                    lCurrentTickObject.mod_cancel_case1.old_price_sum[2]  ,lCurrentTickObject.mod_cancel_case1.old_price_qty_sum[2],lCurrentTickObject.mod_cancel_case1.old_price_sum[3]  ,lCurrentTickObject.mod_cancel_case1.old_price_qty_sum[3],\
                                    lCurrentTickObject.mod_cancel_case1.old_price_sum[4]  ,lCurrentTickObject.mod_cancel_case1.old_price_qty_sum[4],  \
                                    lCurrentTickObject.mod_cancel_case2.count, lCurrentTickObject.mod_cancel_case2.new_price_sum_for_all_levels , lCurrentTickObject.mod_cancel_case2.new_qty_sum_for_all_levels ,lCurrentTickObject.mod_cancel_case2.old_price_sum_for_all_levels , lCurrentTickObject.mod_cancel_case2.old_qty_sum_for_all_levels , lCurrentTickObject.mod_cancel_case2.distance_between_new_price_old_price_sum ,\
                                    lCurrentTickObject.mod_cancel_case2.new_price_sum[0]  ,lCurrentTickObject.mod_cancel_case2.new_price_qty_sum[0] , lCurrentTickObject.mod_cancel_case2.new_price_sum[1]  ,lCurrentTickObject.mod_cancel_case2.new_price_qty_sum[1],\
                                    lCurrentTickObject.mod_cancel_case2.new_price_sum[2]  ,lCurrentTickObject.mod_cancel_case2.new_price_qty_sum[2],lCurrentTickObject.mod_cancel_case2.new_price_sum[3]  ,lCurrentTickObject.mod_cancel_case2.new_price_qty_sum[3],\
                                    lCurrentTickObject.mod_cancel_case2.new_price_sum[4]  ,lCurrentTickObject.mod_cancel_case2.new_price_qty_sum[4],
                                    lCurrentTickObject.mod_cancel_case2.old_price_sum[0]  ,lCurrentTickObject.mod_cancel_case2.old_price_qty_sum[0] , lCurrentTickObject.mod_cancel_case2.old_price_sum[1]  ,lCurrentTickObject.mod_cancel_case2.old_price_qty_sum[1],\
                                    lCurrentTickObject.mod_cancel_case2.old_price_sum[2]  ,lCurrentTickObject.mod_cancel_case2.old_price_qty_sum[2],lCurrentTickObject.mod_cancel_case2.old_price_sum[3]  ,lCurrentTickObject.mod_cancel_case2.old_price_qty_sum[3],\
                                    lCurrentTickObject.mod_cancel_case2.old_price_sum[4]  ,lCurrentTickObject.mod_cancel_case2.old_price_qty_sum[4],  \
                                    lCurrentTickObject.mod_new_case1.new_price_sum[0]  ,lCurrentTickObject.mod_new_case1.new_price_qty_sum[0] , lCurrentTickObject.mod_new_case1.new_price_sum[1]  ,lCurrentTickObject.mod_new_case1.new_price_qty_sum[1],\
                                    lCurrentTickObject.mod_new_case1.new_price_sum[2]  ,lCurrentTickObject.mod_new_case1.new_price_qty_sum[2],lCurrentTickObject.mod_new_case1.new_price_sum[3]  ,lCurrentTickObject.mod_new_case1.new_price_qty_sum[3],\
                                    lCurrentTickObject.mod_new_case1.new_price_sum[4]  ,lCurrentTickObject.mod_new_case1.new_price_qty_sum[4],
                                    lCurrentTickObject.mod_new_case1.old_price_sum[0]  ,lCurrentTickObject.mod_new_case1.old_price_qty_sum[0] , lCurrentTickObject.mod_new_case1.old_price_sum[1]  ,lCurrentTickObject.mod_new_case1.old_price_qty_sum[1],\
                                    lCurrentTickObject.mod_new_case1.old_price_sum[2]  ,lCurrentTickObject.mod_new_case1.old_price_qty_sum[2],lCurrentTickObject.mod_new_case1.old_price_sum[3]  ,lCurrentTickObject.mod_new_case1.old_price_qty_sum[3],\
                                    lCurrentTickObject.mod_new_case1.old_price_sum[4]  ,lCurrentTickObject.mod_new_case1.old_price_qty_sum[4],  \
                                    lCurrentTickObject.mod_new_case2.count, lCurrentTickObject.mod_new_case2.new_price_sum_for_all_levels , lCurrentTickObject.mod_new_case2.new_qty_sum_for_all_levels ,lCurrentTickObject.mod_new_case2.old_price_sum_for_all_levels , lCurrentTickObject.mod_new_case2.old_qty_sum_for_all_levels , lCurrentTickObject.mod_new_case2.distance_between_new_price_old_price_sum ,\
                                    lCurrentTickObject.mod_new_case2.new_price_sum[0]  ,lCurrentTickObject.mod_new_case2.new_price_qty_sum[0] , lCurrentTickObject.mod_new_case2.new_price_sum[1]  ,lCurrentTickObject.mod_new_case2.new_price_qty_sum[1],\
                                    lCurrentTickObject.mod_new_case2.new_price_sum[2]  ,lCurrentTickObject.mod_new_case2.new_price_qty_sum[2],lCurrentTickObject.mod_new_case2.new_price_sum[3]  ,lCurrentTickObject.mod_new_case2.new_price_qty_sum[3],\
                                    lCurrentTickObject.mod_new_case2.new_price_sum[4]  ,lCurrentTickObject.mod_new_case2.new_price_qty_sum[4],
                                    lCurrentTickObject.mod_new_case2.old_price_sum[0]  ,lCurrentTickObject.mod_new_case2.old_price_qty_sum[0] , lCurrentTickObject.mod_new_case2.old_price_sum[1]  ,lCurrentTickObject.mod_new_case2.old_price_qty_sum[1],\
                                    lCurrentTickObject.mod_new_case2.old_price_sum[2]  ,lCurrentTickObject.mod_new_case2.old_price_qty_sum[2],lCurrentTickObject.mod_new_case2.old_price_sum[3]  ,lCurrentTickObject.mod_new_case2.old_price_qty_sum[3],\
                                    lCurrentTickObject.mod_new_case2.old_price_sum[4]  ,lCurrentTickObject.mod_new_case2.old_price_qty_sum[4], \
                                    lCurrentTickObject.mod_new_case3.count, lCurrentTickObject.mod_new_case3.new_price_sum_for_all_levels , lCurrentTickObject.mod_new_case3.new_qty_sum_for_all_levels ,lCurrentTickObject.mod_new_case3.old_price_sum_for_all_levels , lCurrentTickObject.mod_new_case3.old_qty_sum_for_all_levels , lCurrentTickObject.mod_new_case3.distance_between_new_price_old_price_sum ,\
                                    lCurrentTickObject.mod_new_case3.new_price_sum[0]  ,lCurrentTickObject.mod_new_case3.new_price_qty_sum[0] , lCurrentTickObject.mod_new_case3.new_price_sum[1]  ,lCurrentTickObject.mod_new_case3.new_price_qty_sum[1],\
                                    lCurrentTickObject.mod_new_case3.new_price_sum[2]  ,lCurrentTickObject.mod_new_case3.new_price_qty_sum[2],lCurrentTickObject.mod_new_case3.new_price_sum[3]  ,lCurrentTickObject.mod_new_case3.new_price_qty_sum[3],\
                                    lCurrentTickObject.mod_new_case3.new_price_sum[4]  ,lCurrentTickObject.mod_new_case3.new_price_qty_sum[4],
                                    lCurrentTickObject.mod_new_case3.old_price_sum[0]  ,lCurrentTickObject.mod_new_case3.old_price_qty_sum[0] , lCurrentTickObject.mod_new_case3.old_price_sum[1]  ,lCurrentTickObject.mod_new_case3.old_price_qty_sum[1],\
                                    lCurrentTickObject.mod_new_case3.old_price_sum[2]  ,lCurrentTickObject.mod_new_case3.old_price_qty_sum[2],lCurrentTickObject.mod_new_case3.old_price_sum[3]  ,lCurrentTickObject.mod_new_case3.old_price_qty_sum[3],\
                                    lCurrentTickObject.mod_new_case3.old_price_sum[4]  ,lCurrentTickObject.mod_new_case3.old_price_qty_sum[4],  \
                                    lCurrentTickObject.mod_case_normal.count, lCurrentTickObject.mod_case_normal.new_price_sum_for_all_levels , lCurrentTickObject.mod_case_normal.new_qty_sum_for_all_levels ,lCurrentTickObject.mod_case_normal.old_price_sum_for_all_levels , lCurrentTickObject.mod_case_normal.old_qty_sum_for_all_levels , lCurrentTickObject.mod_case_normal.distance_between_new_price_old_price_sum ,\
                                    lCurrentTickObject.mod_case_normal.new_price_sum[0]  ,lCurrentTickObject.mod_case_normal.new_price_qty_sum[0] , lCurrentTickObject.mod_case_normal.new_price_sum[1]  ,lCurrentTickObject.mod_case_normal.new_price_qty_sum[1],\
                                    lCurrentTickObject.mod_case_normal.new_price_sum[2]  ,lCurrentTickObject.mod_case_normal.new_price_qty_sum[2],lCurrentTickObject.mod_case_normal.new_price_sum[3]  ,lCurrentTickObject.mod_case_normal.new_price_qty_sum[3],\
                                    lCurrentTickObject.mod_case_normal.new_price_sum[4]  ,lCurrentTickObject.mod_case_normal.new_price_qty_sum[4],
                                    lCurrentTickObject.mod_case_normal.old_price_sum[0]  ,lCurrentTickObject.mod_case_normal.old_price_qty_sum[0] , lCurrentTickObject.mod_case_normal.old_price_sum[1]  ,lCurrentTickObject.mod_case_normal.old_price_qty_sum[1],\
                                    lCurrentTickObject.mod_case_normal.old_price_sum[2]  ,lCurrentTickObject.mod_case_normal.old_price_qty_sum[2],lCurrentTickObject.mod_case_normal.old_price_sum[3]  ,lCurrentTickObject.mod_case_normal.old_price_qty_sum[3],\
                                    lCurrentTickObject.mod_case_normal.old_price_sum[4]  ,lCurrentTickObject.mod_case_normal.old_price_qty_sum[4]]
            attribute.aList[currentRowNumberForWhichFeatureValueIsBeingCalculated][2] = ";".join(map(str,lListOfValuesToPrint))            

            queueOfValuesInLastNSecs.append([lCurrentTickObject,timeOfCurrentRow])
            numberOfRowsInLastNSecs += 1   # Every append gets a +1 
            currentRowNumberForWhichFeatureValueIsBeingCalculated += 1
            continue     # Since we are going back 1 row from current we cannot get data from current row
        
        else:
            # We need to reset the timeOfOldestRow since timeElapsed has exceeded N seconds
            while(timeElapsed >= N):
                if(len(queueOfValuesInLastNSecs) == 0):
                    timeOfOldestRow = timeOfCurrentRow
                    timeElapsed = 0
                    if(numberOfRowsInLastNSecs != 0):
                        print "Sanity check: This condition is not possible logically. numberOfRowsInLastNSecs should been 0. There has been an unknown error"
                        sys.exit(-1)
                else:   
                    oldestElementInQueue = queueOfValuesInLastNSecs.popleft()
                    colValueInOldestElementInQueue = oldestElementInQueue[0]
                    colTimeStampInOldestElementInQueue = oldestElementInQueue[1]
                    updateTickDeletionFromQueue(colValueInOldestElementInQueue , buyOrSellSide , tickSize , g_data_file_values_to_be_stored)
                    timeOfOldestRow = colTimeStampInOldestElementInQueue
                    numberOfRowsInLastNSecs -= 1 # every pop from the queue gets a -1
                    timeElapsed = timeOfCurrentRow - timeOfOldestRow
                    if(len(queueOfValuesInLastNSecs) != numberOfRowsInLastNSecs):
                        print "Sanity check: This condition is not possible logically. There has been an unknown error"
                        sys.exit(-1)
        
        print "Processed row number " + str(currentRowNumberForWhichFeatureValueIsBeingCalculated)

#     lNameOfFeaturePrinted = "fNumberOfEventsOccuredInCol" +args.c + "InLast" + str(args.n) + "Secs" 
    return [ "TimeStamp", "TimeElapsed" , "Price0;Price1;Price2;Price3;Price4" , "Qty0;Qty1;Qty2;Qty3;Qty4","MsgCode","OrderType","NewP","NewQ","OldP","OldQ","lEventOccured",\
            "NEW_WITH_PRICE_CHANGE-Count","NEW_WITH_PRICE_CHANGE-NewPriceSum" , "NEW_WITH_PRICE_CHANGE-NewQtySum","NEW_WITH_PRICE_CHANGE-PriceAtIndex0sum","NEW_WITH_PRICE_CHANGE-QtyAtIndex0sum","NEW_WITH_PRICE_CHANGE-PriceAtIndex1sum","NEW_WITH_PRICE_CHANGE-QtyAtIndex1sum","NEW_WITH_PRICE_CHANGE-PriceAtIndex2sum","NEW_WITH_PRICE_CHANGE-QtyAtIndex2sum","NEW_WITH_PRICE_CHANGE-PriceAtIndex3sum","NEW_WITH_PRICE_CHANGE-QtyAtIndex3sum","NEW_WITH_PRICE_CHANGE-PriceAtIndex4sum","NEW_WITH_PRICE_CHANGE-QtyAtIndex4sum",
            "NEW_WITHOUT_PRICE_CHANGE-Count","NEW_WITHOUT_PRICE_CHANGE-NewPriceSum" , "NEW_WITHOUT_PRICE_CHANGE-NewQtySum","NEW_WITHOUT_PRICE_CHANGE-PriceAtIndex0sum","NEW_WITHOUT_PRICE_CHANGE-QtyAtIndex0sum","NEW_WITHOUT_PRICE_CHANGE-PriceAtIndex1sum","NEW_WITHOUT_PRICE_CHANGE-QtyAtIndex1sum","NEW_WITHOUT_PRICE_CHANGE-PriceAtIndex2sum","NEW_WITHOUT_PRICE_CHANGE-QtyAtIndex2sum","NEW_WITHOUT_PRICE_CHANGE-PriceAtIndex3sum","NEW_WITHOUT_PRICE_CHANGE-QtyAtIndex3sum","NEW_WITHOUT_PRICE_CHANGE-PriceAtIndex4sum","NEW_WITHOUT_PRICE_CHANGE-QtyAtIndex4sum",
            "CANCEL_WITH_PRICE_CHANGE-Count","CANCEL_WITH_PRICE_CHANGE-NewPriceSum" , "CANCEL_WITH_PRICE_CHANGE-NewQtySum","CANCEL_WITH_PRICE_CHANGE-PriceAtIndex0sum","CANCEL_WITH_PRICE_CHANGE-QtyAtIndex0sum","CANCEL_WITH_PRICE_CHANGE-PriceAtIndex1sum","CANCEL_WITH_PRICE_CHANGE-QtyAtIndex1sum","CANCEL_WITH_PRICE_CHANGE-PriceAtIndex2sum","CANCEL_WITH_PRICE_CHANGE-QtyAtIndex2sum","CANCEL_WITH_PRICE_CHANGE-PriceAtIndex3sum","CANCEL_WITH_PRICE_CHANGE-QtyAtIndex3sum","CANCEL_WITH_PRICE_CHANGE-PriceAtIndex4sum","CANCEL_WITH_PRICE_CHANGE-QtyAtIndex4sum",
            "CANCEL_WITHOUT_PRICE_CHANGE-Count","CANCEL_WITHOUT_PRICE_CHANGE-NewPriceSum" , "CANCEL_WITHOUT_PRICE_CHANGE-NewQtySum","CANCEL_WITHOUT_PRICE_CHANGE-PriceAtIndex0sum","CANCEL_WITHOUT_PRICE_CHANGE-QtyAtIndex0sum","CANCEL_WITHOUT_PRICE_CHANGE-PriceAtIndex1sum","CANCEL_WITHOUT_PRICE_CHANGE-QtyAtIndex1sum","CANCEL_WITHOUT_PRICE_CHANGE-PriceAtIndex2sum","CANCEL_WITHOUT_PRICE_CHANGE-QtyAtIndex2sum","CANCEL_WITHOUT_PRICE_CHANGE-PriceAtIndex3sum","CANCEL_WITHOUT_PRICE_CHANGE-QtyAtIndex3sum","CANCEL_WITHOUT_PRICE_CHANGE-PriceAtIndex4sum","CANCEL_WITHOUT_PRICE_CHANGE-QtyAtIndex4sum",
            "TRADE_WITH_PRICE_CHANGE-Count","TRADE_WITH_PRICE_CHANGE-NewPriceSum" , "TRADE_WITH_PRICE_CHANGE-NewQtySum","TRADE_WITH_PRICE_CHANGE-PriceAtIndex0sum","TRADE_WITH_PRICE_CHANGE-QtyAtIndex0sum","TRADE_WITH_PRICE_CHANGE-PriceAtIndex1sum","TRADE_WITH_PRICE_CHANGE-QtyAtIndex1sum","TRADE_WITH_PRICE_CHANGE-PriceAtIndex2sum","TRADE_WITH_PRICE_CHANGE-QtyAtIndex2sum","TRADE_WITH_PRICE_CHANGE-PriceAtIndex3sum","TRADE_WITH_PRICE_CHANGE-QtyAtIndex3sum","TRADE_WITH_PRICE_CHANGE-PriceAtIndex4sum","TRADE_WITH_PRICE_CHANGE-QtyAtIndex4sum",
            "TRADE_WITHOUT_PRICE_CHANGE-Count","TRADE_WITHOUT_PRICE_CHANGE-NewPriceSum" , "TRADE_WITHOUT_PRICE_CHANGE-NewQtySum","TRADE_WITHOUT_PRICE_CHANGE-PriceAtIndex0sum","TRADE_WITHOUT_PRICE_CHANGE-QtyAtIndex0sum","TRADE_WITHOUT_PRICE_CHANGE-PriceAtIndex1sum","TRADE_WITHOUT_PRICE_CHANGE-QtyAtIndex1sum","TRADE_WITHOUT_PRICE_CHANGE-PriceAtIndex2sum","TRADE_WITHOUT_PRICE_CHANGE-QtyAtIndex2sum","TRADE_WITHOUT_PRICE_CHANGE-PriceAtIndex3sum","TRADE_WITHOUT_PRICE_CHANGE-QtyAtIndex3sum","TRADE_WITHOUT_PRICE_CHANGE-PriceAtIndex4sum","TRADE_WITHOUT_PRICE_CHANGE-QtyAtIndex4sum",
            "MOD_CANCEL_CASE1-Count","MOD_CANCEL_CASE1-NewPriceSum" , "MOD_CANCEL_CASE1-NewQtySum","MOD_CANCEL_CASE1-OldPriceSum" , "MOD_CANCEL_CASE1-OldQtySum","MOD_CANCEL_CASE1-DistanceBetweenNewPrcieOldPriceSum","MOD_CANCEL_CASE1-NewPriceAtIndex0sum","MOD_CANCEL_CASE1-NewQtyAtIndex0sum","MOD_CANCEL_CASE1-NewPriceAtIndex1sum","MOD_CANCEL_CASE1-NewQtyAtIndex1sum","MOD_CANCEL_CASE1-NewPriceAtIndex2sum","MOD_CANCEL_CASE1-NewQtyAtIndex2sum","MOD_CANCEL_CASE1-NewPriceAtIndex3sum","MOD_CANCEL_CASE1-NewQtyAtIndex3sum","MOD_CANCEL_CASE1-NewPriceAtIndex4sum","MOD_CANCEL_CASE1-NewQtyAtIndex4sum",
            "MOD_CANCEL_CASE1-OldQtySum","MOD_CANCEL_CASE1-OldPriceAtIndex0sum","MOD_CANCEL_CASE1-OldQtyAtIndex0sum","MOD_CANCEL_CASE1-OldPriceAtIndex1sum","MOD_CANCEL_CASE1-OldQtyAtIndex1sum","MOD_CANCEL_CASE1-OldPriceAtIndex2sum","MOD_CANCEL_CASE1-OldQtyAtIndex2sum","MOD_CANCEL_CASE1-OldPriceAtIndex3sum","MOD_CANCEL_CASE1-OldQtyAtIndex3sum","MOD_CANCEL_CASE1-OldPriceAtIndex4sum","MOD_CANCEL_CASE1-OldQtyAtIndex4sum",
            "MOD_CANCEL_CASE2-Count","MOD_CANCEL_CASE2-NewPriceSum" , "MOD_CANCEL_CASE2-NewQtySum","MOD_CANCEL_CASE2-OldPriceSum" , "MOD_CANCEL_CASE2-OldQtySum","MOD_CANCEL_CASE2-DistanceBetweenNewPrcieOldPriceSum","MOD_CANCEL_CASE2-NewPriceAtIndex0sum","MOD_CANCEL_CASE2-NewQtyAtIndex0sum","MOD_CANCEL_CASE2-NewPriceAtIndex1sum","MOD_CANCEL_CASE2-NewQtyAtIndex1sum","MOD_CANCEL_CASE2-NewPriceAtIndex2sum","MOD_CANCEL_CASE2-NewQtyAtIndex2sum","MOD_CANCEL_CASE2-NewPriceAtIndex3sum","MOD_CANCEL_CASE2-NewQtyAtIndex3sum","MOD_CANCEL_CASE2-NewPriceAtIndex4sum","MOD_CANCEL_CASE2-NewQtyAtIndex4sum",
            "MOD_CANCEL_CASE2-OldQtySum","MOD_CANCEL_CASE2-OldPriceAtIndex0sum","MOD_CANCEL_CASE2-OldQtyAtIndex0sum","MOD_CANCEL_CASE2-OldPriceAtIndex1sum","MOD_CANCEL_CASE2-OldQtyAtIndex1sum","MOD_CANCEL_CASE2-OldPriceAtIndex2sum","MOD_CANCEL_CASE2-OldQtyAtIndex2sum","MOD_CANCEL_CASE2-OldPriceAtIndex3sum","MOD_CANCEL_CASE2-OldQtyAtIndex3sum","MOD_CANCEL_CASE2-OldPriceAtIndex4sum","MOD_CANCEL_CASE2-OldQtyAtIndex4sum",
            "MOD_NEW_CASE1-Count","MOD_NEW_CASE1-NewPriceSum" , "MOD_NEW_CASE1-NewQtySum","MOD_NEW_CASE1-OldPriceSum" , "MOD_NEW_CASE1-OldQtySum","MOD_NEW_CASE1-DistanceBetweenNewPrcieOldPriceSum","MOD_NEW_CASE1-NewPriceAtIndex0sum","MOD_NEW_CASE1-NewQtyAtIndex0sum","MOD_NEW_CASE1-NewPriceAtIndex1sum","MOD_NEW_CASE1-NewQtyAtIndex1sum","MOD_NEW_CASE1-NewPriceAtIndex2sum","MOD_NEW_CASE1-NewQtyAtIndex2sum","MOD_NEW_CASE1-NewPriceAtIndex3sum","MOD_NEW_CASE1-NewQtyAtIndex3sum","MOD_NEW_CASE1-NewPriceAtIndex4sum","MOD_NEW_CASE1-NewQtyAtIndex4sum",
            "MOD_NEW_CASE1-OldQtySum","MOD_NEW_CASE1-OldPriceAtIndex0sum","MOD_NEW_CASE1-OldQtyAtIndex0sum","MOD_NEW_CASE1-OldPriceAtIndex1sum","MOD_NEW_CASE1-OldQtyAtIndex1sum","MOD_NEW_CASE1-OldPriceAtIndex2sum","MOD_NEW_CASE1-OldQtyAtIndex2sum","MOD_NEW_CASE1-OldPriceAtIndex3sum","MOD_NEW_CASE1-OldQtyAtIndex3sum","MOD_NEW_CASE1-OldPriceAtIndex4sum","MOD_NEW_CASE1-OldQtyAtIndex4sum",
            "MOD_NEW_CASE2-Count","MOD_NEW_CASE2-NewPriceSum" , "MOD_NEW_CASE2-NewQtySum","MOD_NEW_CASE2-OldPriceSum" , "MOD_NEW_CASE2-OldQtySum","MOD_NEW_CASE2-DistanceBetweenNewPrcieOldPriceSum","MOD_NEW_CASE2-NewPriceAtIndex0sum","MOD_NEW_CASE2-NewQtyAtIndex0sum","MOD_NEW_CASE2-NewPriceAtIndex1sum","MOD_NEW_CASE2-NewQtyAtIndex1sum","MOD_NEW_CASE2-NewPriceAtIndex2sum","MOD_NEW_CASE2-NewQtyAtIndex2sum","MOD_NEW_CASE2-NewPriceAtIndex3sum","MOD_NEW_CASE2-NewQtyAtIndex3sum","MOD_NEW_CASE2-NewPriceAtIndex4sum","MOD_NEW_CASE2-NewQtyAtIndex4sum",
            "MOD_NEW_CASE2-OldQtySum","MOD_NEW_CASE2-OldPriceAtIndex0sum","MOD_NEW_CASE2-OldQtyAtIndex0sum","MOD_NEW_CASE2-OldPriceAtIndex1sum","MOD_NEW_CASE2-OldQtyAtIndex1sum","MOD_NEW_CASE2-OldPriceAtIndex2sum","MOD_NEW_CASE2-OldQtyAtIndex2sum","MOD_NEW_CASE2-OldPriceAtIndex3sum","MOD_NEW_CASE2-OldQtyAtIndex3sum","MOD_NEW_CASE2-OldPriceAtIndex4sum","MOD_NEW_CASE2-OldQtyAtIndex4sum",
            "MOD_NEW_CASE3-Count","MOD_NEW_CASE3-NewPriceSum" , "MOD_NEW_CASE3-NewQtySum","MOD_NEW_CASE3-OldPriceSum" , "MOD_NEW_CASE3-OldQtySum","MOD_NEW_CASE3-DistanceBetweenNewPrcieOldPriceSum","MOD_NEW_CASE3-NewPriceAtIndex0sum","MOD_NEW_CASE3-NewQtyAtIndex0sum","MOD_NEW_CASE3-NewPriceAtIndex1sum","MOD_NEW_CASE3-NewQtyAtIndex1sum","MOD_NEW_CASE3-NewPriceAtIndex2sum","MOD_NEW_CASE3-NewQtyAtIndex2sum","MOD_NEW_CASE3-NewPriceAtIndex3sum","MOD_NEW_CASE3-NewQtyAtIndex3sum","MOD_NEW_CASE3-NewPriceAtIndex4sum","MOD_NEW_CASE3-NewQtyAtIndex4sum",
            "MOD_NEW_CASE3-OldQtySum","MOD_NEW_CASE3-OldPriceAtIndex0sum","MOD_NEW_CASE3-OldQtyAtIndex0sum","MOD_NEW_CASE3-OldPriceAtIndex1sum","MOD_NEW_CASE3-OldQtyAtIndex1sum","MOD_NEW_CASE3-OldPriceAtIndex2sum","MOD_NEW_CASE3-OldQtyAtIndex2sum","MOD_NEW_CASE3-OldPriceAtIndex3sum","MOD_NEW_CASE3-OldQtyAtIndex3sum","MOD_NEW_CASE3-OldPriceAtIndex4sum","MOD_NEW_CASE3-OldQtyAtIndex4sum",
            "NORMAL_MOD_CASE-Count","NORMAL_MOD_CASE-NewPriceSum" , "NORMAL_MOD_CASE-NewQtySum","NORMAL_MOD_CASE-OldPriceSum" , "NORMAL_MOD_CASE-OldQtySum","NORMAL_MOD_CASE-DistanceBetweenNewPrcieOldPriceSum","NORMAL_MOD_CASE-NewPriceAtIndex0sum","NORMAL_MOD_CASE-NewQtyAtIndex0sum","NORMAL_MOD_CASE-NewPriceAtIndex1sum","NORMAL_MOD_CASE-NewQtyAtIndex1sum","NORMAL_MOD_CASE-NewPriceAtIndex2sum","NORMAL_MOD_CASE-NewQtyAtIndex2sum","NORMAL_MOD_CASE-NewPriceAtIndex3sum","NORMAL_MOD_CASE-NewQtyAtIndex3sum","NORMAL_MOD_CASE-NewPriceAtIndex4sum","NORMAL_MOD_CASE-NewQtyAtIndex4sum",
            "NORMAL_MOD_CASE-OldQtySum","NORMAL_MOD_CASE-OldPriceAtIndex0sum","NORMAL_MOD_CASE-OldQtyAtIndex0sum","NORMAL_MOD_CASE-OldPriceAtIndex1sum","NORMAL_MOD_CASE-OldQtyAtIndex1sum","NORMAL_MOD_CASE-OldPriceAtIndex2sum","NORMAL_MOD_CASE-OldQtyAtIndex2sum","NORMAL_MOD_CASE-OldPriceAtIndex3sum","NORMAL_MOD_CASE-OldQtyAtIndex3sum","NORMAL_MOD_CASE-OldPriceAtIndex4sum","NORMAL_MOD_CASE-OldQtyAtIndex4sum",
            ]
            
