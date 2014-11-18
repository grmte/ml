#!/usr/bin/python

from __future__ import division
from __future__ import print_function

import sys
sys.path.append("./ob/quality/tradeE15/")
import dd
from math import log
operators = ["<", ">", "="]

def add_node(pLine,pTree,pTreeVariablesPresent,pTreeType):
    lObj = dd.Tree()
    indexOfBracket = pLine.find(')')
    lObj.index = int(pLine[0:indexOfBracket])
    lIndex = indexOfBracket + 1
    variableName = ''
    indexOf1stDigit = 0
    lineSplitAfterOperator = ''
    for s in pLine[indexOfBracket+2:]:
        lIndex += 1
        if variableName.strip()=="root":
            indexOf1stDigit = lIndex
            lineSplitAfterOperator = pLine[indexOf1stDigit:].replace('(',' ').replace(')',' ').split()
            break
        if s in operators :
            if sum([ (item not in variableName) for item in operators ]) == 3:
#                 print("Variable Name detected = " ,variableName , "is")
                lTemp = variableName.strip()
                if lTemp not in  pTreeVariablesPresent:
                    pTreeVariablesPresent.append(lTemp)
                lObj.condition += lTemp
                variableName = s
            else:
                variableName = variableName + s
            
        elif s.isdigit() or s=='-':
#             print("Operator detcted = " , variableName.strip())
            lObj.condition += variableName.strip()
            indexOf1stDigit = lIndex
            lineSplitAfterOperator = pLine[indexOf1stDigit:].replace('(',' ').replace(')',' ').split()
            lObj.condition += lineSplitAfterOperator[0]
            lineSplitAfterOperator = lineSplitAfterOperator[1:]
            break
        else:
            variableName += s
    
    
#     print("Line = " , pLine[indexOf1stDigit:])
    if pTreeType == "1":
        lObj.totalPopulation = int(lineSplitAfterOperator[0])
        lObj.loss = int(lineSplitAfterOperator[1])
        lObj.tag = float(lineSplitAfterOperator[2])
        lObj.probability = (float(lineSplitAfterOperator[3])  , float(lineSplitAfterOperator[4]) )
        try:
            lineSplitAfterOperator[5]
            lObj.leaf  = 'y'
        except:
            lObj.leaf = 'n'
    else:
        lObj.totalPopulation = int(lineSplitAfterOperator[0])
        lObj.loss = float(lineSplitAfterOperator[1])
        lObj.tag = float(lineSplitAfterOperator[2])
        try:
            lineSplitAfterOperator[3]
            lObj.leaf  = 'y'
        except:
            lObj.leaf = 'n'        
     
    tempString = ";".join(map(str,[ lObj.index ,lObj.condition, lObj.totalPopulation ,lObj.loss,lObj.tag,lObj.probability, lObj.leaf ])  )
#     print(tempString)
    pTree[lObj.index] = lObj
    return pTree , pTreeVariablesPresent

def reading_tree(fileName,pTreeType):
    lTree = [ 0 for i in xrange(4078)]  
    lTreeVariablesPresent = [] 
    fp = open(fileName,'r')
    for line in fp.readlines():
        lTree,lTreeVariablesPresent = add_node(line,lTree,lTreeVariablesPresent,pTreeType)
    print("Variable name =" , lTreeVariablesPresent)
    return lTree,lTreeVariablesPresent

def findFinalCondition(pTreeIndex,pTree):
    lCondition = "(" + pTree[pTreeIndex].condition
    while(parent(pTreeIndex)>1):
        pTreeIndex = parent(pTreeIndex)
        lCondition = lCondition + ' and ' + pTree[pTreeIndex].condition
        
    lCondition = lCondition + ")"
    return lCondition
        
def left(index):
    return 2 * index 

def right(index):
    return 2 * index + 1

def parent(index):
    return int(index / 2) 

def traverse_tree(treeIndex,pTreeType,pAccuracy,pTree,pFinalCondition):
    
    if pTree[ left(treeIndex) ] != 0 :
        pFinalCondition = traverse_tree( left(treeIndex) ,pTreeType,pAccuracy,pTree,pFinalCondition)
#     print(str(treeIndex) , ";")
    
    lObj = pTree[ treeIndex]
    lCondition = ''
    if (pTreeType == "1" and ( lObj.probability[1] > float(pAccuracy) )) or (pTreeType == "2" and  ( lObj.tag > float(pAccuracy) )):
        lCondition = findFinalCondition(treeIndex,pTree)
    if lCondition != '':
        if pFinalCondition=='':
            pFinalCondition = lCondition
            lObj.finalCondition = pFinalCondition
        else:
            pFinalCondition = pFinalCondition + ' or ' +  lCondition   
    
    if pTree[ right(treeIndex) ] != 0 :
        pFinalCondition = traverse_tree( right(treeIndex) ,pTreeType,pAccuracy,pTree,pFinalCondition)
    return pFinalCondition

