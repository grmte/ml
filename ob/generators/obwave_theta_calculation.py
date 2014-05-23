import fObwaveHistValueOfColCInLastNSecs as dd

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def calculate_current_wt_sum_for_theta_calculation(p_list, p_weight_list):
    l_index = 0
    l_sum_of_current_wt = 0
    while l_index < len(p_list):
        l_sum_of_current_wt += (p_weight_list[l_index] * p_list[l_index])
        l_index += 1
    return l_sum_of_current_wt

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def calculate_historical_weighted_Price_for_theta(p_cancel_Price_list, p_cancel_qty_list, p_weight_list,p_dict_sum_for_price):
    
    l_current_price_list = list(p_cancel_Price_list)
    p_current_quantity_list = list(p_cancel_qty_list)
    l_index = 0
    l_sum_qty_for_avg_cal = 0
    while l_index < len(p_current_quantity_list):
        l_sum_qty_for_avg_cal += (p_weight_list[l_index] * p_current_quantity_list[l_index])
        l_index += 1
#    l_hist_sum_price_list = [sum([dd.g_list_of_dict_for_market_shift_qty_price_Ask[line][l_current_price] for line in range(p_len)]) for l_current_price in l_current_AskP_list]
    lPriceIndex = 0
    l_hist_sum_price_list = []
    for l_current_price in l_current_price_list:
        l_hist_sum_price_list.append(lPriceIndex)
        l_hist_sum_price_list[lPriceIndex] = p_dict_sum_for_price[l_current_price]
        lPriceIndex += 1 
    l_index_for_hist_sum = 0
    while l_index_for_hist_sum < len(l_hist_sum_price_list):
        l_sum_qty_for_avg_cal += (p_weight_list[l_index_for_hist_sum] * l_hist_sum_price_list[l_index_for_hist_sum])
        l_index_for_hist_sum += 1
    
    return l_sum_qty_for_avg_cal
        

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def calculate_theta_for_mod_new_case1(p_len,p_curr_Price_list,p_prev_Price_list,p_curr_quantity_list,p_prev_quantity_list,p_cur_NewQ ,p_cur_NewP ,  p_dict_sum_for_price):
    '''
    DOC:
        if (l_new_mod_price in l_current_AskP_list and l_new_mod_price not in p_prev_Price_list) and (l_old_mod_price in l_current_AskP_list and l_old_mod_price in p_prev_Price_list):
        Tick        Q0      P0      Q1      P1      Q2      P2      Q3      P3        Q4      P4                NQ     NP        OQ       OP
        1           200    628625   300    628615   600    628610   200    628605    300    628600
        2           150    628630   50    628625    300    628615   600    628610    200    628605    M    B    150    628630    150    628625
    '''
    #LHS
    #========================================================================================
    l_LHS_weight_list = []
    l_LHS_current_AskQ_list = [p_prev_quantity_list[0], p_prev_quantity_list[1], 
                               p_prev_quantity_list[2], p_prev_quantity_list[3], 
                               p_prev_quantity_list[4]]
    
    l_LHS_current_AskP_list = [p_prev_Price_list[0], p_prev_Price_list[1], 
                               p_prev_Price_list[2], p_prev_Price_list[3], 
                               p_prev_Price_list[4]]
    
    l_LHS_weight_list = [dd.g_weight_list[p_prev_Price_list.index(p_prev_Price_list[0])],
                         dd.g_weight_list[p_prev_Price_list.index(p_prev_Price_list[1])],
                         dd.g_weight_list[p_prev_Price_list.index(p_prev_Price_list[2])],
                         dd.g_weight_list[p_prev_Price_list.index(p_prev_Price_list[3])],
                         dd.g_weight_list[p_prev_Price_list.index(p_prev_Price_list[4])]]
    
    l_LHS_current_weighted_sum = calculate_current_wt_sum_for_theta_calculation(l_LHS_current_AskQ_list, l_LHS_weight_list)
    l_LHS_history_weighted_sum = calculate_historical_weighted_Price_for_theta(l_LHS_current_AskP_list, l_LHS_current_AskQ_list, l_LHS_weight_list , p_dict_sum_for_price)
    l_LHS_history_weighted_avg = float(l_LHS_history_weighted_sum) / (p_len + 1)
    l_LHS_ratio = float(l_LHS_current_weighted_sum) / l_LHS_history_weighted_avg
    l_LHS_ratio = min(max(l_LHS_ratio, dd.g_lower_cutoff_for_LHS), dd.g_upper_cutoff_for_LHS)
    #========================================================================================
    
    #RHS
    #========================================================================================
    l_RHS_weight_list = []
    l_RHS_current_AskQ_list = [p_prev_quantity_list[0], p_prev_quantity_list[1], 
                               p_prev_quantity_list[2], p_prev_quantity_list[3]]
    
    l_RHS_current_AskP_list = [p_prev_Price_list[0], p_prev_Price_list[1], 
                               p_prev_Price_list[2], p_prev_Price_list[3]]
    
    l_RHS_weight_list = [dd.g_weight_list[p_curr_Price_list.index(p_prev_Price_list[0])],
                         dd.g_weight_list[p_curr_Price_list.index(p_prev_Price_list[1])],
                         dd.g_weight_list[p_curr_Price_list.index(p_prev_Price_list[2])],
                         dd.g_weight_list[p_curr_Price_list.index(p_prev_Price_list[3])]]
    
    l_RHS_current_weighted_sum = calculate_current_wt_sum_for_theta_calculation(l_RHS_current_AskQ_list, l_RHS_weight_list) 
    
    l_RHS_history_weighted_sum = calculate_historical_weighted_Price_for_theta(l_RHS_current_AskP_list, l_RHS_current_AskQ_list, l_RHS_weight_list , p_dict_sum_for_price)
    l_RHS_history_weighted_avg = float(l_RHS_history_weighted_sum) / (p_len + 1)
    #========================================================================================
    
    c = (1 / float(p_cur_NewQ * dd.g_weight_list[p_curr_Price_list.index(p_cur_NewP)])) * ((float(l_RHS_current_weighted_sum) / l_LHS_ratio) - l_RHS_history_weighted_avg)
    new_theta = max(0, ((p_len + 1) * c - 1) / float(p_len))
    new_theta = min(dd.g_theta_upper , new_theta)
    
    return new_theta

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def calculate_theta_for_mod_new_case2(p_len,p_curr_Price_list,p_prev_Price_list,p_curr_quantity_list,p_prev_quantity_list, p_cur_NewQ ,p_cur_NewP , p_dict_sum_for_price):
    '''
    DOC:
        if (l_old_mod_price not in p_prev_Price_list) and (l_new_mod_price in l_current_AskP_list and l_new_mod_price not in p_prev_Price_list) :
        Tick     Q0      P0        Q1     P1        Q2    P2        Q3     P3        Q4     P4
        1        2500    628300    150    628330    50    628335    100    628515    100    628670
        2        2500    628300    150    628330    50    628335    100    628515    100    628615 N    S    100    628615
    '''
    #LHS
    #========================================================================================
    l_LHS_weight_list = []
    l_index_of_added_qty = p_curr_Price_list.index(p_cur_NewP)
    
    l_LHS_current_AskQ_list = [p_prev_quantity_list[0], p_prev_quantity_list[1], 
                               p_prev_quantity_list[2], p_prev_quantity_list[3], 
                               p_prev_quantity_list[4]]
    
    l_LHS_current_AskQ_list[l_index_of_added_qty] += p_cur_NewQ
    
    l_LHS_current_AskP_list = [p_prev_Price_list[0], p_prev_Price_list[1], 
                               p_prev_Price_list[2], p_prev_Price_list[3], 
                               p_prev_Price_list[4]]
    
    l_LHS_weight_list = [dd.g_weight_list[p_prev_Price_list.index(p_prev_Price_list[0])],
                         dd.g_weight_list[p_prev_Price_list.index(p_prev_Price_list[1])],
                         dd.g_weight_list[p_prev_Price_list.index(p_prev_Price_list[2])],
                         dd.g_weight_list[p_prev_Price_list.index(p_prev_Price_list[3])],
                         dd.g_weight_list[p_prev_Price_list.index(p_prev_Price_list[4])]]
    
    
    l_LHS_current_weighted_sum = calculate_current_wt_sum_for_theta_calculation(l_LHS_current_AskQ_list, l_LHS_weight_list)
                                
    l_LHS_history_weighted_sum = calculate_historical_weighted_Price_for_theta(l_LHS_current_AskP_list, l_LHS_current_AskQ_list, l_LHS_weight_list , p_dict_sum_for_price)
    l_LHS_history_weighted_avg = float(l_LHS_history_weighted_sum) / (p_len + 1)
    l_LHS_ratio = float(l_LHS_current_weighted_sum) / l_LHS_history_weighted_avg
    l_LHS_ratio = min(max(l_LHS_ratio, dd.g_lower_cutoff_for_LHS), dd.g_upper_cutoff_for_LHS)
    #========================================================================================
    
    #RHS
    #========================================================================================
    l_RHS_weight_list = []
    l_RHS_current_AskQ_list = [p_prev_quantity_list[0], p_prev_quantity_list[1], 
                               p_prev_quantity_list[2], p_prev_quantity_list[3]]
    
    l_RHS_current_AskP_list = [p_prev_Price_list[0], p_prev_Price_list[1], 
                               p_prev_Price_list[2], p_prev_Price_list[3]]
    
    l_RHS_weight_list = [dd.g_weight_list[p_curr_Price_list.index(p_prev_Price_list[0])],
                         dd.g_weight_list[p_curr_Price_list.index(p_prev_Price_list[1])],
                         dd.g_weight_list[p_curr_Price_list.index(p_prev_Price_list[2])],
                         dd.g_weight_list[p_curr_Price_list.index(p_prev_Price_list[3])]]
    
    l_RHS_current_weighted_sum = calculate_current_wt_sum_for_theta_calculation(l_RHS_current_AskQ_list, l_RHS_weight_list) + \
    (p_cur_NewQ * dd.g_weight_list[l_index_of_added_qty])
    
    l_RHS_history_weighted_sum = calculate_historical_weighted_Price_for_theta(l_RHS_current_AskP_list, l_RHS_current_AskQ_list, l_RHS_weight_list , p_dict_sum_for_price)
    l_RHS_history_weighted_avg = float(l_RHS_history_weighted_sum) / (p_len + 1)
    #========================================================================================
    
    c = (1 / float(p_cur_NewQ * \
        dd.g_weight_list[l_index_of_added_qty])) * \
        ((float(l_RHS_current_weighted_sum) / l_LHS_ratio) - l_RHS_history_weighted_avg)
        
    new_theta = max(0, ((p_len + 1) * c - 1) / float(p_len))
    new_theta = min(dd.g_theta_upper , new_theta)
    return new_theta
    
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def calculate_theta_for_mod_new_case3(p_len,p_curr_Price_list,p_prev_Price_list,p_curr_quantity_list,p_prev_quantity_list, p_cur_NewQ ,p_cur_NewP, p_curr_OldQ , p_curr_OldP, p_dict_sum_for_price):
    '''
    DOC:
        if (l_old_mod_price in p_prev_Price_list and l_old_mod_price not in l_current_AskP_list) and (l_new_mod_price in l_current_AskP_list and l_new_mod_price not in p_prev_Price_list):
        Tick     Q0      P0        Q1     P1        Q2    P2        Q3     P3        Q4     P4
        1        2500    628300    150    628330    50    628335    100    628515    100    628670
        2        2500    628300    150    628330    50    628335    100    628515    100    628615 M    S    100    628615
    '''
    #LHS
    #========================================================================================
    l_LHS_weight_list = []
    l_index_of_added_qty = p_curr_Price_list.index(p_cur_NewP)
    
    l_LHS_current_AskQ_list = [p_prev_quantity_list[0], p_prev_quantity_list[1], 
                               p_prev_quantity_list[2], p_prev_quantity_list[3], 
                               p_prev_quantity_list[4]]
    
    l_LHS_current_AskP_list = [p_prev_Price_list[0], p_prev_Price_list[1], 
                               p_prev_Price_list[2], p_prev_Price_list[3], 
                               p_prev_Price_list[4]]
    l_old_price_index = l_LHS_current_AskP_list.index(p_curr_OldP)
    l_LHS_current_AskQ_list[l_old_price_index] = p_curr_OldQ
    
    l_LHS_weight_list = [dd.g_weight_list[p_prev_Price_list.index(p_prev_Price_list[0])],
                         dd.g_weight_list[p_prev_Price_list.index(p_prev_Price_list[1])],
                         dd.g_weight_list[p_prev_Price_list.index(p_prev_Price_list[2])],
                         dd.g_weight_list[p_prev_Price_list.index(p_prev_Price_list[3])],
                         dd.g_weight_list[p_prev_Price_list.index(p_prev_Price_list[4])]]
    
    
    l_LHS_current_weighted_sum = calculate_current_wt_sum_for_theta_calculation(l_LHS_current_AskQ_list, l_LHS_weight_list)
                                
    l_LHS_history_weighted_sum = calculate_historical_weighted_Price_for_theta(l_LHS_current_AskP_list, l_LHS_current_AskQ_list, l_LHS_weight_list , p_dict_sum_for_price)
    l_LHS_history_weighted_avg = float(l_LHS_history_weighted_sum) / (p_len + 1)
    l_LHS_ratio = float(l_LHS_current_weighted_sum) / l_LHS_history_weighted_avg
    l_LHS_ratio = min(max(l_LHS_ratio, dd.g_lower_cutoff_for_LHS), dd.g_upper_cutoff_for_LHS)
    #========================================================================================
    
    #RHS
    #========================================================================================
    l_RHS_weight_list = []
    l_RHS_current_AskQ_list = [p_curr_quantity_list[0], p_curr_quantity_list[1], 
                               p_curr_quantity_list[2], p_curr_quantity_list[3],
                               p_curr_quantity_list[4]]
    
    del l_RHS_current_AskQ_list[l_index_of_added_qty]
    
    l_RHS_current_AskP_list = [p_curr_Price_list[0], p_curr_Price_list[1], 
                               p_curr_Price_list[2], p_curr_Price_list[3],
                               p_curr_Price_list[4]]
    
    del l_RHS_current_AskP_list[l_index_of_added_qty]
    
    l_RHS_weight_list = [dd.g_weight_list[p_curr_Price_list.index(p_curr_Price_list[0])],
                         dd.g_weight_list[p_curr_Price_list.index(p_curr_Price_list[1])],
                         dd.g_weight_list[p_curr_Price_list.index(p_curr_Price_list[2])],
                         dd.g_weight_list[p_curr_Price_list.index(p_curr_Price_list[3])],
                         dd.g_weight_list[p_curr_Price_list.index(p_curr_Price_list[4])]]
    
    del l_RHS_weight_list[l_index_of_added_qty]
    
    l_RHS_current_weighted_sum = calculate_current_wt_sum_for_theta_calculation(l_RHS_current_AskQ_list, l_RHS_weight_list) + \
    (p_cur_NewQ * dd.g_weight_list[l_index_of_added_qty])
    
    l_RHS_history_weighted_sum = calculate_historical_weighted_Price_for_theta(l_RHS_current_AskP_list, l_RHS_current_AskQ_list, l_RHS_weight_list , p_dict_sum_for_price)
    l_RHS_history_weighted_avg = float(l_RHS_history_weighted_sum) / (p_len + 1)
    #========================================================================================
    
    c = (1 / float(p_cur_NewQ * \
        dd.g_weight_list[l_index_of_added_qty])) * \
        ((float(l_RHS_current_weighted_sum) / l_LHS_ratio) - l_RHS_history_weighted_avg)
        
    new_theta = max(0, ((p_len + 1) * c - 1) / float(p_len))
    new_theta = min(dd.g_theta_upper , new_theta)
    
    return new_theta

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def calculate_theta_for_new(p_len,p_curr_Price_list,p_prev_Price_list,p_curr_quantity_list,p_prev_quantity_list, p_cur_NewQ ,p_cur_NewP ,  p_dict_sum_for_price):
    '''
    DOC:
    Tick     Q0      P0        Q1     P1        Q2    P2        Q3     P3        Q4     P4
    1        2500    628300    150    628330    50    628335    100    628515    100    628670
    2        2500    628300    150    628330    50    628335    100    628515    100    628615 N    S    100    628615
    '''
    #LHS
    #========================================================================================
    l_LHS_weight_list = []
    l_index_of_added_qty = p_curr_Price_list.index(p_cur_NewP)
    
    l_LHS_current_AskQ_list = [p_prev_quantity_list[0], p_prev_quantity_list[1], 
                               p_prev_quantity_list[2], p_prev_quantity_list[3], 
                               p_prev_quantity_list[4]]
    
    l_LHS_current_AskQ_list[l_index_of_added_qty] += p_cur_NewQ
    
    l_LHS_current_AskP_list = [p_prev_Price_list[0], p_prev_Price_list[1], 
                               p_prev_Price_list[2], p_prev_Price_list[3], 
                               p_prev_Price_list[4]]
    
    l_LHS_weight_list = [dd.g_weight_list[p_prev_Price_list.index(p_prev_Price_list[0])],
                         dd.g_weight_list[p_prev_Price_list.index(p_prev_Price_list[1])],
                         dd.g_weight_list[p_prev_Price_list.index(p_prev_Price_list[2])],
                         dd.g_weight_list[p_prev_Price_list.index(p_prev_Price_list[3])],
                         dd.g_weight_list[p_prev_Price_list.index(p_prev_Price_list[4])]]
    
    
    l_LHS_current_weighted_sum = calculate_current_wt_sum_for_theta_calculation(l_LHS_current_AskQ_list, l_LHS_weight_list)

    l_LHS_history_weighted_sum = calculate_historical_weighted_Price_for_theta(l_LHS_current_AskP_list, l_LHS_current_AskQ_list, l_LHS_weight_list , p_dict_sum_for_price)
    l_LHS_history_weighted_avg = float(l_LHS_history_weighted_sum) / (p_len + 1)
    l_LHS_ratio = float(l_LHS_current_weighted_sum) / l_LHS_history_weighted_avg
    l_LHS_ratio = min(max(l_LHS_ratio, dd.g_lower_cutoff_for_LHS), dd.g_upper_cutoff_for_LHS)
    #========================================================================================
    
    #RHS
    #========================================================================================
    l_RHS_weight_list = []
    l_RHS_current_AskQ_list = [p_prev_quantity_list[0], p_prev_quantity_list[1], 
                               p_prev_quantity_list[2], p_prev_quantity_list[3]]
    
    l_RHS_current_AskP_list = [p_prev_Price_list[0], p_prev_Price_list[1], 
                               p_prev_Price_list[2], p_prev_Price_list[3]]
    
    l_RHS_weight_list = [dd.g_weight_list[p_curr_Price_list.index(p_prev_Price_list[0])],
                         dd.g_weight_list[p_curr_Price_list.index(p_prev_Price_list[1])],
                         dd.g_weight_list[p_curr_Price_list.index(p_prev_Price_list[2])],
                         dd.g_weight_list[p_curr_Price_list.index(p_prev_Price_list[3])]]
    
    l_RHS_current_weighted_sum = calculate_current_wt_sum_for_theta_calculation(l_RHS_current_AskQ_list, l_RHS_weight_list) + \
    (p_cur_NewQ * dd.g_weight_list[l_index_of_added_qty])
    
    l_RHS_history_weighted_sum = calculate_historical_weighted_Price_for_theta(l_RHS_current_AskP_list, l_RHS_current_AskQ_list, l_RHS_weight_list , p_dict_sum_for_price)
    l_RHS_history_weighted_avg = float(l_RHS_history_weighted_sum) / (p_len + 1)
    #========================================================================================
    
    c = (1 / float(p_cur_NewQ * \
        dd.g_weight_list[l_index_of_added_qty])) * \
        ((float(l_RHS_current_weighted_sum) / l_LHS_ratio) - l_RHS_history_weighted_avg)
        
    new_theta = max(0, ((p_len + 1) * c - 1) / float(p_len))
    new_theta = min(dd.g_theta_upper , new_theta)
    
    return new_theta

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def calculate_theta_for_trade(p_len,p_curr_Price_list,p_prev_Price_list,p_curr_quantity_list,p_prev_quantity_list,p_cur_NewP, p_dict_sum_for_price):
    '''
    DOC:
        Q0         P0        Q1        P1        Q2     P2        Q3     P3        Q4     P4
        100      628305    2500        628255    200    628210    200    628205    200    628200    4780000    628350
        2500     628255    200         628210    200    628205    200    628200    200    628195    4780100    628305     T    100    628305    250    629255
    '''
    
    #LHS
    #========================================================================================
    l_LHS_weight_list = []
    l_LHS_current_AskQ_list = [p_curr_quantity_list[0], p_curr_quantity_list[1], 
                               p_curr_quantity_list[2], p_curr_quantity_list[3], 0]
    
    l_LHS_current_AskP_list = [p_curr_Price_list[0], p_curr_Price_list[1], 
                               p_curr_Price_list[2], p_curr_Price_list[3], 
                               p_cur_NewP]
    
    l_LHS_weight_list = [dd.g_weight_list[p_prev_Price_list.index(p_curr_Price_list[0])],
                         dd.g_weight_list[p_prev_Price_list.index(p_curr_Price_list[1])],
                         dd.g_weight_list[p_prev_Price_list.index(p_curr_Price_list[2])],
                         dd.g_weight_list[p_prev_Price_list.index(p_curr_Price_list[3])],
                         dd.g_weight_list[p_prev_Price_list.index(p_cur_NewP)]]
    
    l_LHS_current_weighted_sum = calculate_current_wt_sum_for_theta_calculation(l_LHS_current_AskQ_list, l_LHS_weight_list)
    l_LHS_history_weighted_sum = calculate_historical_weighted_Price_for_theta(l_LHS_current_AskP_list, l_LHS_current_AskQ_list, l_LHS_weight_list , p_dict_sum_for_price)
    l_LHS_history_weighted_avg = float(l_LHS_history_weighted_sum) / (p_len + 1)
    l_LHS_ratio = float(l_LHS_current_weighted_sum) / l_LHS_history_weighted_avg
    l_LHS_ratio = min(max(l_LHS_ratio, dd.g_lower_cutoff_for_LHS), dd.g_upper_cutoff_for_LHS)
    #========================================================================================
    
    #RHS
    #========================================================================================
    l_RHS_weight_list = []
    l_RHS_current_AskQ_list = [p_curr_quantity_list[0], p_curr_quantity_list[1], 
                               p_curr_quantity_list[2], p_curr_quantity_list[3]]
    
    l_RHS_current_AskP_list = [p_curr_Price_list[0], p_curr_Price_list[1], 
                               p_curr_Price_list[2], p_curr_Price_list[3]]
    
    l_RHS_weight_list = [dd.g_weight_list[p_curr_Price_list.index(p_curr_Price_list[0])],
                         dd.g_weight_list[p_curr_Price_list.index(p_curr_Price_list[1])],
                         dd.g_weight_list[p_curr_Price_list.index(p_curr_Price_list[2])],
                         dd.g_weight_list[p_curr_Price_list.index(p_curr_Price_list[3])]]
    
    l_RHS_current_weighted_sum = calculate_current_wt_sum_for_theta_calculation(l_RHS_current_AskQ_list, l_RHS_weight_list) + \
                                (p_curr_quantity_list[4] * dd.g_weight_list[4])
                                
    l_RHS_history_weighted_sum = calculate_historical_weighted_Price_for_theta(l_RHS_current_AskP_list, l_RHS_current_AskQ_list, l_RHS_weight_list,p_dict_sum_for_price)
    l_RHS_history_weighted_avg = float(l_RHS_history_weighted_sum) / (p_len + 1)
    #========================================================================================
    
    c = (1 / float(p_curr_quantity_list[4] * dd.g_weight_list[4])) * ((float(l_RHS_current_weighted_sum) / l_LHS_ratio) - l_RHS_history_weighted_avg)
    trade_theta = ((p_len + 1) * c - 1) / float(p_len)
    trade_theta = min(dd.g_theta_upper , trade_theta)
    
    return trade_theta

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def calculate_theta_for_price_cancel(p_len,p_curr_Price_list,p_prev_Price_list,p_curr_quantity_list,p_prev_quantity_list,p_cur_NewP, p_dict_sum_for_price):
    '''
    DOC:
        Tick        Q0     P0        Q1        P1     Q2        P2     Q3     P3        Q4    P4
        1           50     627740    200    627735    250    627665    850    627660    100    627520
        2           200    627735    250    627665    850    627660    100    627520    50    627510   X    B    50    627740
    '''
    #LHS
    #========================================================================================
    l_LHS_weight_list = []
    l_LHS_current_AskQ_list = [p_curr_quantity_list[0], p_curr_quantity_list[1], 
                               p_curr_quantity_list[2], p_curr_quantity_list[3], 0]
    
    l_LHS_current_AskP_list = [p_curr_Price_list[0], p_curr_Price_list[1], 
                               p_curr_Price_list[2], p_curr_Price_list[3], 
                               p_cur_NewP]
    
    l_LHS_weight_list = [dd.g_weight_list[p_prev_Price_list.index(p_curr_Price_list[0])],
                         dd.g_weight_list[p_prev_Price_list.index(p_curr_Price_list[1])],
                         dd.g_weight_list[p_prev_Price_list.index(p_curr_Price_list[2])],
                         dd.g_weight_list[p_prev_Price_list.index(p_curr_Price_list[3])],
                         dd.g_weight_list[p_prev_Price_list.index(p_cur_NewP)]]
    
    l_LHS_current_weighted_sum = calculate_current_wt_sum_for_theta_calculation(l_LHS_current_AskQ_list, l_LHS_weight_list)
    l_LHS_history_weighted_sum = calculate_historical_weighted_Price_for_theta(l_LHS_current_AskP_list, l_LHS_current_AskQ_list, l_LHS_weight_list , p_dict_sum_for_price)
    l_LHS_history_weighted_avg = float(l_LHS_history_weighted_sum) / (p_len + 1)
    l_LHS_ratio = float(l_LHS_current_weighted_sum) / l_LHS_history_weighted_avg
    l_LHS_ratio = min(max(l_LHS_ratio, dd.g_lower_cutoff_for_LHS), dd.g_upper_cutoff_for_LHS)
    #========================================================================================
    
    #RHS
    #========================================================================================
    l_RHS_weight_list = []
    l_RHS_current_AskQ_list = [p_curr_quantity_list[0], p_curr_quantity_list[1], 
                               p_curr_quantity_list[2], p_curr_quantity_list[3]]
    
    l_RHS_current_AskP_list = [p_curr_Price_list[0], p_curr_Price_list[1], 
                               p_curr_Price_list[2], p_curr_Price_list[3]]
    
    l_RHS_weight_list = [dd.g_weight_list[p_curr_Price_list.index(p_curr_Price_list[0])],
                         dd.g_weight_list[p_curr_Price_list.index(p_curr_Price_list[1])],
                         dd.g_weight_list[p_curr_Price_list.index(p_curr_Price_list[2])],
                         dd.g_weight_list[p_curr_Price_list.index(p_curr_Price_list[3])]]
    
    l_RHS_current_weighted_sum = calculate_current_wt_sum_for_theta_calculation(l_RHS_current_AskQ_list, l_RHS_weight_list) + \
                                (p_curr_quantity_list[4] * dd.g_weight_list[4])
    l_RHS_history_weighted_sum = calculate_historical_weighted_Price_for_theta(l_RHS_current_AskP_list, l_RHS_current_AskQ_list, l_RHS_weight_list , p_dict_sum_for_price)
    l_RHS_history_weighted_avg = float(l_RHS_history_weighted_sum) / (p_len + 1)
    #========================================================================================
    
    c = (1 / float(p_curr_quantity_list[4] * dd.g_weight_list[4])) * ((float(l_RHS_current_weighted_sum) / l_LHS_ratio) - l_RHS_history_weighted_avg)
    cancel_theta = ((p_len + 1) * c - 1) / float(p_len)
    cancel_theta = min(dd.g_theta_upper , cancel_theta)
    
    return cancel_theta
    
