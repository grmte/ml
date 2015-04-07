#!/usr/bin/python                                                                                                                                                                                                                           
from itertools import islice
import itertools, os,argparse, subprocess, multiprocessing
from configobj import ConfigObj
from datetime import datetime
import attribute
import dataFile

parser = argparse.ArgumentParser(description='This program will run order book preparation and target experimenta nd feature experiment to togather \n', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-iT',required=True,help='Instrument name')
parser.add_argument('-sP',required=True,help='Strike price of instrument')
parser.add_argument('-oT',required=True,help='Options Type')
parser.add_argument('-td',required=False,help='Number of days after start training day specified . Defaults to 1 ')
parser.add_argument('-nDays',required=True,help="Number of days present in the data set")

args = parser.parse_args()

attribute.initializeInstDetails(args.iT,args.sP,args.oT)

allDataDirectories = attribute.getListOfTrainingDirectoriesNames( int(args.nDays) , args.td,"" )

for directories in allDataDirectories:
    l_filename = dataFile.getFileNameFromCommandLineParam(directories)
    if args.iT != None:
        l_newfilename = l_filename.split(args.iT)[0]+"Ex"+args.iT+l_filename.split(args.iT)[1]        
        print l_newfilename
        os.system("mv  "+ l_filename + "  "+l_newfilename)
        fp = open(l_newfilename, "r")
        fw = open(l_filename, "w")
        l_prev_band_part = ""
        while(1):
            l_next_n_lines = list(islice(fp , 5000))
            if not l_next_n_lines:
                break
            for line in l_next_n_lines:
                l_list = line.split(";")
                l_band_part =  ";".join(l_list[:-4])
                if(l_band_part == l_prev_band_part):
                    continue
                l_prev_band_part = l_band_part
                fw.write(line)
#     os.system("mv  "+ l_filename)
