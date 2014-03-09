import argparse
parser = argparse.ArgumentParser(description='This program will write a csv file that will have the features. An e.g. command line is python fGen.py -d ob/data/20140207/ -m ob/fLTPOfCurrentRow')
parser.add_argument('-d', required=True,help='Location of the data file')
parser.add_argument('-m', required=True,help='Location of code module')
args = parser.parse_args()
