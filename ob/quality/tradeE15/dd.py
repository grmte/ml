
class Tick():
    def __init__(self,pCurrentDataRowTimeStamp,pAskP,pBidP,pAskQ,pBidQ,pLTP,pTTQ,pFeatureValueDict):
        self.AskP = pAskP
        self.AskQ = pAskQ
        self.BidP = pBidP
        self.BidQ = pBidQ
        self.LTP = pLTP
        self.TTQ  = pTTQ
        self.TTQChange = 0 
        self.NextLTP = 0
        self.currentTimeStamp = pCurrentDataRowTimeStamp
        self.bidPChangedInBetweenLastTickAndCurrentTick = 0
        self.askPChangedInBetweenLastTickAndCurrentTick = 0
        self.featureDict = pFeatureValueDict

gTreeVariablesPresent = []
gFileObjectsOfVariablesPresent = []
gGlobalTree ={'buy':[],'sell':[]} 
gFinalCondition = {'buy':{},'sell':{}}
gNoOfLineReadPerChunk = 10000
gTickSize = 25000
gMaxQty = 300
gNoOfLineReadPerChunk = 10000
g_quantity_adjustment_list_for_sell = {}
g_quantity_adjustment_list_for_buy = {}
gTransactionCost = .000015
currencyDivisor = 10000

class Tree(object):
    def __init__(self):
        self.condition = ''
        self.totalPopulation = 0
        self.loss = 0.0
        self.tag = 0
        self.probability = (0.0,0.0)
        self.index = ''
        self.leaf = 'n'
        self.finalCondition = ''
