#!/usr/bin/python
import os
import commands
import os, sys, argparse
from configobj import ConfigObj
import time
import email_accumulated_results
import attribute

parser = argparse.ArgumentParser(description='This program reads trade results directory\'s all file and accumulates them to single file.\n\
An e.g. command line is \n\
python src/accumulate_results.py -d ob/data/rs/20140205/t/ -e ob/e/9/ -a glmnet -t 0.000015 -m \"Taking tarde engine 4 \" -f 1',formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-d', required=True,help='Training Directory')
parser.add_argument('-e', required=True,help='Directory of the experiment')
parser.add_argument('-t', required=True,help='Transaction Cost of data used')
parser.add_argument('-m', required=True,help='Message regarding experiment it has run')
parser.add_argument('-nD',required=False,help='Number of days of data present')
args = parser.parse_args()

allDataDirectories = attribute.getListOfTrainingDirectoriesNames( int(args.nD) , args.d )
OSQ = 17
CBQ = 11
OSP = 23
CBP = 26
AvgGrossProfitShort = 29
OBQ = 12
CSQ = 18
OBP = 25
CSP = 24
AvgGrossProfitLong = 30

dictionaryOfType = {
                    "1":"500",
                    "2":"1000",
                    "3":"1500",
                    "4":"2000",
                    "5":"2500",
                    "6":"3000",
                    "7":"3500",
                    "8":"4000",
                    "9":"4500",
                    "10":"5000",
                    "11":"5500",
                    "20":"6000",
                    "12":"6500",
                    "13":"7000",
                    "14":"7500",
                    "15":"8000",
                    "16":"8500",
                    "17":"9000",
                    "18":"9500",
                    "19":"10000"
                    }  
desired_statistic_names = ["Directory","targetQtyUsed","StartEndTime","TradeQty",\
                               "TotalOpenSellQty","TotalCloseBuyQty","AvgOpenSellP","AvgCloseBuyPrice","AvgShortGrossProfit",\
                               "AvgShortNetProfit","TotalOpenBuyQty","TotalCloseSellQty","AvgOpenBuyPrice","AvgCloseSellPrice","AvgLongGrossProfit",\
                               "AvgLongNetProfit","TotalNetProfit","TotalNetProfitInDollars"]
#os.chdir("")    # Directory name needed

summary_file_name = args.e + "/Accumulated_Results_for_experiment_" + os.path.basename(os.path.abspath(args.e))+ "_on_date_" +time.strftime("%d_%m_%Y") + ".csv"
print "\nOpening Trade Result file : ", summary_file_name
print "\nStatistics to summarize are : "

for statistic in desired_statistic_names:
    print statistic

write_file_object = open(summary_file_name, 'w')
for name in desired_statistic_names:
    write_file_object.write(name + ";")
write_file_object.write("\n")    # Header done
l_list_of_all_results = []
lLastDayOrDayAfter = ""
index = 0
lastDayOfTraining = ""
dayAfterTraining = ""
for dirN in allDataDirectories :
    dirName = dirN.replace('/ro/','/rs/')
    tradeFileNameDirectory = dirName+"/r/"+os.path.basename(os.path.abspath(args.e))+"/"
    command_output = commands.getoutput("ls -1 "+tradeFileNameDirectory)
    file_list = command_output.split("\n")
    filtered_file_list = [file_name for file_name in file_list if (file_name[-13:] == ".targetResult")]
    for file_name in filtered_file_list:

        print "Filename " , file_name
#         r/targetExperimnet/DummyTradeEngine-d.20140610-l.16h00-17h00-tq.300-tarType20-dte.7.targetResult
        dataDirectory = file_name[file_name.index("-d.") + 3:file_name.index("-l.")]
        startAndEndTime = file_name[file_name.index("-l.") + 3:file_name.index("-tq.")]
        tradeQty = file_name[file_name.index("-tq.")+4:file_name.index("-tarType")]
        targetType = dictionaryOfType[ file_name[file_name.index("-tarType")+8:file_name.index("-dte.")] ]  
        temp_read_file_object = open(tradeFileNameDirectory + file_name, "r")
        line_list = temp_read_file_object.readlines()
        if len(line_list) == 0 :
            print (file_name,"is empty")
#            os.system('rm -rf ' + tradeFileNameDirectory + "/" + file_name)
            continue
        l_line_to_be_printed = ""
        last_occurence_of_space = line_list[OSQ].rindex(": ")
        lTotOpenSellQty = int(float(line_list[OSQ][last_occurence_of_space + 1:].strip()))
        last_occurence_of_space = line_list[CBQ].rindex(": ")
        lTotCloseBuyQty = int(float(line_list[CBQ][last_occurence_of_space + 1:].strip()))
        last_occurence_of_space = line_list[OSP].rindex(": ")
        lAvgOpenSellPrice = float(line_list[OSP][last_occurence_of_space + 1:])
        last_occurence_of_space = line_list[CBP].rindex(": ")
        lAvgCloseBuyPrice = float(line_list[CBP][last_occurence_of_space + 1:])
        last_occurence_of_space = line_list[AvgGrossProfitShort].rindex(": ")
        lAvgGrossProfitShort = float(line_list[AvgGrossProfitShort][last_occurence_of_space + 1:])
        lAvgTotTradedPriceShort = max( lTotOpenSellQty , lTotCloseBuyQty ) * ( lAvgOpenSellPrice + lAvgCloseBuyPrice )
        lTransactionCostShort = float(args.t) * lAvgTotTradedPriceShort
        try:
            lAvgNetProfitShort = ( (lAvgGrossProfitShort * max( lTotOpenSellQty , lTotCloseBuyQty )) - lTransactionCostShort ) / max( lTotOpenSellQty , lTotCloseBuyQty )
        except:
            lAvgNetProfitShort = 0.0
            
        last_occurence_of_space = line_list[OBQ].rindex(": ")
        lTotOpenBuyQty = int(float(line_list[OBQ][last_occurence_of_space + 1:].strip()))
        last_occurence_of_space = line_list[CSQ].rindex(": ")
        lTotCloseSellQty = int(float(line_list[CSQ][last_occurence_of_space + 1:].strip()))
        last_occurence_of_space = line_list[OBP].rindex(": ")
        lAvgOpenBuyPrice = float(line_list[OBP][last_occurence_of_space + 1:])
        last_occurence_of_space = line_list[CSP].rindex(": ")
        lAvgCloseSellPrice = float(line_list[CSP][last_occurence_of_space + 1:])
        last_occurence_of_space = line_list[AvgGrossProfitLong].rindex(": ")
        lAvgGrossProfitLong = float(line_list[AvgGrossProfitLong][last_occurence_of_space + 1:])
        lAvgTotTradedPriceLong = max( lTotCloseSellQty , lTotOpenBuyQty ) * ( lAvgOpenBuyPrice + lAvgCloseSellPrice )
        lTransactionCostLong = float(args.t) * lAvgTotTradedPriceLong
        try:
            lAvgNetProfitLong = ( (lAvgGrossProfitLong * max( lTotOpenBuyQty , lTotCloseSellQty )) - lTransactionCostLong ) / max( lTotOpenBuyQty , lTotCloseSellQty )
        except:
            lAvgNetProfitLong = 0.0
        lNetProfitLongAndShort = ( lAvgNetProfitShort * lTotOpenSellQty ) + ( lAvgNetProfitLong * lTotOpenBuyQty )
        if "nsecur" in os.path.abspath(args.e):
            lNetProfitLongAndShortInDollars = lNetProfitLongAndShort / ( 60 * 10000 )
        elif "nsefut" in os.path.abspath(args.e):
            lNetProfitLongAndShortInDollars = lNetProfitLongAndShort / ( 60 * 100 )
        elif "nseopt" in os.path.abspath(args.e):
            lNetProfitLongAndShortInDollars = lNetProfitLongAndShort / ( 60 * 100 )
        else:
            lNetProfitLongAndShortInDollars = ""
            print "Error in experiment file complete path name "
        
        l_list_to_printed = [dataDirectory , targetType , startAndEndTime , tradeQty ,\
                              str(lTotOpenSellQty) , str(lTotCloseBuyQty) ,str(lAvgOpenSellPrice), \
                              str(lAvgCloseBuyPrice),str(lAvgGrossProfitShort),str(lAvgNetProfitShort),
                              str(lTotOpenBuyQty) , str(lTotCloseSellQty) ,str(lAvgOpenBuyPrice), str(lAvgCloseSellPrice),str(lAvgGrossProfitLong),\
                              str(lAvgNetProfitLong),str(lNetProfitLongAndShort),str(lNetProfitLongAndShortInDollars)]
        l_list_of_all_results.append(l_list_to_printed)
        index = index + 1

sorted_list = sorted(l_list_of_all_results, key = lambda x: float(x[-2]))
for list_to_printed in sorted_list[::-1]:
    l_line_to_be_printed = ";".join(list_to_printed)
    write_file_object.write(l_line_to_be_printed+"\n")

print "\nAll the files are summarized according to the statistic parameters given"
write_file_object.close()

l_files_to_be_mailed = [ summary_file_name , args.e + "design.ini" ]
print "Files being mailed are = " , l_files_to_be_mailed
email_accumulated_results.start_mail(l_files_to_be_mailed,os.path.basename(os.path.abspath(args.e)),args.m)