import os
import commands
import os, sys, argparse
from configobj import ConfigObj
import time
import email_accumulated_results

parser = argparse.ArgumentParser(description='This program reads trade results directory\'s all file and accumulates them to single file.\n\
An e.g. command line is \n\
python src/accumulate_results.py -d ob/data/rs/20140205/t/ -e ob/e/9/ -a glmnet -t 0.000015 -m \"Taking tarde engine 4 \"',formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-d', required=True,help='Directory from where trade results is to be taken')
parser.add_argument('-e', required=True,help='Directory of the experiment')
parser.add_argument('-a', required=True,help='Algorithm name')
parser.add_argument('-t', required=True,help='Transaction Cost of data used')
parser.add_argument('-m', required=True,help='Meassge regarding experiment it has run')
args = parser.parse_args()

desired_statistic_line_numbers = [6,9,12,13,15]    # Line numbers for desired statistics 6: - Total Sell qty , 9 : Total Buy Qty , 15 :- Total Gross Profit
desired_statistic_names = ["FeatureCombination","EntryCL","ExitCL","TotalSellQty","TotalBuyQty","AvgSellP","AvgBuyPrice","AvgGrossProfit","AvgNetProfit"]
#os.chdir("")    # Directory name needed
summary_file_name = args.d + "Accumulated_Results_for_experiment_" + os.path.basename(os.path.abspath(args.e))+ "_on_date_" +time.strftime("%d_%m_%Y") + ".csv"
print "\nOpening Trade Result file : ", summary_file_name
print "\nStatistics to summarize are : "

for statistic in desired_statistic_names:
    print statistic

write_file_object = open(summary_file_name, 'w')
command_output = commands.getoutput("ls -1 "+args.d)
file_list = command_output.split("\n")

filtered_file_list = [file_name for file_name in file_list if ((file_name[-6:] == ".trade") and (args.a in file_name))]

for name in desired_statistic_names:
    write_file_object.write(name + ";")

write_file_object.write("\n")    # Header done

for file_name in filtered_file_list:
    
    feature = file_name[:file_name.index(args.a[0])]
    entryCL = file_name[file_name.index("."):file_name.index("-")]
    exitCL = file_name[file_name.index("-")+1:file_name.rindex(".")]
    temp_read_file_object = open(args.d + file_name, "r")
    line_list = temp_read_file_object.readlines()
    l_line_to_be_printed = ""
    last_occurence_of_space = line_list[desired_statistic_line_numbers[0]].rindex(": ")
    lTotSellQty = int(line_list[desired_statistic_line_numbers[0]][last_occurence_of_space + 1:])
    last_occurence_of_space = line_list[desired_statistic_line_numbers[1]].rindex(": ")
    lTotBuyQty = int(line_list[desired_statistic_line_numbers[1]][last_occurence_of_space + 1:])
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
    l_line_to_be_printed = ";".join(l_list_to_printed)
    
    write_file_object.write(l_line_to_be_printed+"\n")

print "\nAll the files are summarized according to the statistic parameters given"

l_files_to_be_mailed = [ summary_file_name , args.e + "design.ini" ]
print "Files being mailed are = " , l_files_to_be_mailed
email_accumulated_results.start_mail(l_files_to_be_mailed,os.path.basename(os.path.abspath(args.e)),args.m)