def calculate_theta_for_mod_cancel_case1(p_len,p_curr_Price_list,p_prev_Price_list,p_curr_quantity_list,p_prev_quantity_list,p_cur_oldP, p_dict_sum_for_price):
    '''
    DOC : 
        if (l_old_mod_price in p_prev_Price_list and l_old_mod_price not in l_current_AskP_list) and (l_new_mod_price in l_current_AskP_list and l_new_mod_price in p_prev_Price_list):
        Tick      Q0      P0      Q1      P1       Q2      P2       Q3      P3        Q4      P4                NQ     NP        OQ       OP
        1        100    628600    200    628605    300    628610    400    628615    500    628620
        2        100    628600    200    628605    700    628615    500    628620    800    628625    M    B    300    628615    300    628610
    '''
    #LHS
    #========================================================================================
    l_LHS_weight_list = []
    l_LHS_current_AskQ_list = [p_curr_quantity_list[0], p_curr_quantity_list[1], 
                               p_curr_quantity_list[2], p_curr_quantity_list[3], 0]
    
    l_LHS_current_AskP_list = [p_curr_Price_list[0], p_curr_Price_list[1], 
                               p_curr_Price_list[2], p_curr_Price_list[3], 
                               p_cur_oldP]
    
    l_LHS_weight_list = [dd.g_weight_list[p_prev_Price_list.index(p_curr_Price_list[0])],
                         dd.g_weight_list[p_prev_Price_list.index(p_curr_Price_list[1])],
                         dd.g_weight_list[p_prev_Price_list.index(p_curr_Price_list[2])],
                         dd.g_weight_list[p_prev_Price_list.index(p_curr_Price_list[3])],
                         dd.g_weight_list[p_prev_Price_list.index(p_cur_oldP)]]
    
    l_LHS_current_weighted_sum = calculate_current_wt_sum_for_theta_calculation(l_LHS_current_AskQ_list, l_LHS_weight_list)
    l_LHS_history_weighted_sum = calculate_historical_weighted_Price_for_theta(l_LHS_current_AskP_list, l_LHS_current_AskQ_list, l_LHS_weight_list , p_dict_sum_for_price)
    l_LHS_history_weighted_avg = float(l_LHS_history_weighted_sum) / (p_len + 1)
    l_LHS_ratio = float(l_LHS_current_weighted_sum) / l_LHS_history_weighted_avg
    l_LHS_ratio = min(max(l_LHS_ratio, dd.g_lower_cutoff_for_LHS), dd.g_upper_cutoff_for_LHS)
    #========================================================================================
    
    #RHS
    #========================================================================================
    l_RHS_weight_list = []
    l_RHS_current_AskQ_list = [p_curr_quantity_list[0], p_curr_quantity_list[1], 
                               p_curr_quantity_list[2], p_curr_quantity_list[3]]
    
    l_RHS_current_AskP_list = [p_curr_Price_list[0], p_curr_Price_list[1], 
                               p_curr_Price_list[2], p_curr_Price_list[3]]
    
    l_RHS_weight_list = [dd.g_weight_list[p_curr_Price_list.index(p_curr_Price_list[0])],
                         dd.g_weight_list[p_curr_Price_list.index(p_curr_Price_list[1])],
                         dd.g_weight_list[p_curr_Price_list.index(p_curr_Price_list[2])],
                         dd.g_weight_list[p_curr_Price_list.index(p_curr_Price_list[3])]]
    
    l_RHS_current_weighted_sum = calculate_current_wt_sum_for_theta_calculation(l_RHS_current_AskQ_list, l_RHS_weight_list) + \
                                (p_curr_quantity_list[4]* dd.g_weight_list[4])
    l_RHS_history_weighted_sum = calculate_historical_weighted_Price_for_theta(l_RHS_current_AskP_list, l_RHS_current_AskQ_list, l_RHS_weight_list , p_dict_sum_for_price)
    l_RHS_history_weighted_avg = float(l_RHS_history_weighted_sum) / (p_len + 1)
    #========================================================================================
    
    c = (1 / float(p_curr_quantity_list[4]* dd.g_weight_list[4])) * ((float(l_RHS_current_weighted_sum) / l_LHS_ratio) - l_RHS_history_weighted_avg)
    cancel_theta = ((p_len + 1) * c - 1) / float(p_len)
    cancel_theta = min(dd.g_theta_upper , cancel_theta)
    
    return cancel_theta

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def calculate_theta_for_mod_cancel_case2(p_len,p_curr_Price_list,p_prev_Price_list,p_curr_quantity_list,p_prev_quantity_list,p_cur_oldP,p_dict_sum_for_price):
    '''
    DOC:
        if (l_new_mod_price not in p_prev_Price_list and l_new_mod_price not in l_current_AskP_list) and (l_old_mod_price not in l_current_AskP_list and l_old_mod_price in p_prev_Price_list):
        Tick        Q0     P0        Q1        P1     Q2        P2     Q3     P3        Q4    P4
        1           50     627740    200    627735    250    627665    850    627660    100   627520
        2           200    627735    250    627665    850    627660    100    627520    50    627510   M    B    50    627740
    '''
      
    #LHS
    #========================================================================================
    l_LHS_weight_list = []
    l_LHS_current_AskQ_list = [p_curr_quantity_list[0], p_curr_quantity_list[1], 
                               p_curr_quantity_list[2], p_curr_quantity_list[3], 0]
    
    l_LHS_current_AskP_list = [p_curr_Price_list[0], p_curr_Price_list[1], 
                               p_curr_Price_list[2], p_curr_Price_list[3], 
                               p_cur_oldP]
    
    l_LHS_weight_list = [dd.g_weight_list[p_prev_Price_list.index(p_curr_Price_list[0])],
                         dd.g_weight_list[p_prev_Price_list.index(p_curr_Price_list[1])],
                         dd.g_weight_list[p_prev_Price_list.index(p_curr_Price_list[2])],
                         dd.g_weight_list[p_prev_Price_list.index(p_curr_Price_list[3])],
                         dd.g_weight_list[p_prev_Price_list.index(p_cur_oldP)]]
    
    l_LHS_current_weighted_sum = calculate_current_wt_sum_for_theta_calculation(l_LHS_current_AskQ_list, l_LHS_weight_list)
    l_LHS_history_weighted_sum = calculate_historical_weighted_Price_for_theta(l_LHS_current_AskP_list, l_LHS_current_AskQ_list, l_LHS_weight_list , p_dict_sum_for_price)
    l_LHS_history_weighted_avg = float(l_LHS_history_weighted_sum) / (p_len + 1)
    l_LHS_ratio = float(l_LHS_current_weighted_sum) / l_LHS_history_weighted_avg
    l_LHS_ratio = min(max(l_LHS_ratio, dd.g_lower_cutoff_for_LHS), dd.g_upper_cutoff_for_LHS)
    #========================================================================================
    
    #RHS
    #========================================================================================
    l_RHS_weight_list = []
    l_RHS_current_AskQ_list = [p_curr_quantity_list[0], p_curr_quantity_list[1], 
                               p_curr_quantity_list[2], p_curr_quantity_list[3]]
    
    l_RHS_current_AskP_list = [p_curr_Price_list[0], p_curr_Price_list[1], 
                               p_curr_Price_list[2], p_curr_Price_list[3]]
    
    l_RHS_weight_list = [dd.g_weight_list[p_curr_Price_list.index(p_curr_Price_list[0])],
                         dd.g_weight_list[p_curr_Price_list.index(p_curr_Price_list[1])],
                         dd.g_weight_list[p_curr_Price_list.index(p_curr_Price_list[2])],
                         dd.g_weight_list[p_curr_Price_list.index(p_curr_Price_list[3])]]
    
    l_RHS_current_weighted_sum = calculate_current_wt_sum_for_theta_calculation(l_RHS_current_AskQ_list, l_RHS_weight_list) + \
                                (p_curr_quantity_list[4]* dd.g_weight_list[4])
    l_RHS_history_weighted_sum = calculate_historical_weighted_Price_for_theta(l_RHS_current_AskP_list, l_RHS_current_AskQ_list, l_RHS_weight_list,p_dict_sum_for_price)
    l_RHS_history_weighted_avg = float(l_RHS_history_weighted_sum) / (p_len + 1)
    #========================================================================================
    
    c = (1 / float(p_curr_quantity_list[4]* dd.g_weight_list[4])) * ((float(l_RHS_current_weighted_sum) / l_LHS_ratio) - l_RHS_history_weighted_avg)
    cancel_theta = ((p_len + 1) * c - 1) / float(p_len)
    cancel_theta = min(dd.g_theta_upper , cancel_theta)
    
    return cancel_theta

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
