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
    if((args.e).find("nsefut") >= 0):
        args.targetType= "12500_1.5;15000_1.5;17500_1.5;20000_1.5;12500_2.0;15000_2.0;17500_2.0;20000_2.0;12500_2.5;15000_2.5;17500_2.5;20000_2.5"
    else:
        args.targetType= "500;1000;1500;2000;2500;3000;3500;4000;4500;5000;5500;6000;6500;7000"
def scriptWrapperForTradeGeneration(TargetNumber):
    if((args.e).find("nsefut") >= 0):
        utility.runCommand(["./ob/quality/tradeE7OnTargetVariableNseFut.py", "-orderQty", args.orderQty, "-d", args.d,"-startTime", args.startTime ,"-endTime",args.endTime ,"-tickSize",args.tickSize,\
                        "-targetType",TargetNumber,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP,"-e",args.e],args.run,args.sequence)
    else:
        utility.runCommand(["./ob/quality/tradeE7OnTargetVariable.py", "-orderQty", args.orderQty, "-d", args.d,"-startTime", args.startTime ,"-endTime",args.endTime ,"-tickSize",args.tickSize,\
                        "-targetType",TargetNumber,"-iT",args.iT,"-oT",args.oT,"-sP",args.sP,"-e",args.e],args.run,args.sequence)
print("number of targets ",len(args.targetType.split(";")))        
if args.sequence == 'lp':
    # to run it in local parallel mode
    print "reached"
    pool = multiprocessing.Pool() # this will return the number of CPU's
    print("number of targets ",len(args.targetType.split(";")))
    results = map(scriptWrapperForTradeGeneration,args.targetType.split(";"))
    print "reached"
else:
    results = map(scriptWrapperForTradeGeneration,args.targetType.split(";"))
        
