import argparse
parser = argparse.ArgumentParser(description='Ths program will write a csv file that will have the targets. An e.g. command line is: ./tGen.py -d ob/data/20140207/ -m ob/tBidGreaterThanAskInNext100')
parser.add_argument('-d', required=True,help='Location of the data file')
parser.add_argument('-m', required=True,help='Location of code module')
parser.add_argument('-n', required=False,help='This is a parameter for the generator. Specified number of rows in future to look into.')
args = parser.parse_args()
