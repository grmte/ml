import argparse
parser = argparse.ArgumentParser(description='Ths program will write a csv file that will have the targets. An e.g. command line is: ./tGen.py -d ../data/20140207/ -m tBidGreaterThanAskInNext100')
parser.add_argument('-d', required=True,help='Location of the data file')
parser.add_argument('-m', required=True,help='Location of code module')
args = parser.parse_args()
