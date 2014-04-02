#!/usr/bin/python
import glob, linecache, argparse

parser = argparse.ArgumentParser(description='This program will show the columns from the results file')
parser.add_argument('-d', required=True,help='Directory of the results file')
parser.add_argument('-e', required=True,help='File extension')
args = parser.parse_args()


interestedCols = list()

for file in glob.glob(args.d+"/*."+args.e):
    retrievedPL = linecache.getline(file, 16).strip().replace('Profit or loss per Qty traded is: ','')
    retrievedNumOfTrades = linecache.getline(file, 7).strip().replace('Assumed buy trade happened:','')

    if(len(retrievedPL)>1):
        retrievedPL = float(retrievedPL)
        retrievedPL = retrievedPL / 1000
        retrievedPL = round(retrievedPL)
    interestedCols.append([file,retrievedPL,retrievedNumOfTrades])

for row in interestedCols:
    print "%30s, %15s, %10s" % (row[0],row[1],row[2])
