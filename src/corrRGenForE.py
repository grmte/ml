#!/usr/bin/python                                                                                                                                                                                                                            

import os
import argparse
from configobj import ConfigObj
import rCodeGen
import attribute

def main():
    parser = argparse.ArgumentParser(description='Generates train.r. A sample command is mGenForE.py -e ob/e1/ ')
    parser.add_argument('-e', required=True,help='Experiement folder to use to find the features and targets')
    parser.add_argument('-sd',required=True,help="Day on which it was trained")
    parser.add_argument('-dt',required=True,help="Number of days it was trained")
    parser.add_argument('-iT',required=False,help='Instrument name')
    parser.add_argument('-sP',required=False,help='Strike price of instrument')
    parser.add_argument('-oT',required=False,help='Options Type')
    args = parser.parse_args()

    attribute.initializeInstDetails(args.iT,args.sP,args.oT)
    if args.skipM == None:
        args.skipM = "yes"

    print "Using the experiment folder " + args.e

    config = ConfigObj(args.e+"/design.ini")

    print "The config parameters that I am working with are"
    print config

    dirName=os.path.dirname(args.e)+"/"

    rProgName = "corr-sd." + os.path.basename(os.path.abspath(args.td)) + "-dt." + args.dt + attribute.generateExtension() +".r"
    rProgLocation = dirName+'/'+rProgName
    rScript = open(rProgLocation,'w')
    rScript.write('#!/usr/bin/Rscript \n')
    rCodeGen.ForSetUpChecks(rScript)
    lCorrelationFileName = dirName + '/' + '-td.' + os.path.basename(os.path.abspath(args.td))+ '-dt.' + args.dt + attribute.generateExtension()  
    rCodeGen.ToReadTargetFile(rScript,config)
    for target in config['target']:
        rCodeGen.ToReadFeatureFiles(rScript,config,target)
        rCodeGen.ForSanityChecks(rScript,config,target)
        rCodeGen.ToFindCorrelationAndPrintingToFile(rScript,config,target,lCorrelationFileName)

    rScript.close()
    print "Finished generating R training program: " + rProgLocation
    os.system("chmod +x "+rProgLocation)

if __name__ == "__main__":
    main()