def breadth_first_traversal(pInputTree,pOutputTree,lTargetVariable,lFeatureValueDict):
    from collections import deque
    queueOfTreeNodes = deque()
    
    queueOfTreeNodes.append(1)
    
    while(len(queueOfTreeNodes)!=0):
        lInputTreeObject = pInputTree[queueOfTreeNodes.popleft()]
        
        for variable in pInputTree:
            #print('%s = lObject.featureDict["%s"]' %(variable,variable))
            exec('%s = lFeatureValueDict["%s"]' %(variable,variable))
            
        #short decisions
        if(lInputTreeObject.index==1 or eval(lInputTreeObject.condition) ):
            if pOutputTree[lInputTreeObject.index] == 0:
                pOutputTree[lInputTreeObject.index] = dd.Tree() 
            if lTargetVariable == 1:
                pOutputTree[lInputTreeObject.index].numberOfOnes += 1
            else:
                pOutputTree[lInputTreeObject.index].numberOfZeroes += 1
            pOutputTree[lInputTreeObject.index].condition = lInputTreeObject.condition
            pOutputTree[lInputTreeObject.index].index = lInputTreeObject.index  
            pOutputTree[lInputTreeObject.index].totalPopulation += 1
            pOutputTree[lInputTreeObject.index].leaf = lInputTreeObject.leaf
            if pInputTree[ right(lInputTreeObject.index) ] != 0 :
                queueOfTreeNodes.append(right(lInputTreeObject.index))
            if pInputTree[ left(lInputTreeObject.index) ] != 0 :
                queueOfTreeNodes.append(left(lInputTreeObject.index))         

    queueOfTreeNodes = None
    return pOutputTree   
                    
def traverse_nodes(pTreeType,pNodes,pTree):
    lFinalCondition = ''
    
    for n in pNodes:
        lCondition = findFinalCondition(int(n),pTree) 
        if lCondition != '':
            if lFinalCondition=='':
                lFinalCondition = lCondition
            else:
                lFinalCondition = lFinalCondition + ' or ' +  lCondition  
    return lFinalCondition 

def print_ouput_tree(pOutputTree , lOutputFileObject):
    from collections import deque
    queueOfTreeNodes = deque()
    
    queueOfTreeNodes.append(1)
    
    while(len(queueOfTreeNodes)!=0):
        lNodePoped = queueOfTreeNodes.popleft()
        numberOfTabs = log(lNodePoped)
        stringToPrint = ['    ' for tab in range(numberOfTabs+1)]
        stringToPrint += str(lNodePoped) + ") "
        stringToPrint += pOutputTree[lNodePoped].condition + "  "
        stringToPrint += str(pOutputTree[lNodePoped].totalPopulation) + "  "
        
        if pOutputTree[lNodePoped].numberOfZeroes < pOutputTree[lNodePoped].numberOfOnes :
            pOutputTree[lNodePoped].tag = '1'
            pOutputTree[lNodePoped].loss =  pOutputTree[lNodePoped].numberOfZeroes
        else:
            pOutputTree[lNodePoped].tag = '0'
            pOutputTree[lNodePoped].loss =  pOutputTree[lNodePoped].numberOfOnes
            
        stringToPrint += str(pOutputTree[lNodePoped].loss) + "  "
        stringToPrint += str(pOutputTree[lNodePoped].tag) + "  ("
        pOutputTree[lNodePoped].probability = ( pOutputTree[lNodePoped].numberOfZeroes/pOutputTree[lNodePoped].totalPopulation ,\
                                                 pOutputTree[lNodePoped].numberOfOnes /pOutputTree[lNodePoped].totalPopulation   )
        stringToPrint += str(pOutputTree[lNodePoped].probability[0]) + "  " + str(pOutputTree[lNodePoped].probability[1])
        if pOutputTree[lNodePoped].leaf == 'y':
            stringToPrint +=  "* \n"
        else:
            stringToPrint +=  "\n"
        lOutputFileObject.write(stringToPrint)
        if pOutputTree[ right(lNodePoped) ] != 0 :
            queueOfTreeNodes.append(right(lNodePoped))
        if pOutputTree[ left(lNodePoped) ] != 0 :
            queueOfTreeNodes.append(left(lNodePoped))         

    queueOfTreeNodes = None
    return pOutputTree       
                     
if __name__=='__main__':     
    lTree,lTreeVariablesPresent = reading_tree('/home/ml/tree2.txt',"2")
#     if len(p_nodes) == 0:
    lCondition = ''
    lCondition = traverse_tree(1,"2",.5,lTree,lCondition)
#     else:
#         nodes = p_nodes.split(";")
#         traverse_nodes("1",nodes,lTree)
    print(lCondition)
