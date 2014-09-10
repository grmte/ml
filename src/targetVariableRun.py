#!/usr/bin/python
import argparse,os,multiprocessing
from datetime import timedelta
from datetime import datetime
import utility
import attribute

parser = argparse.ArgumentParser(description='This program will do trades to measure the quality of the experiment.\n\
 An e.g. command line is tradeE7OnTargetVariable.py -d ob/data/20140207/ -orderQty 500 -startTime 9 -endTime 5', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-orderQty',required=True,help='Order Quantity with which we trade')
parser.add_argument("-skipT",required=False,help="Skip creating trade files if already generated")
parser.add_argument('-d', required=True,help='Directory of the training data file')
parser.add_argument('-startTime', required=False,help='Start Time List')
parser.add_argument('-endTime', required=False,help='End Time List')
parser.add_argument('-tickSize',required=True,help="Nse Currency = 25000 , Future Options = 5")
parser.add_argument('-targetType',required=False,help="1,2,3,4 ")
parser.add_argument('-e',required=True,help="experiment design file to be used")
parser.add_argument('-run', required=True,help='dry or real')
parser.add_argument('-sequence', required=True,help='dp/lp/serial')
parser.add_argument('-iT',required=False,help='Instrument name')
parser.add_argument('-sP',required=False,help='Strike price of instrument')
parser.add_argument('-oT',required=False,help='Options Type')
args = parser.parse_args()
attribute.initializeInstDetails(args.iT,args.sP,args.oT)
if args.startTime == None:
    args.startTime = "9h00"
if args.endTime == None:
    args.endTime = "17h00"
if args.targetType == None:
    args.targetType= "500_1.5;1000_1.5;1500_1.5;2000_1.5;2500_1.5;3000_1.5;3500_1.5;4000_1.5;4500_1.5;5000_1.5;5500_1.5;6000_1.5;6500_1.5;7000_1.5;7500_1.5;8000_1.5;8500_1.5;9000_1.5;9500_1.5;10000_1.5;500_2.0;1000_2.0;1500_2.0;2000_2.0;2500_2.0;3000_2.0;3500_2.0;4000_2.0;4500_2.0;5000_2.0;5500_2.0;6000_2.0;6500_2.0;7000_2.0;7500_2.0;8000_2.0;8500_2.0;9000_2.0;9500_2.0;10000_2.0;500_2.5;1000_2.5;1500_2.5;2000_2.5;2500_2.5;3000_2.5;3500_2.5;4000_2.5;4500_2.5;5000_2.5;5500_2.5;6000_2.5;6500_2.5;7000_2.5;7500_2.5;8000_2.5;8500_2.5;9000_2.5;9500_2.5;10000_2.5"
def scriptWrapperForTradeGeneration(TargetNumber):
    utility.runCommand(["./ob/quality/tradeE7OnTargetVariable.py", "-orderQty", args.orderQty, "-d", args.d,"-startTime", args.startTime ,"-endTime",args.endTime ,"-tickSize",args.tickSize,\
                        "-targetType",TargetNumber,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP,"-e",args.e],args.run,args.sequence)
        
if args.sequence == 'lp':
    # to run it in local parallel mode
    print "reached"
    pool = multiprocessing.Pool() # this will return the number of CPU's
    results = map(scriptWrapperForTradeGeneration,args.targetType.split(";"))
    print "reached"
else:
    results = map(scriptWrapperForTradeGeneration,args.targetType.split(";"))
        
