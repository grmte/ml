#!/usr/bin/python
import os, sys, argparse
import commands
from configobj import ConfigObj

from numpy import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import time,datetime

matrix = []
g_sim_running_qty_long = 0
g_sim_running_profit_long = 0
g_total_sim_traded_price_long = 0
gross_sim_mtm_profit_long = 0
g_sim_running_profit_short = 0
g_sim_running_qty_short = 0
g_total_sim_traded_price_short = 0
g_total_sim_traded_price_short = 0
g_transaction_cost = 0.00001
g_sim_gross_mtm_profit_list = []
g_sim_net_mtm_profit_list = []
g_epoch_timestamp_list = []

def plot(p_xlabel_list,p_ylabel_list,p_title,p_image_name):
    l_dates = matplotlib.dates.date2num(p_xlabel_list)
    # Create the plot for gross profit  
    ll1 = plt.plot_date(l_dates, p_ylabel_list[0], 'r')
    
    plt.title(p_title +'(Red Sim)')
    plt.xlabel('Timestamp')
    plt.ylabel(p_title)
    
    # Save the figure in a separate file
    plt.savefig(p_image_name)
    
    # Draw the plot to the screen
#    plt.show()
    plt.close()

def calculate_current_tick_sim_mtm_profit():
    global gross_sim_mtm_profit_long, g_sim_running_profit_long, g_sim_running_qty_long, gross_sim_mtm_profit_short, g_sim_running_profit_short, g_sim_running_qty_short, g_total_sim_traded_price_short, g_total_sim_traded_price_short,\
    g_total_sim_traded_price_long, g_transaction_cost
    global g_sim_gross_mtm_profit_list, g_sim_net_mtm_profit_list
    prviousIndex = 0
    for index in matrix: 
        l_action_performed_long = index[14]
        l_action_performed_short = index[14]
        
        if len(l_action_performed_long) > 5 or len(l_action_performed_short) > 5:
            #FOR LONG FILE----------------------------------------------------------------------
            if l_action_performed_long.find("OpenBuy"):
                if l_action_performed_long.find("Standing"):
                    l_trade_price_long = float(index[4]) +1
                else:
                    l_trade_price_long = float(index[5]) 
                l_trade_qty_long = abs(prviousIndex - index[1])
                    
                g_sim_running_qty_long += l_trade_qty_long
                g_sim_running_profit_long -= (l_trade_price_long * l_trade_qty_long)
                g_total_sim_traded_price_long += (l_trade_price_long * l_trade_qty_long)
                
            if l_action_performed_long.find("CloseSell"):
                if l_action_performed_long.find("Standing"):
                    l_trade_price_long = float(index[5]) - 1
                else:
                    l_trade_price_long = int(index[4])
                l_trade_qty_long = abs(prviousIndex - index[1])
                                
                g_sim_running_qty_long -= l_trade_qty_long
                g_sim_running_profit_long += (l_trade_price_long * l_trade_qty_long)
                g_total_sim_traded_price_long += (l_trade_price_long * l_trade_qty_long)

            if l_action_performed_short.find("OpenSell"):
                if l_action_performed_short.find("Standing"):
                    l_trade_price_short = float(index[5]) -1
                else:
                    l_trade_price_short = float(index[4])                
                l_trade_qty_long = abs(prviousIndex - index[2])
                g_sim_running_qty_short += l_trade_qty_short
                g_sim_running_profit_short += (l_trade_price_short * l_trade_qty_short)
                g_total_sim_traded_price_short += (l_trade_price_short * l_trade_qty_short)
                
            if l_action_performed_short.find("CloseBuy"):
                if l_action_performed_short.find("Standing"):
                    l_trade_price_short = float(index[4]) +1
                else:
                    l_trade_price_short = float(index[5]) 
                l_trade_qty_long = abs(prviousIndex - index[2])
                g_sim_running_qty_short -= l_trade_qty_short
                g_sim_running_profit_short -= (l_trade_price_short * l_trade_qty_short)
                g_total_sim_traded_price_short += (l_trade_price_short * l_trade_qty_short)
                
            prviousIndex = index
         
        gross_sim_mtm_profit_long = g_sim_running_profit_long + (float(index[4]) * g_sim_running_qty_long)
        gross_sim_mtm_profit_short = g_sim_running_profit_short - (float(index[5]) * g_sim_running_qty_short)
        
        l_mtm_net_profit_long = gross_sim_mtm_profit_long - ((g_total_sim_traded_price_long + (float(index[4]) * g_sim_running_qty_long)) *  g_transaction_cost)
        l_mtm_net_profit_short = gross_sim_mtm_profit_short - ((g_total_sim_traded_price_short + (float(index[5]) * g_sim_running_qty_short)) *  g_transaction_cost)
        net_sim_mtm_profit_long = l_mtm_net_profit_long
        net_sim_mtm_profit_short = l_mtm_net_profit_short
        
        l_current_obj_tot_gross_profit = gross_sim_mtm_profit_long + gross_sim_mtm_profit_short
        l_current_obj_tot_net_profit = l_mtm_net_profit_long + l_mtm_net_profit_short
        
        g_epoch_timestamp_list.append(index[0])
        
    return [l_current_obj_tot_gross_profit,l_current_obj_tot_net_profit]


def addDataRowToMatrix(pDataRow):
   dataColumns=pDataRow.split(';')
   matrix.append(dataColumns)
   
def getDataIntoMatrix(lFileName):
   fileHasHeader = 1
   headerSkipped = 0
   for dataRow in open(lFileName):
      if(fileHasHeader == 1 and headerSkipped != 1):
         headerSkipped = 1 
         continue
      dataRow=dataRow.rstrip('\n')
      addDataRowToMatrix(dataRow)
      
def makeFileForMarketToMarket():
    print matrix[0]
    print matrix[1]   
    
def main():
    lFileName = "/spa/ml/src/ml/ob/data/rs/20140205/t/9/9glmnet.10-.00.trade"
    if os.path.isfile(lFileName):
        print "Yes file is exist"
    else:
        print "File does not exist"
    getDataIntoMatrix(lFileName)
    makeFileForMarketToMarket()
    l_gross_net_sim_profit_list = calculate_current_tick_sim_mtm_profit()
    g_sim_gross_mtm_profit_list.append(l_gross_net_sim_profit_list[0])
    g_sim_net_mtm_profit_list.append(l_gross_net_sim_profit_list[1])

    l_yLabel_list = [g_sim_gross_mtm_profit_list]
    plot(g_epoch_timestamp_list , l_yLabel_list , "GROSS_MTM_SIM_LIVE" , "test.ping")
    

if __name__ == "__main__":
    main()
