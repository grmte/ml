#!/usr/bin/python
import os
import commands
import os, sys, argparse
from configobj import ConfigObj
import time
import email_accumulated_results
import attribute
import pdb
parser = argparse.ArgumentParser(description='This program reads trade results directory\'s all file and accumulates them to single file.\n\
An e.g. command line is \n\
python src/accumulate_results.py -d ob/data/rs/20140205/t/ -e ob/e/9/ -a glmnet -t 0.000015 -m \"Taking tarde engine 4 \" -f 1',formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-td', required=True,help='Training Directory')
parser.add_argument('-dt', required=True,help="Number of days trained")
parser.add_argument('-e', required=True,help='Directory of the experiment')
parser.add_argument('-a', required=True,help='Algorithm name')
parser.add_argument('-t', required=True,help='Transaction Cost of data used')
parser.add_argument('-m', required=True,help='Meassge regarding experiment it has run')
parser.add_argument('-f', required=False,help='Format of the Trade File (can be 0 (old format) or 1 (new format)')
parser.add_argument('-nD',required=False,help='Number of days of data present')
parser.add_argument('-pd',required=False,help="Prediction Directory , if all days after 1st training set is to be given , then we need not specify it")
parser.add_argument('-iT',required=False,help='Instrument name')
parser.add_argument('-sP',required=False,help='Strike price of instrument')
parser.add_argument('-oT',required=False,help='Options Type')
args = parser.parse_args()

attribute.initializeInstDetails(args.iT,args.sP,args.oT)

if args.nD == None:
    args.nD = args.dt
allDataDirectories = attribute.getListOfTrainingDirectoriesNames( int(args.nD) , args.td ,args.iT)
if args.pd == None:
    allPredictionDataDirectories = allDataDirectories[int(args.dt)-1:]
else:
    allPredictionDataDirectories = args.pd.split(";")
if args.f == None:
    args.f = "1"    
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
    if args.iT is not None:
        desired_statistic_names = ["AlgorithmUsed","InstrName-Ticker","TrainingDirectory","NoOfDaysForTraining","PredictionDirectory","LastDayOfTrainingORActuallyPredictedDayAfterTraining","targetClass","WeightType","FeatureCombination",\
                               "EntryCL","ExitCL","OrderQty","TradeEngine","TotalOpenSellQty","TotalCloseBuyQty","AvgOpenSellP","AvgCloseBuyPrice","AvgShortGrossProfit",\
                               "AvgShortNetProfit","TotalOpenBuyQty","TotalCloseSellQty","AvgOpenBuyPrice","AvgCloseSellPrice","AvgLongGrossProfit",\
                               "AvgLongNetProfit","TotalNetProfit","TotalNetProfitInDollars"]

    else:
        desired_statistic_names = ["AlgorithmUsed","TrainingDirectory","NoOfDaysForTraining","PredictionDirectory","LastDayOfTrainingORActuallyPredictedDayAfterTraining","targetClass","WeightType","FeatureCombination",\
                               "EntryCL","ExitCL","OrderQty","TradeEngine","TotalOpenSellQty","TotalCloseBuyQty","AvgOpenSellP","AvgCloseBuyPrice","AvgShortGrossProfit",\
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

for dirN in allPredictionDataDirectories:
    dirName = dirN.replace('/ro/','/rs/')
    tradeFileNameDirectory = dirName+"/r/"+os.path.basename(os.path.abspath(args.e))+"/"
    command_output = commands.getoutput("ls -1 "+tradeFileNameDirectory)
    file_list = command_output.split("\n")
    filtered_file_list = [file_name for file_name in file_list if ((file_name[-7:] == ".result") and (args.a in file_name))]
    for file_name in filtered_file_list:
        algoName = file_name[:file_name.index("-")]

        
        if "-tTD." in file_name:
            trainingDirectory = file_name[file_name.index("-td.") + 4:file_name.index("-tTD.")]
        else:
            trainingDirectory = file_name[file_name.index("-td.") + 4:file_name.index("-dt.")]
        noOfDaysForTraining = file_name[file_name.index("-dt.") + 4:file_name.index("-targetClass.")]
       
        for directory in allDataDirectories:
            if trainingDirectory in directory:
                lastDayOfTraining = allDataDirectories[allDataDirectories.index(directory)+int(noOfDaysForTraining)-1]
                try:
                    dayAfterTraining = allDataDirectories[allDataDirectories.index(directory)+int(noOfDaysForTraining)]
                except:
                    dayAfterTraining = ""
                break
#        print noOfDaysForTraining , lastDayOfTraining , dayAfterTraining , dirN
        if lastDayOfTraining == dirN:
            lLastDayOrDayAfter = "LastDayOfTraining"
            #continue
        elif dayAfterTraining == dirN:
            lLastDayOrDayAfter = "DayAfterTraining"
            #continue
        
        else:
            lLastDayOrDayAfter = ""
            #continue
#        print "Filename " , file_name
        '''
        glmnet-td.20140128-dt.1-targetClass.binomial-f.1-wt.default-l.55-45-tq.300-te.7.result
        glmnet-td.20140128-dt.1-targetClass.binomial-f.ABC-wt.default-iT.RELIANCE-oT.0-sP.-1-l.60-50-tq.500-te.7.result
        glmnet-td.20140924-tTD30-dt.10-targetClass.binomial-f.AmBRAmB-wt.default-l.60-55-tq.300-te.15.result
        '''
        
        targetClass = file_name[file_name.index("-targetClass.") + 13:file_name.index("-f.")]
        feature = file_name[file_name.index("-f.") + 3:file_name.index("-wt.")]
        if args.iT is not None:
            try:
                weightTypeTaken = file_name[file_name.index("-wt.")+4:file_name.index("-iT.")]
                instrType = file_name[file_name.index("-iT.")+4:file_name.index("-oT.")]
                optionsType = file_name[file_name.index("-oT.")+4:file_name.index("-sP.")]
                strikePrice = file_name[file_name.index("-sP.")+4:file_name.index("-l.")]
            except:
                print "Except"
                continue
        else:
            weightTypeTaken = file_name[file_name.index("-wt.")+4:file_name.index("-l.")]
        try:
            l_levels = file_name[file_name.index("-l.") + 3:file_name.index("-tq")].split("-")
            
            entryCL = l_levels[0]
            exitCL = l_levels[1]
            try:
                buy_cut_off = l_levels[2]
                sell_cut_off = l_levels[3]
                continue
            except:
                pass
            orderQty = file_name[file_name.index("-tq.")+4:file_name.index("-te")]
            tradeEngine = file_name[file_name.index("-te.")+4:file_name.index(".result")]
#            if tradeEngine != "15":
#                continue
            temp_read_file_object = open(tradeFileNameDirectory + file_name, "r")
            line_list = temp_read_file_object.readlines()
        except:
            print "Except"
            continue
        if len(line_list) == 0 :
            print (file_name,"is empty")
#            os.system('rm -rf ' + tradeFileNameDirectory + "/" + file_name)
            continue
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
            if args.iT is not None:
                instrTicker = instrType +"-"+ strikePrice +"-"+ optionsType
                l_list_to_printed = [algoName ,instrTicker, trainingDirectory , noOfDaysForTraining , os.path.basename(os.path.abspath(dirN)) , lLastDayOrDayAfter , targetClass ,\
                                  weightTypeTaken , feature , entryCL , exitCL , orderQty , tradeEngine ,  str(lTotOpenSellQty) , str(lTotCloseBuyQty) ,str(lAvgOpenSellPrice), \
                                  str(lAvgCloseBuyPrice),str(lAvgGrossProfitShort),str(lAvgNetProfitShort),
                                  str(lTotOpenBuyQty) , str(lTotCloseSellQty) ,str(lAvgOpenBuyPrice), str(lAvgCloseSellPrice),str(lAvgGrossProfitLong),\
                                  str(lAvgNetProfitLong),str(lNetProfitLongAndShort),str(lNetProfitLongAndShortInDollars)]

            else:
                l_list_to_printed = [algoName , trainingDirectory , noOfDaysForTraining , os.path.basename(os.path.abspath(dirN)) , lLastDayOrDayAfter , targetClass ,\
                                  weightTypeTaken , feature , entryCL , exitCL , orderQty , tradeEngine ,  str(lTotOpenSellQty) , str(lTotCloseBuyQty) ,str(lAvgOpenSellPrice), \
                                  str(lAvgCloseBuyPrice),str(lAvgGrossProfitShort),str(lAvgNetProfitShort),
                                  str(lTotOpenBuyQty) , str(lTotCloseSellQty) ,str(lAvgOpenBuyPrice), str(lAvgCloseSellPrice),str(lAvgGrossProfitLong),\
                                  str(lAvgNetProfitLong),str(lNetProfitLongAndShort),str(lNetProfitLongAndShortInDollars)]
            l_list_of_all_results.append(l_list_to_printed)
            if len(l_list_of_all_results)%10000==0:
                print "Completed 10000 files accumulation"
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
