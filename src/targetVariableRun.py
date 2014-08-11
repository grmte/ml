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
parser.add_argument('-targetType',required=True,help="1,2,3,4 ")
parser.add_argument('-e',required=True,help="experiment design file to be used")
parser.add_argument('-run', required=True,help='dry or real')
parser.add_argument('-sequence', required=True,help='dp/lp/serial')
args = parser.parse_args()

if args.startTime == None:
    args.startTime = "9h00;10h00;11h00;12h00;13h00;14h00;15h00;16h00"
if args.endTime == None:
    args.endTime = "10h00;11h00;12h00;13h00;14h00;15h00;16h00;17h00"

def scriptWrapperForTradeGeneration(TargetNumber):
    utility.runCommand(["./ob/quality/tradeE7OnTargetVariable.py", "-orderQty", args.orderQty, "-d", args.d,"-startTime", args.startTime ,"-endTime",args.endTime ,"-tickSize",args.tickSize,\
                        "-targetType",TargetNumber,"-e",args.e],args.run,args.sequence)
        
if args.sequence == 'lp':
    # to run it in local parallel mode
    print "reached"
    pool = multiprocessing.Pool() # this will return the number of CPU's
    results = map(scriptWrapperForTradeGeneration,args.targetType.split(";"))
    print "reached"
else:
    results = map(scriptWrapperForTradeGeneration,args.targetType.split(";"))
        
