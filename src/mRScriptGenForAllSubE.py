#!/usr/bin/python

import os
import argparse
from configobj import ConfigObj
import rCodeGen
import utility



def main():
    parser = argparse.ArgumentParser(description='Generates train.r. A sample command is mGenForE.py -e ob/e1/ ')
    parser.add_argument('-e', required=True,help='Experiement folder to use to find the features and targets')
    parser.add_argument('-a', required=True,help='Algorithm name')
    args = parser.parse_args()

    print "Using the experiment folder " + args.e
    
    config = ConfigObj(args.e+"/design.ini")

    print "The config parameters that I am working with are"
    print config 

    dirName=os.path.dirname(args.e)

    algo = rCodeGen.getAlgoName(args)

    rProgName = "train-"+algo+"ForAllSubE.r"
    rProgLocation = dirName+'/'+rProgName
    rScript = open(rProgLocation,'w')

    rScript.write('#!/usr/bin/Rscript \n')

    if(algo == 'glmnet'):
        rScript.write('require (glmnet) \n')
    elif(algo == 'randomForest'):
        rScript.write('require (randomForest) \n')
    elif(algo == 'mda'):
        rScript.write('require (mda) \n')

    rCodeGen.ForSetUpChecks(rScript)
    rCodeGen.ToReadTargetFile(rScript,config)
    rCodeGen.ToReadFeatureFiles(rScript,config)
    rCodeGen.ForSanityChecks(rScript,config)
    
    designFiles = utility.list_files(dirName+"/s/")

    for designFile in designFiles:
        print "Generating r code for " + designFile
        rScript.write('\n\nprint ("Running r code for ' + designFile + '")')
        config = ConfigObj(designFile)
        rCodeGen.ToCreateDataFrameForTraining(rScript,config)
        rCodeGen.ForTraining(rScript,args,config)
        rCodeGen.saveTrainingModel(rScript,args,os.path.dirname(designFile))

    rScript.close()
    print "Finished generating R training program: " + rProgLocation
    os.system("chmod +x "+rProgLocation)
    
if __name__ == "__main__":
    main()
