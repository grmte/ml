#!/usr/bin/python

import os
import argparse
from configobj import ConfigObj
import rCodeGen

def main():
    parser = argparse.ArgumentParser(description='Generates train.r. A sample command is mGenForE.py -e ob/e1/ ')
    parser.add_argument('-e', required=True,help='Experiement folder to use to find the features and targets')
    parser.add_argument('-a', required=True,help='Algorithm name')
    parser.add_argument('-targetClass',required=True,help="binomial(target takes only true and false) / multinomial (target values takes more than 2 values)")
    parser.add_argument('-skipM',required=False,help="yes or no , If you want to regenerate already generated algorithm model file then make this value No")
    args = parser.parse_args()

    if args.skipM == None:
        args.skipM = "yes"
    
    print "Using the experiment folder " + args.e
    
    config = ConfigObj(args.e+"/design.ini")

    print "The config parameters that I am working with are"
    print config 

    dirName=os.path.dirname(args.e)

    algo = rCodeGen.getAlgoName(args)

    rProgName = "train-"+algo+".r"
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
    for target in config['target']:
        lModelGeneratedAfterTraining = dirName + '/' + algo +'-'+ target + '.model'
        if os.path.isfile(lModelGeneratedAfterTraining) and ( args.skipM.lower() == "yes" ):
            print "Model File " + lModelGeneratedAfterTraining + " already exists . So it will not be formed again . So it will not be formed again . If you want to re-generate model then re-run with -skipM=No"
        else:
            rCodeGen.ToCreateDataFrameForTraining(rScript,config,target)
            rCodeGen.ForTraining(rScript,args,config,target)
            rCodeGen.saveTrainingModel(rScript,args,dirName,target)

    rScript.close()
    print "Finished generating R training program: " + rProgLocation
    os.system("chmod +x "+rProgLocation)
    
if __name__ == "__main__":
    main()
