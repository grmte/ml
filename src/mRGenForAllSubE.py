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
    parser.add_argument('-s', required=True,help='Location of the folder containing all the sub experiments')
    parser.add_argument('-targetClass',required=True,help="binomial(target takes only true and false) / multinomial (target values takes more than 2 values)")
    parser.add_argumnet('-skipM',required=False,help="yes or no , If you want to regenerate already generated algorithm model file then make this value No")
    args = parser.parse_args()

    print "Using the experiment folder " + args.e
    
    config = ConfigObj(args.e+"/design.ini")

    print "The config parameters that I am working with are"
    print config 

    dirName=os.path.dirname(args.e)

    algo = rCodeGen.getAlgoName(args)

    args.s = args.s + "/"
    rProgName = "train-"+algo+"For"+os.path.basename(os.path.dirname(args.s))+"SubE.r"
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
    
    designFiles = utility.list_files(args.s)

    for designFile in designFiles:
        print "Generating r code for " + designFile
        rScript.write('\n\nprint ("Running r code for ' + designFile + '")')
        config = ConfigObj(designFile)
        lModelGeneratedAfterTraining = os.path.dirname(designFile) + '/' + algo  + '.model'
        if os.path.isfile(lModelGeneratedAfterTraining)and ( args.skipM == "yes" ):
            print "Model File " + lModelGeneratedAfterTraining + " already exists . So it will not be formed again . If you want to re-generate model then first delete this file and restart it"
        else:
            rCodeGen.ToCreateDataFrameForTraining(rScript,config)
            rCodeGen.ForTraining(rScript,args,config)
            rCodeGen.saveTrainingModel(rScript,args,os.path.dirname(designFile))

    rScript.close()
    print "Finished generating R training program: " + rProgLocation
    os.system("chmod +x "+rProgLocation)
    
if __name__ == "__main__":
    main()
