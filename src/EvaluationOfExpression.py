import pdb
tokenTypeDictionary = {
                       "OPERATOR":0,
                       "FEATURE":1,
                       "CONSTANT":2,
                       }
priority = {
            "[Pow]":1,
            "[Exp]":1,
            "[Log]":1,
            "[Add]":2,
            "[Subtract]":2,
            "[MultiplyBy]":3,
            "[DivideBy]":3,
            }

class token():
    def __init__(self):
        self.name = ''
        self.type = 1
 
def convertingInfixToPostfix(Feature_Name):        
    FetauresStack =[]
    stringBeingFormed = ''
    for i in Feature_Name:
        if i == '(':
            if stringBeingFormed != '':
                temp_token = token()
                temp_token.name = stringBeingFormed
                try:
                    float(stringBeingFormed)
                    temp_token.type =  "CONSTANT"
                    FetauresStack.append(temp_token)   
                except:
                    temp_token.type =  "FEATURE"
                    FetauresStack.append(temp_token)            
            temp_token = token()
            temp_token.name = i
            temp_token.type =  "OPENB"
            FetauresStack.append(temp_token)
            stringBeingFormed = ''
            continue
        if i == '[':
            if  stringBeingFormed != '':
                temp_token = token()
                temp_token.name = stringBeingFormed
                try:
                    float(stringBeingFormed)
                    temp_token.type =  "CONSTANT"
                    FetauresStack.append(temp_token)   
                except:
                    temp_token.type =  "FEATURE"
                    FetauresStack.append(temp_token)  
            stringBeingFormed = i
            continue
        if i == ']':
            stringBeingFormed = stringBeingFormed + i
            temp_token = token()
            temp_token.name = stringBeingFormed
            temp_token.type =  "OPERATOR" 
            FetauresStack.append(temp_token)        
            stringBeingFormed = ''
            continue
        if i == ')':
            if  stringBeingFormed != '':
                temp_token = token()
                temp_token.name = stringBeingFormed
                try:
                    float(stringBeingFormed)
                    temp_token.type =  "CONSTANT"
                    FetauresStack.append(temp_token)   
                except:
                    temp_token.type =  "FEATURE"
                    FetauresStack.append(temp_token)  
            temp_token = token()
            temp_token.name = i
            temp_token.type =  "CLOSEB"
            FetauresStack.append(temp_token)
            stringBeingFormed = ''
            continue
        stringBeingFormed = stringBeingFormed + i
    
    if  stringBeingFormed != '':
        temp_token = token()
        temp_token.name = stringBeingFormed
        try:
            float(stringBeingFormed)
            temp_token.type =  "CONSTANT"
            FetauresStack.append(temp_token)   
        except:
            temp_token.type =  "FEATURE"
            FetauresStack.append(temp_token)  
    
    outputPostFixStack = []
    outputOperatorStack = []
    for i in FetauresStack:
        if ( i.type == "FEATURE" ) or ( i.type == "CONSTANT" )   :
            outputPostFixStack.append(i)
        elif i.type == "OPENB":
            outputOperatorStack.append(i)
        elif i.type == "OPERATOR":
            while len(outputOperatorStack) > 0 and (outputOperatorStack[-1].type!='OPENB'):
                if priority[i.name] <= priority[outputOperatorStack[-1].name] :
                    element = outputOperatorStack.pop()
                    outputPostFixStack.append(element)
                else:
                    break
            outputOperatorStack.append(i)
        elif i.type == "CLOSEB":
            while len(outputOperatorStack) > 0 and (outputOperatorStack[-1].type!='OPENB'):
                element = outputOperatorStack.pop()
                outputPostFixStack.append(element) 
            if len(outputOperatorStack) > 0:
                element = outputOperatorStack.pop()           
    while len(outputOperatorStack) > 0 :
        element = outputOperatorStack.pop()
        outputPostFixStack.append(element)       
        
#     count = 0
#     for i in outputPostFixStack: 
#         print str(count) + ":" +  i.name + ":" + i.type
#         count += 1      
    return outputPostFixStack
