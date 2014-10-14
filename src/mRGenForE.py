#!/usr/bin/python                                                                                                                                                                                                                            

import os
import argparse
from configobj import ConfigObj
import rCodeGen
import attribute

def main():
    parser = argparse.ArgumentParser(description='Generates train.r. A sample command is mGenForE.py -e ob/e1/ ')
    parser.add_argument('-e', required=True,help='Experiement folder to use to find the features and targets')
    parser.add_argument('-a', required=True,help='Algorithm name')
    parser.add_argument('-targetClass',required=True,help="binomial(target takes only true and false) / multinomial (target values takes more than 2 values)")
    parser.add_argument('-skipM',required=False,help="yes or no , If you want to regenerate already generated algorithm model file then make this value No")
    parser.add_argument('-td',required=True,help="Day on which it was trained")
    parser.add_argument('-dt',required=True,help="Number of days it was trained")
    parser.add_argument('-wt',required=True,help="default/exp , weight type to be given to different days")
    parser.add_argument('-iT',required=False,help='Instrument name')
    parser.add_argument('-sP',required=False,help='Strike price of instrument')
    parser.add_argument('-oT',required=False,help='Options Type')
    parser.add_argument('-double',required=False,help='Double training of in model')
    args = parser.parse_args()

    attribute.initializeInstDetails(args.iT,args.sP,args.oT)
    if args.skipM == None:
        args.skipM = "yes"

    print "Using the experiment folder " + args.e

    config = ConfigObj(args.e+"/design.ini")

    print "The config parameters that I am working with are"
    print config

    dirName=os.path.dirname(args.e)

    algo = rCodeGen.getAlgoName(args)
    if args.double:
        rProgName = "train" + algo + "-td." + os.path.basename(os.path.abspath(args.td)) + "-dt." + args.dt + "-wt." + args.wt + attribute.generateExtension() +"double.r"
    else:
        rProgName = "train" + algo + "-td." + os.path.basename(os.path.abspath(args.td)) + "-dt." + args.dt + "-wt." + args.wt + attribute.generateExtension() +".r"
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
    lAllFilePresent = True
    for target in config['target']:
        if args.double:
            lModelGeneratedAfterTraining = dirName + '/' + algo + target + '-td.' + os.path.basename(os.path.abspath(args.td))\
                             + '-dt.' + args.dt + '-targetClass.' + args.targetClass + "-wt." + args.wt+ attribute.generateExtension()  +'double.model'
        else:
            lModelGeneratedAfterTraining = dirName + '/' + algo + target + '-td.' + os.path.basename(os.path.abspath(args.td))\
                             + '-dt.' + args.dt + '-targetClass.' + args.targetClass + "-wt." + args.wt+ attribute.generateExtension()  +'.model'           
        if os.path.isfile(lModelGeneratedAfterTraining) and ( args.skipM.lower() == "yes" ):
            continue
        else:
            lAllFilePresent = False
            break
    if lAllFilePresent == False:
        rCodeGen.ToReadTargetFile(rScript,config)
        rCodeGen.ForWtVectorGeneration(rScript,args.wt.lower())

        for target in config['target']:
            rCodeGen.ToReadFeatureFiles(rScript,config,target)
            rCodeGen.ForSanityChecks(rScript,config,target)
            if args.double:
                lModelGeneratedAfterTraining = dirName + '/' + algo + target + '-td.' + os.path.basename(os.path.abspath(args.td))\
                                 + '-dt.' + args.dt + '-targetClass.' + args.targetClass + "-wt." + args.wt+ attribute.generateExtension()  +'double.model'
            else:
                lModelGeneratedAfterTraining = dirName + '/' + algo + target + '-td.' + os.path.basename(os.path.abspath(args.td))\
                                 + '-dt.' + args.dt + '-targetClass.' + args.targetClass + "-wt." + args.wt+ attribute.generateExtension()  +'.model' 
            if os.path.isfile(lModelGeneratedAfterTraining) and ( args.skipM.lower() == "yes" ):
                print "Model File " + lModelGeneratedAfterTraining + " already exists . So it will not be formed again . So it will not be formed again . If you want to re-generate model then re-run with -skipM=No"
            else:
                rCodeGen.ToCreateDataFrameForTraining(rScript,config,target)
                rCodeGen.ForTraining(rScript,args,config,target)
                if args.double:
                    rCodeGen.forPreparingWtVectorForDoubleTraining(rScript,args,target)
                    rCodeGen.saveTrainingModel(rScript,args,dirName,target,"double")
                else:
                    rCodeGen.saveTrainingModel(rScript,args,dirName,target)


    rScript.close()
    print "Finished generating R training program: " + rProgLocation
    os.system("chmod +x "+rProgLocation)

if __name__ == "__main__":
    main()


