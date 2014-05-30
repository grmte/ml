#!/usr/bin/python
import os
import commands
import os, sys, argparse
from configobj import ConfigObj
import time
import email_accumulated_results

parser = argparse.ArgumentParser(description='This program reads trade results directory\'s all file and accumulates them to single file.\n\
An e.g. command line is \n\
python src/accumulate_results.py -d ob/data/rs/20140205/t/ -e ob/e/9/ -a glmnet -t 0.000015 -m \"Taking tarde engine 4 \" -f 1',formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-pd', required=True,help='Prediction Directory')
parser.add_argument('-e', required=True,help='Directory of the experiment')
parser.add_argument('-a', required=True,help='Algorithm name')
parser.add_argument('-t', required=True,help='Transaction Cost of data used')
parser.add_argument('-m', required=True,help='Meassge regarding experiment it has run')
parser.add_argument('-f', required=True,help='Format of the Trade File (can be 0 (old format) or 1 (new format)')
args = parser.parse_args()

dirName = args.pd.replace('/ro/','/rs/')
tradeFileNameDirectory = dirName+"/r/"+os.path.basename(os.path.abspath(args.e))+"/"

if args.f == "0":
    desired_statistic_line_numbers = [6,9,12,13,15]    # Line numbers for desired statistics 6: - Total Sell qty , 9 : Total Buy Qty , 15 :- Total Gross Profit
elif args.f == "1":
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
else:
    print "\nNo valid -f argument given, -f 0 for old format and -f 1 for new format"
    sys.exit(-99)
  
if args.f == "0":
    desired_statistic_names = ["FeatureCombination","EntryCL","ExitCL","TotalSellQty","TotalBuyQty","AvgSellP","AvgBuyPrice","AvgGrossProfit","AvgNetProfit"]
else:
    desired_statistic_names = ["AlgorithmUsed","TrainingDirectory","NoOfDaysForTraining","PredictionDirectory","targetClass","WeightType","FeatureCombination",\
                               "EntryCL","ExitCL","TradeEngine","TotalOpenSellQty","TotalCloseBuyQty","AvgOpenSellP","AvgCloseBuyPrice","AvgShortGrossProfit",\
                               "AvgShortNetProfit","TotalOpenBuyQty","TotalCloseSellQty","AvgOpenBuyPrice","AvgCloseSellPrice","AvgLongGrossProfit",\
                               "AvgLongNetProfit","TotalNetProfit","TotalNetProfitInDollars"]
#os.chdir("")    # Directory name needed
summary_file_name = tradeFileNameDirectory + "Accumulated_Results_for_experiment_" + os.path.basename(os.path.abspath(args.e))+ "_on_date_" +time.strftime("%d_%m_%Y") + ".csv"
print "\nOpening Trade Result file : ", summary_file_name
print "\nStatistics to summarize are : "

for statistic in desired_statistic_names:
    print statistic

write_file_object = open(summary_file_name, 'w')
command_output = commands.getoutput("ls -1 "+tradeFileNameDirectory)
file_list = command_output.split("\n")

filtered_file_list = [file_name for file_name in file_list if ((file_name[-7:] == ".result") and (args.a in file_name))]

for name in desired_statistic_names:
    write_file_object.write(name + ";")

write_file_object.write("\n")    # Header done
l_list_of_all_results = []
for file_name in filtered_file_list:
    algoName = file_name[:file_name.index("-")]
    print "File Name " , file_name
    trainingDirectory = file_name[file_name.index("-td.") + 4:file_name.index("-dt.")]
    noOfDaysForTraining = file_name[file_name.index("-dt.") + 4:file_name.index("-targetClass.")]
    targetClass = file_name[file_name.index("-targetClass.") + 13:file_name.index("-f.")]
    feature = file_name[file_name.index("-f.") + 3:file_name.index("-wt.")]
    weightTypeTaken = file_name[file_name.index("-wt.")+3:file_name.index("-l.")]
    entryCL = "."+file_name[file_name.index("-l.") + 3:file_name.index("-te")][:(file_name[file_name.index("-l.") + 3:file_name.index("-te")]).index("-")]   
    exitCL = "."+file_name[file_name.index("-l.") + 3:file_name.index("-te")][(file_name[file_name.index("-l.") + 3:file_name.index("-te")]).index("-")+1:]  
    tradeEngine = file_name[file_name.index(".result")-1:file_name.index(".result")]        
    temp_read_file_object = open(tradeFileNameDirectory + file_name, "r")
    line_list = temp_read_file_object.readlines()
    l_line_to_be_printed = ""
    if args.f == "0":
        last_occurence_of_space = line_list[desired_statistic_line_numbers[0]].rindex(": ")
        lTotSellQty = int(float(line_list[desired_statistic_line_numbers[0]][last_occurence_of_space + 1:].strip()))
        last_occurence_of_space = line_list[desired_statistic_line_numbers[1]].rindex(": ")
        lTotBuyQty = int(float(line_list[desired_statistic_line_numbers[1]][last_occurence_of_space + 1:].strip()))
        last_occurence_of_space = line_list[desired_statistic_line_numbers[2]].rindex(": ")
        lAvgSellPrice = float(line_list[desired_statistic_line_numbers[2]][last_occurence_of_space + 1:])
        last_occurence_of_space = line_list[desired_statistic_line_numbers[3]].rindex(": ")
        lAvgBuyPrice = float(line_list[desired_statistic_line_numbers[3]][last_occurence_of_space + 1:])
        last_occurence_of_space = line_list[desired_statistic_line_numbers[4]].rindex(": ")
        lAvgGrossProfit = float(line_list[desired_statistic_line_numbers[4]][last_occurence_of_space + 1:])
        lAvgTotTradedPrice = max( lTotSellQty , lTotBuyQty ) * ( lAvgSellPrice + lAvgBuyPrice )
        lTransactionCost = float(args.t) * lAvgTotTradedPrice
        try:
            lAvgNetProfit = ( (lAvgGrossProfit * max( lTotSellQty , lTotBuyQty )) - lTransactionCost )  / max( lTotSellQty , lTotBuyQty )
        except:
            lAvgNetProfit = 0.0
        l_list_to_printed = [feature ,entryCL, exitCL ,str(lTotSellQty) , str(lTotBuyQty) ,str(lAvgSellPrice), str(lAvgBuyPrice),str(lAvgGrossProfit),str(lAvgNetProfit)]
        l_list_of_all_results.append(l_list_to_printed)
    else:
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
            lAvgNetProfitShort = ( (lAvgGrossProfitShort * max( lTotOpenSellQty , lTotCloseBuyQty )) - lTransactionCostShort )  / max( lTotOpenSellQty , lTotCloseBuyQty )
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
            lAvgNetProfitLong = ( (lAvgGrossProfitLong * max( lTotOpenBuyQty , lTotCloseSellQty )) - lTransactionCostLong )  / max( lTotOpenBuyQty , lTotCloseSellQty )
        except:
            lAvgNetProfitLong = 0.0
        lNetProfitLongAndShort =  ( lAvgNetProfitShort * lTotOpenSellQty ) + ( lAvgNetProfitLong *  lTotOpenBuyQty ) 
        if "nsecur" in os.path.abspath(args.e):
            lNetProfitLongAndShortInDollars = lNetProfitLongAndShort /  ( 60 * 10000 )  
        elif "nsefut" in os.path.abspath(args.e):
            lNetProfitLongAndShortInDollars = lNetProfitLongAndShort /  ( 60 * 100 )  
        elif "nseopt" in os.path.abspath(args.e):
            lNetProfitLongAndShortInDollars = lNetProfitLongAndShort /  ( 60 * 100 )
        else:
            lNetProfitLongAndShortInDollars = ""
            print "Error in experiment file complete path name "
        
        l_list_to_printed = [algoName , trainingDirectory , noOfDaysForTraining , os.path.basename(os.path.abspath(args.pd)) , targetClass ,\
                              weightTypeTaken , feature , entryCL , exitCL , tradeEngine , str(lTotOpenSellQty) , str(lTotCloseBuyQty) ,str(lAvgOpenSellPrice), \
                              str(lAvgCloseBuyPrice),str(lAvgGrossProfitShort),str(lAvgNetProfitShort),
                              str(lTotOpenBuyQty) , str(lTotCloseSellQty) ,str(lAvgOpenBuyPrice), str(lAvgCloseSellPrice),str(lAvgGrossProfitLong),\
                              str(lAvgNetProfitLong),str(lNetProfitLongAndShort),str(lNetProfitLongAndShortInDollars)]
        l_list_of_all_results.append(l_list_to_printed)

sorted_list = sorted(l_list_of_all_results, key = lambda x: float(x[-2]))    
for list_to_printed in sorted_list[::-1]:
    l_line_to_be_printed = ";".join(list_to_printed)    
    write_file_object.write(l_line_to_be_printed+"\n")

print "\nAll the files are summarized according to the statistic parameters given"
write_file_object.close()

l_files_to_be_mailed = [ summary_file_name , args.e + "design.ini" ]
print "Files being mailed are = " , l_files_to_be_mailed
email_accumulated_results.start_mail(l_files_to_be_mailed,os.path.basename(os.path.abspath(args.e)),args.m)
