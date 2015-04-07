#!/usr/bin/python                                                                                                                                                                                                                                                             
from datetime import timedelta
import itertools, os,argparse, subprocess, multiprocessing
from configobj import ConfigObj
from datetime import datetime
import rCodeGen, utility
import attribute
import aGenForE

parser = argparse.ArgumentParser(description='This program will run order book preparation for ob experiment to togather \n', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-nDays',required=True,help="Number of days present in the data set")
parser.add_argument('-nComputers',required=True,help="Number of computers at which task has to be run present in the data set")
parser.add_argument('-td', required=True,help='Training directory')
parser.add_argument('-run', required=True,help='dry (only show dont execute) or real (show and execute)')
parser.add_argument('-sequence', required=True,help='lp (Local parallel) / dp (Distributed parallel) / serial')
parser.add_argument('-iT', required=False,help='Instrument_symbol_list')
parser.add_argument('-sP', required=False,help='Instrument_strikeprice_list')
parser.add_argument('-oT', required=False,help='instrument_option_list')
parser.add_argument('-dateList',required=False,help="date list for which it has top be run")
parser.add_argument('-insType',required=False,help="Opt/Cur")
parser.add_argument('-priceDepth',required=False,help="price depth")
parser.add_argument('-exp', required=False,help='Instruments_expiry_List')
parser.add_argument('-uGE',required=False,help="yes:-Expiry list given No:- expiry list taken automatically")
args = parser.parse_args()
def getListOfDataDirectoriesNames(nDays,start_dir):
    l_data_directory="/home/vikas/nselogdata/"
    l_start_date=datetime.strptime(start_dir, '%Y%m%d')
    index=0
    l_count =0
    l_data_directiories = []
    while(1):
        l_training_date = l_start_date + timedelta(days = index)
        index = index + 1
        if( l_training_date.weekday() == 5 or l_training_date.weekday() == 6): # Day is monday                                                                                                                                                                               
            continue
        l_training_date_in_string = l_training_date.strftime('%Y%m%d')
        l_date_folder = l_training_date_in_string[0:4] +"-"+ l_training_date_in_string[4:6] + "-"+ l_training_date_in_string[6:8]
        l_current_day = int(l_date_folder.split("-")[2])
        l_current_month = int(l_date_folder.split("-")[1])
        l_current_year = int(l_date_folder.split("-")[0])
        g_file_token = "M" + str(l_current_month) + "-" + "D" + str(l_current_day)
        g_NSE_filename = "NSE_" + g_file_token + "-Y" + str(l_current_year)[-2:] + ".txt"
        if os.path.exists(l_data_directory+ "/"+l_date_folder+"/"+g_NSE_filename):
            l_data_directiories.append(l_training_date_in_string)
            l_count = l_count+1
        if(l_count>=nDays):
            print l_count,nDays
            break
    return l_data_directiories
allDataDirectories = getListOfDataDirectoriesNames( int(args.nDays) , args.td)
print allDataDirectories
if args.sequence == "dp":
    for directories in allDataDirectories:
        commandList.append(["generate_orderbook_from_nsedata_v15JanY14.py ","-td",directories,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP,'-uGE','no','-insType','Opt'])                                                                                                    
        pass
    for chunkNum in range(0,len(commandList),int(args.nComputers)):
        lSubGenList = commandList[chunkNum:chunkNum+int(args.nComputers)]
        utility.runCommandList(lSubGenList,args)
        print dp.printGroupStatus()
else:
    def scriptWrapperForGeneratingOrderBook(trainingDirectory):
        utility.runCommand(["generate_orderbook_from_nsedata_v15JanY14.py","-td",trainingDirectory,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP,'-uGE','no','-insType','Opt'],args.run,args.sequence)
    results = map(scriptWrapperForGeneratingOrderBook,allDataDirectories)
