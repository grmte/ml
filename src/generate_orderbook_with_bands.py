#!/usr/bin/python

#============================================================[ Import Modules ]============================================================
import inspect
import calendar,datetime, time, os, sys, commands, gc
from multiprocessing import Process
#===========================================================[ Global Declarations ]========================================================
import argparse

parser = argparse.ArgumentParser(description='This program will run generate order book from raw tbt file \n', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-exp', required=False,help='Instruments_expiry_List')
parser.add_argument('-iT', required=True,help='Instrument_symbol_list')
parser.add_argument('-sP', required=True,help='Instrument_strikeprice_list')
parser.add_argument('-oT', required=True,help='instrument_option_list')
parser.add_argument('-insType',required=False,help="Opt/Cur")
parser.add_argument('-uGE',required=False,help="yes:-Expiry list given No:- expiry list taken automatically")
parser.add_argument('-bGap',required=True,help="Band gap price = ceil(price*TC*2)")
parser.add_argument('-td',required=True,help="Base directory Where output is to be moved")
parser.add_argument('pD',required=False,help="Price depth order book required")
args = parser.parse_args()

if args.uGE == None:
    args.uGE = "yes"
if args.insType == None:
    args.insType = "opt"
    
g_start_execution_time = time.time()
g_mother_directory = "/home/vikas/nselogdata/"
g_ml_base_directory = args.td
g_file_location = ""
g_NSE_filename = ""
g_unique_instrument_identifier_dict = {}
g_list_of_instrument_wise_global_containers = []
g_file_token = ""
if args.pD == None:
    g_price_depth = 5
else:
    g_price_depth = int(args.pD)
g_price_distance = [30, 60, 100]    

#-------------- [ Instrument wise global containers ] --------------
g_fp_output_orderbook_price_list = ""
g_ask_price_quantity_dict = {}
g_bid_price_quantity_dict = {}
g_LTP = 0
g_TTQ = 0
g_serial_no = 0
g_timestamp = ""
g_previous_ob_string = ""
g_instrument_fullname = ""
g_messagecode = ""
g_ordertype = ""
g_quantity_1 = ""
g_quantity_2 = ""
g_price_1 = ""
g_price_2 = ""
g_exchange_timestamp = ""
g_day = ""
g_month = ""
g_year = ""
#------------------------------------------------------------------
#============================================================[ Main Coding ]===============================================================
'''
Q: Why this function is required?
Ans: Is use to flush out the variables used during the whole execution.
'''
def destructor():
    global g_unique_instrument_identifier_dict, g_list_of_instrument_wise_global_containers, g_fp_output_orderbook_price_list
    global g_ask_price_quantity_dict, g_bid_price_quantity_dict, g_timestamp, g_LTP, g_TTQ, g_previous_ob_string
    global g_instrument_fullname, g_serial_no, g_file_token, g_messagecode, g_ordertype, g_quantity_1, g_quantity_2, g_price_1, g_price_2 , g_exchange_timestamp
    
    g_unique_instrument_identifier_dict = {}
    g_list_of_instrument_wise_global_containers = []
    g_fp_output_orderbook_price_list = ""
    g_ask_price_quantity_dict = {}
    g_bid_price_quantity_dict = {}
    g_timestamp = ""
    g_LTP = 0
    g_TTQ = 0
    g_previous_ob_string = ""
    g_instrument_fullname = ""
    g_serial_no = 0
    g_file_token = ""
    g_messagecode = ""
    g_ordertype = ""
    g_quantity_1 = ""
    g_quantity_2 = ""
    g_price_1 = ""
    g_price_2 = ""
    g_exchange_timestamp = ""
    return

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
'''
Q: Why this function is required?
Ans: This function generates a dynamic header for the new Order-Book based upon the Depth-Price value.
'''
def get_header():
    global g_price_depth
    
    l_header = "Instrument;"
    
    l_list_askorbid = ["Ask", "Bid"]
    l_idx_askorbid = 0
    while l_idx_askorbid < len(l_list_askorbid):
        l_idx = 0
        while l_idx < g_price_depth:
            l_header += l_list_askorbid[l_idx_askorbid] + "Q" + str(l_idx) + ";"
            l_header += l_list_askorbid[l_idx_askorbid] + "P" + str(l_idx) + ";"
            l_idx += 1
        l_idx_askorbid += 1
        
    l_header += "TTQ;LTP;LTQ;LTT;ATP;TBQ;TSQ;CP;OP;HP;LP;TimeStamp;SerialNo;MsgCode;OrderType;Quantity1;Price1;Quantity2;Price2;ExchangeTS;BestBidQ;BestBidP;BestAskQ;BestAskP"
    return l_header

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
'''
Q: Why this function is required?
Ans: This function is called to check whether we should print the OB-Log to the file or not, i.e if the previously printed OB-Log 
     is similar to the current one then we will print it to avoid redundant logs. This function only prints the unique logs.   
'''
def generate_final_orderbook_records_and_print_into_file():
    global g_ask_price_quantity_dict, g_bid_price_quantity_dict, g_timestamp, g_LTP, g_TTQ, g_serial_no, g_price_depth
    global g_previous_ob_string, g_fp_output_orderbook_price_list, g_instrument_fullname, g_messagecode, g_ordertype, g_quantity_1, g_quantity_2, g_price_1, g_price_2 , g_exchange_timestamp
    
    l_ob_string_to_be_printed = ""
    l_current_ob_string = ""
    l_flag_indicating_to_be_printed_or_not = 1
    try:
        l_idx = g_price_depth
        l_all_key_values_list_for_ask = sorted(g_ask_price_quantity_dict.items())
        for l_key, l_value in l_all_key_values_list_for_ask:
            l_current_ob_string += (str(l_value[0]) + ";" + str(l_key) + ";") 
            l_idx -= 1
            if l_idx == 0: break
        for index in range(0,l_idx):
            l_current_ob_string += ";;"
            l_flag_indicating_to_be_printed_or_not = 0
        l_idx = 0
        l_all_key_values_list_for_bid = sorted(g_bid_price_quantity_dict.items(), reverse = True)
        
        for l_key, l_value in l_all_key_values_list_for_bid:
            l_current_ob_string += (str(l_value[0]) + ";" + str(l_key) + ";")
            l_idx += 1
            if l_idx == g_price_depth: break
        for index in range(l_idx,g_price_depth):
            l_current_ob_string += ";;"
            l_flag_indicating_to_be_printed_or_not = 0
        l_current_ob_string += str(g_TTQ) + ";" + str(g_LTP)  
       
        l_bestBidP = "" 
        l_bestBidQ = ""
        l_bestAskP = ""
        l_bestAskQ = ""
        if(l_all_key_values_list_for_bid != []):
            import pdb
            #pdb.set_trace()
            l_best_bid_bandlist = l_all_key_values_list_for_bid[0][1][1]
            l_all_prices_in_bid_band = sorted(l_best_bid_bandlist.items(), reverse = True)
            l_bestBidP= str(l_all_prices_in_bid_band[0][0])
            l_bestBidQ= str(l_all_prices_in_bid_band[0][1])
        if(l_all_key_values_list_for_ask != []):
            import pdb
            #pdb.set_trace()
            l_best_ask_bandlist = l_all_key_values_list_for_ask[0][1][1]
            l_all_prices_in_ask_band = sorted(l_best_ask_bandlist.items())
            l_bestAskP = str(l_all_prices_in_ask_band[0][0])
            l_bestAskQ = str(l_all_prices_in_ask_band[0][1])

        if g_previous_ob_string <> l_current_ob_string:
            if l_flag_indicating_to_be_printed_or_not == 1 :
                l_ob_string_to_be_printed = g_instrument_fullname + ";" + l_current_ob_string + ";0;0;0;0;0;0;0;0;0;" + g_timestamp + ";" + str(g_serial_no) + ";" + g_messagecode + ";" + g_ordertype + ";" + \
                                            g_quantity_1 + ";" + g_price_1 + ";" + g_quantity_2 + ";" + g_price_2 + ";" + g_exchange_timestamp + ";" + str(l_bestBidQ) + ";" + str(l_bestBidP) + ";" + str(l_bestAskQ)+ ";" + str(l_bestAskP)      
                g_fp_output_orderbook_price_list.write(l_ob_string_to_be_printed + "\n")
                g_previous_ob_string = l_current_ob_string
                     
    except Exception, e:
        print "Exception @Print: ", e
    return

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++    
def get_max_frequency_occuring_expiry():
    global g_NSE_filename,g_file_location
    temp_str = "head -100000 " + g_file_location + g_NSE_filename + " | awk 'BEGIN {FS=\",\"};{print $7}' | sort | uniq -c | sort -n | tail -1"
    import pdb
    #pdb.set_trace()
    return (commands.getoutput(temp_str)).split()[1]
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++    

def get_band_given_price_and_side(p_price, p_band_gap, p_order_side):
    l_value = 0.0
    if p_order_side == "B":
        l_value = float(int(p_price/p_band_gap)*p_band_gap)
    else:
        if(p_price % p_band_gap == 0):
            l_value = p_price
        else:
            l_value = float((int(p_price/p_band_gap)+1)*p_band_gap)
    return str(l_value)
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
'''
Q: Why this function is required?
Ans: This is the main logic behind the TBT-OB is coded here. Based upon the message codes (N,M,X,T) the logic to generate
     the Order-Book logs are generated for each TBT log.  
'''
def prepare_orderbook_pricelist(p_nse_temp_list):
    global g_ask_price_quantity_dict, g_bid_price_quantity_dict, g_TTQ, g_LTP, g_timestamp, g_serial_no, g_messagecode, g_ordertype, g_quantity_1, g_quantity_2
    global g_list_of_instrument_wise_global_containers, g_fp_output_orderbook_price_list, g_previous_ob_string, g_instrument_fullname, g_price_1, g_price_2 , g_exchange_timestamp
    
    generate_final_orderbook_records_and_print_into_file()    #<----------- Print OB File
    g_serial_no = p_nse_temp_list[-3]
    g_messagecode = p_nse_temp_list[0]
    g_timestamp = p_nse_temp_list[1]
    g_exchange_timestamp = p_nse_temp_list[-2]
    l_band_price_gap = p_nse_temp_list[-1]
    l_flag =  0
    if p_nse_temp_list[0] == "M":
        g_price_1 = p_nse_temp_list[3]
        g_quantity_1 = p_nse_temp_list[4]
        g_price_2 = p_nse_temp_list[5]
        g_quantity_2 = p_nse_temp_list[6]
    elif p_nse_temp_list[0] == "N" or p_nse_temp_list[0] == "X":
        g_price_1 = p_nse_temp_list[3]
        g_quantity_1 = p_nse_temp_list[4]
        g_price_2 = ""
        g_quantity_2 = ""
    else:
        g_price_1 = p_nse_temp_list[2]
        g_quantity_1 = p_nse_temp_list[3]
        g_price_2 = ""
        g_quantity_2 = ""
        
    if p_nse_temp_list[0] <> "T":
        g_ordertype = p_nse_temp_list[2]
    else:
        g_ordertype = ""
    import pdb
    if p_nse_temp_list[0] <> "T":
        l_band_price1 = get_band_given_price_and_side(float(g_price_1),l_band_price_gap,p_nse_temp_list[2])
        if(g_price_2 != ""):
            l_band_price2 = get_band_given_price_and_side(float(g_price_2),l_band_price_gap,p_nse_temp_list[2])
    #________________________________________ [ NORMAL (N) ] ________________________________________
    if p_nse_temp_list[0] == "N":
        try:
            if p_nse_temp_list[2] == "B":
                if float(l_band_price1) in g_bid_price_quantity_dict: 
                    (g_bid_price_quantity_dict[float(l_band_price1)])[0] = ((g_bid_price_quantity_dict.get(float(l_band_price1)))[0] + int(p_nse_temp_list[4]))
                    if(float(p_nse_temp_list[3]) in g_bid_price_quantity_dict[float(l_band_price1)][1]):
                        (g_bid_price_quantity_dict[float(l_band_price1)])[1][float(p_nse_temp_list[3])] = ((g_bid_price_quantity_dict.get(float(l_band_price1)))[1][float(p_nse_temp_list[3])] + int(p_nse_temp_list[4]))
                    else:
                        (g_bid_price_quantity_dict[float(l_band_price1)])[1][float(p_nse_temp_list[3])] = int(p_nse_temp_list[4])
                else:
                    (g_bid_price_quantity_dict[float(l_band_price1)]) = [int(p_nse_temp_list[4]), {}]
                    (g_bid_price_quantity_dict[float(l_band_price1)])[1][float(p_nse_temp_list[3])] = int(p_nse_temp_list[4])
            else:
                if float(l_band_price1) in g_ask_price_quantity_dict: 
                    (g_ask_price_quantity_dict[float(l_band_price1)])[0] = (g_ask_price_quantity_dict.get(float(l_band_price1))[0] + int(p_nse_temp_list[4]))
                    if(float(p_nse_temp_list[3]) in g_ask_price_quantity_dict[float(l_band_price1)][1] ):
                        (g_ask_price_quantity_dict[float(l_band_price1)])[1][float(p_nse_temp_list[3])] = (g_ask_price_quantity_dict.get(float(l_band_price1))[1][float(p_nse_temp_list[3])] + int(p_nse_temp_list[4]))
                    else:
                        (g_ask_price_quantity_dict[float(l_band_price1)])[1][float(p_nse_temp_list[3])] = (int(p_nse_temp_list[4]))
                else:
                    g_ask_price_quantity_dict[float(l_band_price1)] = [int(p_nse_temp_list[4]) , {}]
                    (g_ask_price_quantity_dict[float(l_band_price1)])[1][float(p_nse_temp_list[3])] = (int(p_nse_temp_list[4]))
        except:
            pdb.set_trace()
            print "Exception in New"
    #________________________________________ [ CANCEL (X) ] ________________________________________
    elif p_nse_temp_list[0] == "X":
        try:
            if p_nse_temp_list[2] == "B":
                if float(l_band_price1) in g_bid_price_quantity_dict: 
                    g_bid_price_quantity_dict[float(l_band_price1)][0] = (g_bid_price_quantity_dict.get(float(l_band_price1))[0] - int(p_nse_temp_list[4]))
                    if(float(p_nse_temp_list[3]) in g_bid_price_quantity_dict[float(l_band_price1)][1] ):
                        g_bid_price_quantity_dict[float(l_band_price1)][1][float(p_nse_temp_list[3])] = (g_bid_price_quantity_dict.get(float(l_band_price1))[1][float(p_nse_temp_list[3])] - int(p_nse_temp_list[4]))
                        if g_bid_price_quantity_dict[float(l_band_price1)][1][float(p_nse_temp_list[3])] <= 0:
                            del g_bid_price_quantity_dict[float(l_band_price1)][1][float(p_nse_temp_list[3])]
                    else:
                        pdb.set_trace()
                        print "\nException Cancel:"
                    if g_bid_price_quantity_dict[float(l_band_price1)][0] <= 0:
                        del g_bid_price_quantity_dict[float(l_band_price1)]
                else:
                    pdb.set_trace()
                    print "\nException Cancel: Price not found ...!!", float(l_band_price1), int(p_nse_temp_list[4]), p_nse_temp_list[0], p_nse_temp_list[2]
            else:
                if float(l_band_price1) in g_ask_price_quantity_dict: 
                    g_ask_price_quantity_dict[float(l_band_price1)][0] = (g_ask_price_quantity_dict.get(float(l_band_price1))[0] - int(p_nse_temp_list[4]))
                    if(float(p_nse_temp_list[3]) in g_ask_price_quantity_dict[float(l_band_price1)][1]):
                        g_ask_price_quantity_dict[float(l_band_price1)][1][float(p_nse_temp_list[3])] = (g_ask_price_quantity_dict.get(float(l_band_price1))[1][float(p_nse_temp_list[3])] - int(p_nse_temp_list[4]))
                        if g_ask_price_quantity_dict[float(l_band_price1)][1][float(p_nse_temp_list[3])] <= 0:
                            del g_ask_price_quantity_dict[float(l_band_price1)][1][float(p_nse_temp_list[3])]
                    else:
                        pdb.set_trace()
                        print "\nException Cancel:"
                    if g_ask_price_quantity_dict[float(l_band_price1)][0] <= 0:
                        del g_ask_price_quantity_dict[float(l_band_price1)]
                else:
                    pdb.set_trace()
                    print "\nException Cancel: Price not found ...!!", float(l_band_price1), int(p_nse_temp_list[4]), p_nse_temp_list[0], p_nse_temp_list[2]
        except:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]     
            print "Error type: %s, File name: %s, Line no: %s" %(str(exc_type), str(fname), str(exc_tb.tb_lineno))
            pdb.set_trace()
    
    #________________________________________ [ MODIFY (M) ] ________________________________________
    elif p_nse_temp_list[0] == "M":
        if p_nse_temp_list[2] == "B":
            if float(l_band_price1) in g_bid_price_quantity_dict: 
                g_bid_price_quantity_dict[float(l_band_price1)][0] = (g_bid_price_quantity_dict.get(float(l_band_price1))[0] + int(p_nse_temp_list[4]))
                if(float(p_nse_temp_list[3]) in g_bid_price_quantity_dict[float(l_band_price1)][1]):
                    g_bid_price_quantity_dict[float(l_band_price1)][1][float(p_nse_temp_list[3])] = (g_bid_price_quantity_dict.get(float(l_band_price1))[1][float(p_nse_temp_list[3])] + int(p_nse_temp_list[4]))
                else:
                    g_bid_price_quantity_dict[float(l_band_price1)][1][float(p_nse_temp_list[3])] = int(p_nse_temp_list[4])
            else:
                g_bid_price_quantity_dict[float(l_band_price1)] = [int(p_nse_temp_list[4]), {}]
                g_bid_price_quantity_dict[float(l_band_price1)][1][float(p_nse_temp_list[3])] = int(p_nse_temp_list[4])
            if float(l_band_price2) in g_bid_price_quantity_dict: 
                g_bid_price_quantity_dict[float(l_band_price2)][0] = (g_bid_price_quantity_dict.get(float(l_band_price2))[0] - int(p_nse_temp_list[6]))
                if(float(p_nse_temp_list[5]) in g_bid_price_quantity_dict[float(l_band_price2)][1] ):
                    g_bid_price_quantity_dict[float(l_band_price2)][1][float(p_nse_temp_list[5])] = (g_bid_price_quantity_dict.get(float(l_band_price2))[1][float(p_nse_temp_list[5])] - int(p_nse_temp_list[6]))
                    if g_bid_price_quantity_dict[float(l_band_price2)][1][float(p_nse_temp_list[5])] <= 0:
                        del g_bid_price_quantity_dict[float(l_band_price2)][1][float(p_nse_temp_list[5])]
                if g_bid_price_quantity_dict[float(l_band_price2)][0] <= 0:
                    del g_bid_price_quantity_dict[float(l_band_price2)]
            else:
                print "\nException Modify: Price not found ...!!", float(l_band_price2), int(p_nse_temp_list[6]), p_nse_temp_list[0], p_nse_temp_list[2]
        else:
            if float(l_band_price1) in g_ask_price_quantity_dict: 
                g_ask_price_quantity_dict[float(l_band_price1)][0] = (g_ask_price_quantity_dict.get(float(l_band_price1))[0] + int(p_nse_temp_list[4]))
                if(float(p_nse_temp_list[3]) in g_ask_price_quantity_dict[float(l_band_price1)][1]):
                    g_ask_price_quantity_dict[float(l_band_price1)][1][float(p_nse_temp_list[3])] = (g_ask_price_quantity_dict.get(float(l_band_price1))[1][float(p_nse_temp_list[3])] + int(p_nse_temp_list[4]))
                else:
                    g_ask_price_quantity_dict[float(l_band_price1)][1][float(p_nse_temp_list[3])]  = int(p_nse_temp_list[4])
            else:
                g_ask_price_quantity_dict[float(l_band_price1)] = [int(p_nse_temp_list[4]), {}]
                g_ask_price_quantity_dict[float(l_band_price1)][1][float(p_nse_temp_list[3])]  = int(p_nse_temp_list[4])
                    
            if float(l_band_price2) in g_ask_price_quantity_dict: 
                g_ask_price_quantity_dict[float(l_band_price2)][0] = (g_ask_price_quantity_dict.get(float(l_band_price2))[0] - int(p_nse_temp_list[6]))
                if(float(p_nse_temp_list[5]) in g_ask_price_quantity_dict[float(l_band_price2)][1]):
                    g_ask_price_quantity_dict[float(l_band_price2)][1][float(p_nse_temp_list[5])] = (g_ask_price_quantity_dict.get(float(l_band_price2))[1][float(p_nse_temp_list[5])] - int(p_nse_temp_list[6]))
                    if g_ask_price_quantity_dict[float(l_band_price2)][1][float(p_nse_temp_list[5])] <= 0:
                        del g_ask_price_quantity_dict[float(l_band_price2)][1][float(p_nse_temp_list[5])]
                if g_ask_price_quantity_dict[float(l_band_price2)][0] <= 0:
                    del g_ask_price_quantity_dict[float(l_band_price2)]
            else:
                print "\nException Modify: Price not found ...!!", float(l_band_price2), int(p_nse_temp_list[6]), p_nse_temp_list[0], p_nse_temp_list[2] 
                    
    #________________________________________ [ TRADE (T) ] ________________________________________
    elif p_nse_temp_list[0] == "T":
        l_band_price1_bid_side = get_band_given_price_and_side(float(g_price_1),l_band_price_gap,"B")
        l_band_price1_ask_side = get_band_given_price_and_side(float(g_price_1),l_band_price_gap,"S")
        if float(l_band_price1_bid_side) in g_bid_price_quantity_dict: 
            if( float(p_nse_temp_list[2]) in g_bid_price_quantity_dict[float(l_band_price1_bid_side)][1]):
                l_flag = 1
                g_bid_price_quantity_dict[float(l_band_price1_bid_side)][0] = (g_bid_price_quantity_dict.get(float(l_band_price1_bid_side))[0] - int(p_nse_temp_list[3]))
                g_bid_price_quantity_dict[float(l_band_price1_bid_side)][1][float(p_nse_temp_list[2])] = (g_bid_price_quantity_dict.get(float(l_band_price1_bid_side))[1][float(p_nse_temp_list[2])] - int(p_nse_temp_list[3]))
                if g_bid_price_quantity_dict[float(l_band_price1_bid_side)][1][float(p_nse_temp_list[2])]  <= 0:
                    del g_bid_price_quantity_dict[float(l_band_price1_bid_side)][1][float(p_nse_temp_list[2])]
                if g_bid_price_quantity_dict[float(l_band_price1_bid_side)][0] <= 0:
                    del g_bid_price_quantity_dict[float(l_band_price1_bid_side)]
        
        if l_flag == 0 and float(l_band_price1_ask_side) in g_ask_price_quantity_dict: 
            if( float(p_nse_temp_list[2]) in g_ask_price_quantity_dict[float(l_band_price1_ask_side)][1]):
                l_flag = 1
                g_ask_price_quantity_dict[float(l_band_price1_ask_side)][0]= (g_ask_price_quantity_dict.get(float(l_band_price1_ask_side))[0] - int(p_nse_temp_list[3]))
                g_ask_price_quantity_dict[float(l_band_price1_ask_side)][1][float(p_nse_temp_list[2])]= (g_ask_price_quantity_dict.get(float(l_band_price1_ask_side))[1][float(p_nse_temp_list[2])] - int(p_nse_temp_list[3]))
                if g_ask_price_quantity_dict[float(l_band_price1_ask_side)][1][float(p_nse_temp_list[2])] <= 0:
                    del g_ask_price_quantity_dict[float(l_band_price1_ask_side)][1][float(p_nse_temp_list[2])] 
                if g_ask_price_quantity_dict[float(l_band_price1_ask_side)][0] <= 0:
                    del g_ask_price_quantity_dict[float(l_band_price1_ask_side)]
        
        if l_flag == 0:
            print "\nException Trade: Price not found ...!!", float(p_nse_temp_list[2]), int(p_nse_temp_list[3]), p_nse_temp_list[0], p_nse_temp_list[2]
            import pdb
            pdb.set_trace()
        g_LTP = float(p_nse_temp_list[2])
        g_TTQ = (g_TTQ + int(p_nse_temp_list[3]))
    else:
        print "\nError in Message Type ...!!"
    
    g_list_of_instrument_wise_global_containers[0] = g_fp_output_orderbook_price_list 
    g_list_of_instrument_wise_global_containers[1] = g_ask_price_quantity_dict 
    g_list_of_instrument_wise_global_containers[2] = g_bid_price_quantity_dict
    g_list_of_instrument_wise_global_containers[3] = g_timestamp
    g_list_of_instrument_wise_global_containers[4] = g_LTP
    g_list_of_instrument_wise_global_containers[5] = g_TTQ
    g_list_of_instrument_wise_global_containers[6] = g_previous_ob_string
    g_list_of_instrument_wise_global_containers[7] = g_instrument_fullname
    g_list_of_instrument_wise_global_containers[8] = g_serial_no
    g_list_of_instrument_wise_global_containers[9] = g_messagecode
    g_list_of_instrument_wise_global_containers[10] = g_ordertype
    g_list_of_instrument_wise_global_containers[11] = g_quantity_1
    g_list_of_instrument_wise_global_containers[12] = g_price_1
    g_list_of_instrument_wise_global_containers[13] = g_quantity_2
    g_list_of_instrument_wise_global_containers[14] = g_price_2
    g_list_of_instrument_wise_global_containers[15] = g_exchange_timestamp
    return

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
'''
 Sample Raw TBT Logs:- 
 -----------------------------------------------------------------------------------------------------------------------------------
     [0]      [1]    [2]     [3]       [4]       [5]        [6]        [7]         [8]       [9]      [10]    [11]    [12]    [13]    
 ReceivedTS,MsgCode,SqNo,ExchangeTS,InstType,InstSymbol,ExpiryDate,StrikePrice,OptionType,OrderType,NewPrice,NewQty,OldPrice,OldQty
 -----------------------------------------------------------------------------------------------------------------------------------
 1386825451s10531us,N,3179,1071306900083,3,NIFTY     ,1072535400,610000,4,B,100,100
 1386825451s10556us,N,3180,1071306900084,1,NIFTY     ,1072535400,-1,0,B,628300,100
 1386825451s10581us,N,3181,1071306900086,4,NHPC      ,1072535400,2000,3,S,20,10000
 1386825451s10606us,N,3182,1071306900083,3,NIFTY     ,1072535400,630000,4,S,9800,100
 1386825451s10631us,N,3183,1071306900084,1,NIFTY     ,1072535400,-1,0,B,628000,50 
 -----------------------------------------------------------------------------------------------------------------------------------
 
Q: Why this function is required?
Ans: This is the main function which reads the Raw-TBT data by a chunk each time and passes each of the logs from that chunk for further
     processing to generate Order Book log. Also maintains a dictionary to hold the whole Order-Book logs. 
'''
def read_the_filtered_file_and_generate_object(p_file_name):
    global g_file_location, g_NSE_filename, g_unique_instrument_identifier_dict, g_list_of_instrument_wise_global_containers
    global g_fp_output_orderbook_price_list, g_ask_price_quantity_dict, g_bid_price_quantity_dict, g_timestamp, g_LTP, g_TTQ
    global g_previous_ob_string, g_instrument_fullname, g_serial_no, g_messagecode, g_ordertype, g_quantity_1, g_quantity_2, g_price_1, g_price_2 , g_exchange_timestamp
    l_counter = 0
    
    print "\nReading the NSE Raw TBT file and generate Order-Book ...\n"
    
    from itertools import islice
    
    with open(g_file_location + p_file_name, "r") as l_fp_nse_file:
        
        while True:
            l_next_n_lines = list(islice(l_fp_nse_file, 100000))
            
            if not l_next_n_lines: break
            
            l_counter += 100000
            print "Processing %s lines."%l_counter
            
            for l_line in l_next_n_lines:
                l_line_list = l_line.split(",")
                try:
                    l_instrument_key = l_line_list[5] + "," + l_line_list[6] + "," + l_line_list[7] + "," + l_line_list[8] 
                except:
                    continue
                if l_instrument_key in g_unique_instrument_identifier_dict:
                    try:
                        g_list_of_instrument_wise_global_containers = g_unique_instrument_identifier_dict[l_instrument_key]
                        
                        #[ Initialize the global containers ]===============================================
                        g_fp_output_orderbook_price_list = g_list_of_instrument_wise_global_containers[0]
                        g_ask_price_quantity_dict = g_list_of_instrument_wise_global_containers[1]
                        g_bid_price_quantity_dict = g_list_of_instrument_wise_global_containers[2]
                        g_timestamp = g_list_of_instrument_wise_global_containers[3]
                        g_LTP = g_list_of_instrument_wise_global_containers[4]
                        g_TTQ = g_list_of_instrument_wise_global_containers[5]
                        g_previous_ob_string = g_list_of_instrument_wise_global_containers[6]
                        g_instrument_fullname = g_list_of_instrument_wise_global_containers[7]
                        g_serial_no = g_list_of_instrument_wise_global_containers[8]
                        
                        g_messagecode = g_list_of_instrument_wise_global_containers[9]
                        g_ordertype = g_list_of_instrument_wise_global_containers[10]
                        g_quantity_1 = g_list_of_instrument_wise_global_containers[11]
                        g_price_1 = g_list_of_instrument_wise_global_containers[12]
                        g_quantity_2 = g_list_of_instrument_wise_global_containers[13]
                        g_price_2 = g_list_of_instrument_wise_global_containers[14]
                        g_exchange_timestamp = g_list_of_instrument_wise_global_containers[15]
                        g_band_price_gap = g_list_of_instrument_wise_global_containers[16]
                        #===================================================================================
                        l_nse_temp_list = [l_line_list[1], l_line_list[0] , l_line_list[9], l_line_list[10], l_line_list[11].strip()]
                        
                        try: l_nse_temp_list.append(l_line_list[12])
                        except: pass
                        
                        try: l_nse_temp_list.append(l_line_list[13].strip())
                        except: pass
                        l_nse_temp_list.append(l_line_list[2])
                        l_nse_temp_list.append( "%.6f" %(int(l_line_list[3])/1000.000))
                        l_nse_temp_list.append(g_band_price_gap)
                        
                        prepare_orderbook_pricelist(l_nse_temp_list)
                        
                        g_unique_instrument_identifier_dict[l_instrument_key] = g_list_of_instrument_wise_global_containers
                        
                    except Exception, e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]    
                        print "Error type: %s, File name: %s, Line no: %s" %(str(exc_type), str(fname), str(exc_tb.tb_lineno))
                        print "EXCEPTION in :- ",e, l_line
            
            gc.collect()
            
    l_fp_nse_file.close()
    del l_fp_nse_file
    return

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
'''
Q: Why this function is required?
Ans: It generates the folder name in yyyy-mm-dd format according to the date being used in the program. Also prepares
     the name of the Raw-TBT data as NSE_M1-D12-Y14.txt, as the initial name of the raw file is not used.
'''
def get_current_date_folder(p_date):
    global g_file_token,g_ml_base_directory, g_NSE_filename , g_day , g_month , g_year
    l_current_month = 0 
    l_current_day = 0
    l_current_year= 0
        
    l_current_day = int(p_date[6-8])
    l_current_month = int(p_date[4-6])
    l_current_year = int(p_date[0-4])

    g_file_token = "M" + str(l_current_month) + "-" + "D" + str(l_current_day)
    
    if l_current_day < 10: l_day = "0" + str(l_current_day)
    else: l_day = str(l_current_day)
    
    if l_current_month < 10: l_month = "0" + str(l_current_month)
    else: l_month = str(l_current_month)
    
    last_modified_folder = str(l_current_year) + "-" + l_month + "-" + l_day
    if not os.path.exists(g_ml_base_directory):
        os.mkdir(g_ml_base_directory)
    g_day = l_day
    g_month = l_month
    g_year = l_current_year  
    if args.insType.lower() == "opt":
        g_NSE_filename = "NSE_" + g_file_token + "-Y" + str(l_current_year)[-2:] + ".txt"
    elif args.insType.lower() == "cur":
        g_NSE_filename = "NSE_" + g_file_token + "-Y" + str(l_current_year)[-2:] + "_Curr.txt"
    print "FILE READ IS " , g_NSE_filename
        
    return last_modified_folder

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
'''
Q: Why this function is required?
Ans: To calculates and returns the elapsed time of execution from the starting time. 
'''
def elapsed():
    global g_start_execution_time
    return (time.time() - g_start_execution_time)

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
'''
Q: Why this function is required?
Ans: It returns the expiry date in DDMMYY format (eg.: 30JanY14) from the epoch time wrt 1970 given in the TBT data.
'''
def return_expiry_string(p_expiry):
    import calendar, datetime
    l_expiry_wrt_1970 = float(p_expiry) + 315513000.0
    
    l_dt = datetime.datetime.fromtimestamp(l_expiry_wrt_1970)
    l_current_expiry_string = str(l_dt.day) + calendar.month_name[l_dt.month][:3] + "Y" + str(l_dt.year)[2:]
    return str(l_current_expiry_string)

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def get_expiry_date(p_year,p_month):
    l_list_of_days_in_that_month = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if (p_year % 100 != 0 and p_year % 4 == 0) or (p_year % 400 == 0):
        l_list_of_days_in_that_month[2] = 29
    l_last_thrs_date = datetime.datetime(int(p_year),int(p_month),l_list_of_days_in_that_month[int(p_month)],9, 0, 0, 0)
    while l_last_thrs_date.weekday() != 3:
        l_last_thrs_date = l_last_thrs_date + datetime.timedelta(days=-1)
    l_current_expiry_string = str(l_last_thrs_date.day) + calendar.month_name[l_last_thrs_date.month][:3] + "Y" + str(l_last_thrs_date.year)[2:]
    print "Expiry date = " ,l_current_expiry_string
    return l_current_expiry_string,l_last_thrs_date
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def get_epoch_time_of_last_thursday_of_given_date():
    global g_year,g_month,g_day
    import time,datetime,calendar
    l_execution_date = datetime.datetime(int(g_year),int(g_month),int(g_day),9, 0, 0, 0)
    l_current_expiry_string,l_last_thrs_date = get_expiry_date(g_year,g_month)
    if l_execution_date > l_last_thrs_date:
        if int(g_month) == 12 :
            l_current_expiry_string,l_last_thrs_date = get_expiry_date(int(g_year)+1,1)
        else:
            l_current_expiry_string,l_last_thrs_date = get_expiry_date(g_year,int(g_month) + 1)
    l_epoch_secs = calendar.timegm(l_last_thrs_date.utctimetuple())
    l_epoch_secs = l_epoch_secs - 315513000.0
    return str(int(l_epoch_secs))
    
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++    
'''
Q: Why this function is required?
Ans: This is the main program which initialize all the local variables with the global variables' value set earlier in
     Then initiates/invokes the function which reads the Raw-TBT file and does the other processing. 
'''
def main():
    global g_unique_instrument_identifier_dict, g_file_location, g_file_token, g_ml_base_directory ,g_price_distance, g_NSE_filename, g_mother_directory
    print "\nExecution started ..."
    
    if os.path.exists(g_file_location + g_NSE_filename) == False:
        print "\nThe file %s is not present.\n\nExecution is terminated ...\n"%(g_file_location + g_NSE_filename)
        return
    else:
        print "\nThe Raw TBT Data file %s has been identified at %s"%(g_NSE_filename, g_file_location)
        
    l_str_p_dep = ""
    for l_pd in g_price_distance:
        l_str_p_dep += str(l_pd) + "-"
    
    l_total_no_of_lines = commands.getoutput('tail -3 ' + g_file_location + g_NSE_filename).split("\n")[0].split(",")[2]
    
    print "\nNo. of lines to be processed: ", l_total_no_of_lines 
    print "\nInstruments to be filtered are ..."
    
    l_input_file_name = ''
        
    l_symbol = args.iT
    if args.uGE == "no":
        l_expiry = get_max_frequency_occuring_expiry()#get_epoch_time_of_last_thursday_of_given_date()
    else:
        l_expiry = args.exp
    print l_expiry
    l_strikeprice = args.sP
    l_option = args.oT
    l_instrument_ticker = l_symbol.strip() + "-" + l_strikeprice + "-" + l_option
    print l_instrument_ticker
    l_expirydate = return_expiry_string(l_expiry)
    l_ouptut_file_name =  g_file_token + "-Expiry-" + l_expirydate + "-" + l_instrument_ticker + "-bandPrice-depth-" + str(g_price_depth) + ".txt"
    if os.path.exists(g_file_location +l_ouptut_file_name):
        print "File Exist , delete and rerun it ", g_file_location + g_file_token + "-Expiry-" + l_expirydate + "-" + l_instrument_ticker + "-bandPrice-depth-" + str(g_price_depth) + ".txt" 
        os.exit(1)
    l_fp_output_orderbook_price_list = open(g_file_location + l_ouptut_file_name, 'w')
    l_fp_output_orderbook_price_list.write(get_header() + "\n")
    
    l_input_file_name =  g_file_token + "-Expiry-" + l_expirydate + "-" + l_instrument_ticker + "-bandPrice-depth-" + str(g_price_depth) + "temp.txt"
    l_symbol = "%10s" %l_symbol
    print 'grep  \'' + l_symbol + ',' + l_expiry + ',' + l_strikeprice + ',' + l_option + '\' ' + g_file_location + g_NSE_filename + ' > ' + g_file_location + l_input_file_name
    os.system('grep  \'' + l_symbol + ',' + l_expiry + ',' + l_strikeprice + ',' + l_option + '\' ' + g_file_location + g_NSE_filename + ' > ' + g_file_location + l_input_file_name)

    l_ask_price_quantity_dict = {}
    l_bid_price_quantity_dict = {}
    l_timestamp = ""
    l_LTP = 0
    l_TTQ = 0
    l_previous_ob_string = "" 
    l_instrument_fullname = l_instrument_ticker + "-" + l_expirydate
    l_serial_no = 0
    l_messagecode = ""
    l_ordertype = ""
    l_quantity_1 = ""
    l_quantity_2 = ""
    l_price_1 = ""
    l_price_2 = ""
    l_exchange_time_stamp = ""
    l_band_gap_price = int(args.bGap)
    print l_instrument_fullname , l_band_gap_price
    
    l_list_of_instrument_wise_global_containers = [l_fp_output_orderbook_price_list, l_ask_price_quantity_dict, l_bid_price_quantity_dict, l_timestamp,\
                                                   l_LTP, l_TTQ, l_previous_ob_string, l_instrument_fullname, l_serial_no, l_messagecode, l_ordertype,\
                                                   l_quantity_1, l_price_1, l_quantity_2, l_price_2 , l_exchange_time_stamp , l_band_gap_price]
    
    g_unique_instrument_identifier_dict[l_symbol + "," + l_expiry + "," + l_strikeprice + "," + l_option] = l_list_of_instrument_wise_global_containers
    print l_input_file_name
    read_the_filtered_file_and_generate_object(l_input_file_name)        # <----- Read the File and generate a Python Object
    print "\nTime elapsed to create the OB file: ", elapsed()
    
    for l_key in g_unique_instrument_identifier_dict:
        l_value_list = g_unique_instrument_identifier_dict[l_key]
        l_value_list[0].flush()
        l_value_list[0].close()
    
    os.system('rm -rf ' + g_file_location + l_input_file_name)
    os.system('mv '+ g_file_location + l_ouptut_file_name + ' ' + g_ml_base_directory)
    ml_working_file_directory = g_ml_base_directory.replace("/ro/",'/wf/')
    if not os.path.exists(ml_working_file_directory):
        os.mkdir(ml_working_file_directory)
        os.mkdir(ml_working_file_directory+"/f/")
        os.mkdir(ml_working_file_directory+"/t/")
        os.mkdir(ml_working_file_directory+"/p/")
    ml_results_file_directory = g_ml_base_directory.replace("/ro/",'/rs/')
    if not os.path.exists(ml_results_file_directory):
        os.mkdir(ml_results_file_directory)
        os.mkdir(ml_results_file_directory+"/r/")
        os.mkdir(ml_results_file_directory+"/t/")

    print "\nExecution is completed ..."
    destructor()
    gc.collect()
    return

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
'''
Q: Why this function is required?
Ans: This is the start-up function which determines whether to use the user given date of execution or current date.
     Also sets the file path and invokes the main program to proceed.
'''
def start():
    global g_mother_directory, g_file_location
    gc.enable()
    g_date_in_string = os.path.basename(os.path.abspath(args.td))
    print g_date_in_string
    g_file_location = g_mother_directory + get_current_date_folder(g_date_in_string) + "/"
    main()
    
    gc.disable()

start()

#============================================================[ EOC ]===============================================================
