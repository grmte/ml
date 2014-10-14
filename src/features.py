import commands
import os
import numpy
import sys

day, month = sys.argv[1:]
head = True
path = "/root/MLExp/nsecur/data/"
timelength = 5
read_file = path + [file for file in os.listdir(path) if ("M" + month + "-D" + day in file and ".txt" in file)][0]
print "selected file is ", read_file
write_file = read_file[:-4] + ".feature"
sep = ";"
header = commands.getoutput("head -1 " + read_file)
attributes = header.strip().split(sep)
ob = []
timeline = []
featuresum = [0, 0, 0, 0, 0]
covar_matrix = [[0, 0], [0, 0]]
length = 0

class Tick():
    
    def __init__(self, val):
        attr_val = [(name, value) for name,value in zip(attributes, val)]
        self.__dict__.update(attr_val)
        askp = [self.AskP0, self.AskP1, self.AskP2, self.AskP3, self.AskP4]
        askq = [self.AskQ0, self.AskQ1, self.AskQ2, self.AskQ3, self.AskQ4]
        bidp = [self.BidP0, self.BidP1, self.BidP2, self.BidP3, self.BidP4]
        bidq = [self.BidQ0, self.BidQ1, self.BidQ2, self.BidQ3, self.BidQ4]
        
        inv_wt = [sum([float(price) / float(qty) for price, qty in zip(askp[:i] + bidp[:i], askq[:i] + bidq[:i])]) for i in xrange(1,6)]
        inv_wt_sum = [sum([1 / float(qty) for qty in askq[:i] + bidq[:i]]) for i in xrange(1,6)]
        self.all_ab_feature = [price / qty for price,qty in zip(inv_wt, inv_wt_sum)]
        
index = 0

with open(read_file, 'r') as file:
    
    with open(write_file, 'w') as writer:
        
        for line in file.readlines():
            
            if head  == True:
                writer.write("TimeStamp;SerialNo;FeatureAll1;FeatureAll2;FeatureAll3;FeatureAll4;FeatureAll5;RatioFeatureAll1;RatioFeatureAll2;RatioFeatureAll3;RatioFeatureAll4;RatioFeatureAll5\n")
                head = False
                continue
            
            tick = Tick(line.strip().split(sep))
            ob.append(tick)
            ob = ob[1:] if len(ob) > 2 else ob
            
            featuresum[0] += tick.all_ab_feature[0]
            featuresum[1] += tick.all_ab_feature[1]            
            featuresum[2] += tick.all_ab_feature[2]            
            featuresum[3] += tick.all_ab_feature[3]            
            featuresum[4] += tick.all_ab_feature[4]
#             covar_matrix[0][0] += tick.best_ab_feature ** 2
#             covar_matrix[1][1] += tick.all_ab_feature ** 2
#             covar_matrix[0][1] += tick.all_ab_feature * tick.best_ab_feature
#             covar_matrix[1][0] = covar_matrix[0][1]
#             
            timeline.append([float(tick.TimeStamp[:10]) + float(tick.TimeStamp[11:-2]) / 10000000, tick.all_ab_feature[0],
                             tick.all_ab_feature[1], tick.all_ab_feature[2], tick.all_ab_feature[3], tick.all_ab_feature[4]])
            length += 1
            while timeline[-1][0] - timeline[0][0] > timelength:
                featuresum[0] -= timeline[0][1]
                featuresum[1] -= timeline[0][2]
                featuresum[2] -= timeline[0][3]
                featuresum[3] -= timeline[0][4]
                featuresum[4] -= timeline[0][5]

                timeline = timeline[1:]
#                 covar_matrix[0][0] -= tick.best_ab_feature ** 2
#                 covar_matrix[1][1] -= tick.all_ab_feature ** 2
#                 covar_matrix[0][0] -= tick.all_ab_feature * tick.best_ab_feature
                length -= 1
                
#             cov_array = [[covar_matrix[0][0] / length - (featuresum[0]) ** 2, covar_matrix[0][1] / length - (featuresum[0] * featuresum[1])], 
#                          [covar_matrix[0][1] / length - (featuresum[0] * featuresum[1]), covar_matrix[1][1] / length - (featuresum[1]) ** 2]]
            
#             slope_best = cov_array[0][1] / covar_matrix[0][0]
#             slope_list = [timeline[i+1][0] - timeline[i][0] for i in range(len(timeline)-1)]
#             
            array = ["%.6f" % timeline[-1][0], tick.SerialNo, str(tick.all_ab_feature[0]), str(tick.all_ab_feature[1]), str(tick.all_ab_feature[2]),
                     str(tick.all_ab_feature[3]), str(tick.all_ab_feature[4]), str(tick.all_ab_feature[0] *length / featuresum[0]), str(tick.all_ab_feature[1] *length / featuresum[1]), 
                     str(tick.all_ab_feature[2] *length / featuresum[2]), str(tick.all_ab_feature[3] *length / featuresum[3]), str(tick.all_ab_feature[4] *length / featuresum[4])]
            string = sep.join(array)
            writer.write(string + "\n")
            writer.flush()
            
            index += 1
            if index % 100000 == 1:
                print "line no :", index
            
