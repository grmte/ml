import argparse

parser = argparse.ArgumentParser(description='This program will write a csv file that will have the features. An e.g. command line is python aGen.py -d ob/data/20140207/ -m ob/fLTPOfCurrentRow')
parser.add_argument('-d', required=True,help='Directory of the data file')
parser.add_argument('-g', required=True,help='File location of the generators')
parser.add_argument('-n', required=False,help='This is a parameter for the attribute generator. Specifies number of rows in history to look back.')
parser.add_argument('-c', required=False,help='This is a parameter for the attribute generator. Specifies column to be used')
parser.add_argument('-e', required=False,help='Experiment name')
args = parser.parse_args()
