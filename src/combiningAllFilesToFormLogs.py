#!/usr/bin/python

import itertools, os,argparse, subprocess, multiprocessing
from configobj import ConfigObj
from datetime import datetime
import rCodeGen, utility


parser = argparse.ArgumentParser(description='This program will get results for all the subexperiments. \n\
An e.g. command line is \n\
rsGenForAllSubE.py -e ob/e/4/ -a glmnet -td ob/data/ro/20140204 -pd ob/data/ro/20140205 -g ob/generators/ -run real -sequence serial -targetClass multinomial -skipM Yes -skipP Yes',formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('-e', required=True,help='Directory of the experiment')
parser.add_argument('-a', required=True,help='Algorithm name.')
parser.add_argument('-td', required=True,help='Training directory')
parser.add_argument('-pd', required=True,help='Prediction directory')
parser.add_argument('-g', required=True,help='Generators directory')
parser.add_argument('-run', required=True,help='dry (only show dont execute) or real (show and execute)')
parser.add_argument('-sequence', required=True,help='lp (Local parallel) / dp (Distributed parallel) / serial')
parser.add_argument('-targetClass',required=False,help="binomial(target takes only true and false) / multinomial (target values takes more than 2 values)")
parser.add_argument('-skipM',required=False,help="yes or no , If you want to regenerate already generated algorithm model file then make this value No")
parser.add_argument('-skipP',required=False,help="yes or no , If you want to regenerate already generated algorithm prediction file then make this value No")
parser.add_argument('-skipT',required=False,help="yes or no , If you want to regenerated trade files then make this value no")
parser.add_argument('-mpMearge',required=False,help="yes or no , If you want to separate model and prediction files then make this no") 
args = parser.parse_args()

if args.skipM == None:
    args.skipM = "yes"
if args.skipP == None:
    args.skipP = "yes"
if args.skipT == None:
    args.skipT = "yes"
if args.mpMearge == None:
    args.mpMearge = "yes"
            
if(args.sequence == "dp"):
    import dp

config = ConfigObj(args.e+"/design.ini")
features = config["features"]

algo = rCodeGen.getAlgoName(args)

if args.targetClass == None:
    args.targetClass = "binomial"
    print "Since no class of target variable is specified so taking binomial class of target variable"