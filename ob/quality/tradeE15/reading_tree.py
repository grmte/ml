#!/usr/bin/python

from __future__ import division
from __future__ import print_function

import sys
sys.path.append("./ob/quality/tradeE15/")
import dd
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
        else:
            pFinalCondition = pFinalCondition + ' or ' +  lCondition   
    
    if pTree[ right(treeIndex) ] != 0 :
        pFinalCondition = traverse_tree( right(treeIndex) ,pTreeType,pAccuracy,pTree,pFinalCondition)
    return pFinalCondition
        
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
                     
if __name__=='__main__':     
    lTree,lTreeVariablesPresent = reading_tree('/home/ml/tree2.txt',"2")
#     if len(p_nodes) == 0:
    lCondition = ''
    lCondition = traverse_tree(1,"2",.5,lTree,lCondition)
#     else:
#         nodes = p_nodes.split(";")
#         traverse_nodes("1",nodes,lTree)
    print(lCondition)
