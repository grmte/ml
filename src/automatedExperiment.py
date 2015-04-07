#!/usr/bin/python
import os,sys,argparse
from configobj import ConfigObj
import dp
from termcolor import colored

parser = argparse.ArgumentParser(description='This program will run mGenForE.py and pGenForE.py. An e.g. command line is \n\                                                                                                               rGenForE.py -e ob/e/9.1/ -a glmnet -sequence serial -targetClass multinomial -skipM Yes -pd ob/data/ro/20140205 -skipP Yes', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-e', required=True,help='Directory of the experiment')
parser.add_argument('-td',required=True,help='Training Directory')
parser.add_argument("-orderQty",required=True,help="Order qty ")
parser.add_argument('-allSub',required=True,help="yes:-Run the progarm for all sub combinations , no:-Run Progarm for just one design file inside eexpiremnt main folder")
parser.add_argument('-run', required=True,help='dry or real')
parser.add_argument('-sequence', required=True,help='lp / dp / serial')
parser.add_argument('-nDays',required=True,help="Number of days present in the data set")

parser.add_argument('-a', required=False,help='Algorithm name')
parser.add_argument('-targetClass',required=False,help="binomial(target takes only true and false) / multinomial (target values takes more than 2 values)")
parser.add_argument('-skipT',required=False,help="yes or no , If you want to regenerated trade files then make this value no.  Defaults to yes")
parser.add_argument('-skipM',required=False,help="yes or no , If you want to regenerate already generated algorithm model file then make this value No")
parser.add_argument('-skipP',required=False,help="yes or no , If you want to regenerate already generated algorithm prediction file then make this value No")
parser.add_argument('-dt',required=False,help='No of day from start for which it is to be trained ')
parser.add_argument('-wt',required=False,help="default/exp , weight type to be given to different days")
parser.add_argument('-tickSize',required=False,help="Nse Currency = 25000 , Future Options = 5")
parser.add_argument('-t',required=False,help="TransactionCost")
parser.add_argument('-iT',required=False,help='Instrument name')
parser.add_argument('-sP',required=False,help='Strike price of instrument')
parser.add_argument('-oT',required=False,help='Options Type')
parser.add_argument("-nComputers",required=False,help="nComputers")
parser.add_argument('-pd',required=False,help="Prediction directory ")
parser.add_argument('-pdt',required=False,help="Number of prediction directory for whoch prediction is to be done")
parser.add_argument('-g', required=False,help='Generators directory')
args = parser.parse_args()


#=========Initializing all param and everything ======================
if args.skipT == None:
    args.skipT = "yes"
if args.skipM == None:
    args.skipM = "yes"
if args.skipP == None:
    args.skipP = "yes"
if args.dt == None:
    args.dt = "1"
if args.wt == None:
    args.wt = "default"
if args.pd == None:
    args.pd = args.td
if args.pdt == None:
    args.pdt = args.nDays
if args.g == None:
    args.g = "ob/generators/"
if args.targetClass == None:
    args.targetClass = "binomial"
if args.iT is not None and args.sP is None and args.oT is None:
    args.sP = "-1"
    args.oT = "0"
    
if "/nsecur/" in args.td:
    if args.t == None:
        args.t = "0.000015"
    if args.tickSize == None:
        args.tickSize = "25000" 
elif "/nsefut/" in args.td:
    if args.t == None:
        args.t = "0.00015"
    if args.tickSize == None:
        args.tickSize = "5" 

dp.printGroupStatus()


