#!/usr/bin/python                                                                                                                                                                                                                         
import os
import argparse
from configobj import ConfigObj
import rCodeGen
import attribute

def main():
    parser = argparse.ArgumentParser(description='Generates train.r. A sample command is :- src/corrRGenForE.py -e ob/e/nsefut/CorExpHINDALCO/ -td ob/data/ro/nsefut/20141017/ -dt 10 -iT HINDALCO -sP -1 -oT 0')
    parser.add_argument('-e', required=True,help='Experiement folder to use to find the features and targets')
    parser.add_argument('-td',required=True,help="Day on which it was trained")
    parser.add_argument('-dt',required=True,help="Number of days it was trained")
    parser.add_argument('-iT',required=False,help='Instrument name')
    parser.add_argument('-sP',required=False,help='Strike price of instrument')
    parser.add_argument('-oT',required=False,help='Options Type')
    args = parser.parse_args()

    attribute.initializeInstDetails(args.iT,args.sP,args.oT)
    print "Using the experiment folder " + args.e
    print args.e+"/design.ini"
    config = ConfigObj(args.e+"/design.ini")

    print "The config parameters that I am working with are"
    print config
    dirName=os.path.dirname(args.e)+"/"
    trainingDaysDirectory = attribute.getListOfTrainingDirectoriesNames( int(args.dt) , args.td ,args.iT)
    for l_trainingday in trainingDaysDirectory:
        rProgName = "corr-date-"+ os.path.basename(os.path.abspath(l_trainingday)) +"-td." + os.path.basename(os.path.abspath(args.td)) + "-dt." + args.dt + attribute.generateExtension() +".r"
        rProgLocation = dirName+'/'+rProgName
        rScript = open(rProgLocation,'w')
        rScript.write('#!/usr/bin/Rscript \n')
        rCodeGen.ForSetUpChecks(rScript)
        lCorrelationFileName = dirName + '/correlation-coef-date-'+  os.path.basename(os.path.abspath(l_trainingday)) + '-td.' + os.path.basename(os.path.abspath(args.td))+ '-dt.' + args.dt + attribute.generateExtension() + ".coef" 
        rCodeGen.ToReadTargetFile(rScript,config)
        for target in config['target']:
            rCodeGen.ToFindCorrelationDatewiseAndPrintingToFile(rScript,config,target,lCorrelationFileName)
        rScript.close()
        os.system("chmod +x "+rProgLocation)
#     print "Finished generating R training program: " + rProgLocation
    

if __name__ == "__main__":
    main()


