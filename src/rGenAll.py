#!/usr/bin/python


import argparse
parser = argparse.ArgumentParser(description='This program will run mGen.py and pGen.py. An e.g. command line is rGenAll.py -e e1/')
parser.add_argument('-e', required=True,help='Directory of the experiment')
parser.add_argument('-a', required=True,help='Algorithm name')
args = parser.parse_args()

import subprocess

print "Running mGen.py"
subprocess.call(["mGen.py","-e",args.e,"-a",args.a])

print "Generating pGen.py"
subprocess.call(["pGen.py","-e",args.e,"-a",args.a])

    
