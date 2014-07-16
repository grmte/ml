#!/usr/bin/python
import os, sys, argparse
import commands
from configobj import ConfigObj

from numpy import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import time,datetime

import datetime, time

def calculate_epoch_time(p_epoch):
    l_dt = datetime.datetime.fromtimestamp(p_epoch)
    
    return str(l_dt.year) + "-" + str(l_dt.month) + "-" + str(l_dt.day) + " " + str(l_dt.hour) + ":" + str(l_dt.minute) + ":" + str(l_dt.second)

matrix = []
g_sim_running_qty_long = 0
g_sim_running_profit_long = 0.0
g_total_sim_traded_price_long = 0.0
gross_sim_mtm_profit_long = 0.0
g_sim_running_profit_short = 0.0
g_sim_running_qty_short = 0
g_total_sim_traded_price_short = 0.0
g_transaction_cost = 0.00001
g_sim_gross_mtm_profit_list_long = []
g_sim_gross_mtm_profit_list_short = []
g_sim_net_mtm_profit_list = []
g_epoch_timestamp_list = []

def plot(p_xlabel_list,p_ylabel_list,p_title,p_image_name):
    l_dates = matplotlib.dates.date2num(p_xlabel_list)
    # Create the plot for gross profit  
    ll1 = plt.plot_date(l_dates, p_ylabel_list, 'r')
    
    plt.title(p_title +'(Red Sim)')
    plt.xlabel('Timestamp')
    plt.ylabel(p_title)
    
    # Save the figure in a separate file
    plt.savefig(p_image_name)
    
    plt.close()

def calculate_current_tick_sim_mtm_profit():
    global gross_sim_mtm_profit_long, g_sim_running_profit_long, g_sim_running_qty_long, gross_sim_mtm_profit_short, g_sim_running_profit_short, g_sim_running_qty_short, g_total_sim_traded_price_short,\
    g_total_sim_traded_price_long, g_transaction_cost
    global g_sim_gross_mtm_profit_list_long,g_sim_gross_mtm_profit_list_short, g_sim_net_mtm_profit_list
    prviousIndex = [0] * 23
    fp = open("/home/vikas/ml/ob/quality/output.csv", "w")
    fp.write("g_sim_running_qty_long;g_sim_running_profit_long;g_total_sim_traded_price_long;g_sim_running_qty_short;g_sim_running_profit_short;g_total_sim_traded_price_short\n")
    for index in matrix: 
        l_action_performed_long = str(index[14])
        l_action_performed_short = str(index[11])
        
        if len(l_action_performed_long) > 5 or len(l_action_performed_short) > 5:
            #FOR LONG FILE----------------------------------------------------------------------
            if l_action_performed_long.find("OpenBuy") >= 0:
                if l_action_performed_long.find("Standing") >= 0:
                    l_trade_price_long = float(index[4]) + 25000
                else:
                    l_trade_price_long = float(index[5]) 
                l_trade_qty_long = abs(float(prviousIndex[1]) - float(index[1]))
                    
                g_sim_running_qty_long += l_trade_qty_long
                g_sim_running_profit_long -= (l_trade_price_long * l_trade_qty_long)
                g_total_sim_traded_price_long += (l_trade_price_long * l_trade_qty_long)
                
            if l_action_performed_long.find("CloseSell") >= 0:
                if l_action_performed_long.find("Standing") >= 0:
                    l_trade_price_long = float(index[5]) - 25000
                else:
                    l_trade_price_long = float(index[4])
                l_trade_qty_long = abs(float(prviousIndex[1]) - float(index[1]))
                                
                g_sim_running_qty_long -= l_trade_qty_long
                g_sim_running_profit_long += (l_trade_price_long * l_trade_qty_long)
                g_total_sim_traded_price_long += (l_trade_price_long * l_trade_qty_long)

            if l_action_performed_short.find("OpenSell") >= 0:
                if l_action_performed_short.find("Standing") >= 0:
                    l_trade_price_short = float(index[5]) - 25000
                else:
                    l_trade_price_short = float(index[4])                
                l_trade_qty_short = abs(float(prviousIndex[2]) - float(index[2]))
                g_sim_running_qty_short += l_trade_qty_short
                g_sim_running_profit_short += (l_trade_price_short * l_trade_qty_short)
                g_total_sim_traded_price_short += (l_trade_price_short * l_trade_qty_short)
                
            if l_action_performed_short.find("CloseBuy") >= 0:
                if l_action_performed_short.find("Standing") >= 0:
                    l_trade_price_short = float(index[4]) + 25000
                else:
                    l_trade_price_short = float(index[5]) 
                l_trade_qty_short = abs(float(prviousIndex[2]) - float(index[2]))
                g_sim_running_qty_short -= l_trade_qty_short
                g_sim_running_profit_short -= (l_trade_price_short * l_trade_qty_short)
                g_total_sim_traded_price_short += (l_trade_price_short * l_trade_qty_short)
            
            lineToPrint = str(g_sim_running_qty_long) + ";" + str(g_sim_running_profit_long) + ";" + str(g_total_sim_traded_price_long) + ";" + str(g_sim_running_qty_short) + ";" + str(g_sim_running_profit_short) + ";" + str(g_total_sim_traded_price_short) + "\n"
            fp.write(lineToPrint)
            prviousIndex = index
         
        gross_sim_mtm_profit_long = g_sim_running_profit_long + (float(index[4]) * g_sim_running_qty_long)
        gross_sim_mtm_profit_short = g_sim_running_profit_short - (float(index[5]) * g_sim_running_qty_short)
        
        l_epoch_time = calculate_epoch_time(float(index[0]))
        g_epoch_timestamp_list.append(datetime.datetime.strptime(l_epoch_time, '%Y-%m-%d %H:%M:%S'))
        
        g_sim_gross_mtm_profit_list_long.append(gross_sim_mtm_profit_long)
        g_sim_gross_mtm_profit_list_short.append(gross_sim_mtm_profit_short)
    fp.close()

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
    
def main():
    global g_sim_gross_mtm_profit_list_long, g_sim_gross_mtm_profit_list_short, g_epoch_timestamp_list
    lFileName = "/home/vikas/ml/ob/data/rs/nsecur/20140703/t/ABFeatureExp/glmnet-td.20140618-dt.10-targetClass.binomial-f.AB-wt.default-l.55-45-tq.300.trade"
    getDataIntoMatrix(lFileName)
    calculate_current_tick_sim_mtm_profit()
    
    print len(g_epoch_timestamp_list), len(g_sim_gross_mtm_profit_list_long), len(g_sim_gross_mtm_profit_list_short)
    
    plot(g_epoch_timestamp_list , g_sim_gross_mtm_profit_list_long , "GROSS_MTM_SIM_FOR_LONG" , "/home/vikas/ml/ob/quality/for-long.png")
    plot(g_epoch_timestamp_list , g_sim_gross_mtm_profit_list_short , "GROSS_MTM_SIM_FOR_SHORT" , "/home/vikas/ml/ob/quality/for-short.png")
    

if __name__ == "__main__":
    main()
