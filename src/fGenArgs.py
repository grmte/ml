import argparse

if 'parser' not in globals():
    parser = argparse.ArgumentParser(description='This program will write a csv file that will have the features. An e.g. command line is python fGen.py -d ob/data/20140207/ -m ob/fLTPOfCurrentRow')
    parser.add_argument('-d', required=True,help='Directory of the data file')
    parser.add_argument('-m', required=True,help='File location of code module')
    parser.add_argument('-n', required=False,help='This is a parameter for the feature generator. Specified number of rows in history to look back.')
    parser.add_argument('-c', required=False,help='This is a parameter for the feature generator. Soecifies column to be used')
    parser.add_argument('-e', required=False,help='Experiment name')
    args = parser.parse_args()
