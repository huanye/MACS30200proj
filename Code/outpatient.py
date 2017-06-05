#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 26 15:17:40 2017

@author: huanyeliu
"""
from mrjob.job import MRJob
import numpy as np

freq_dict={}
pmt_dict={}

class MRPatientCount(MRJob):
    
    def mapper(self,_,line):
       wlist = line.split(',')
       yield (wlist[5],wlist[4]),1
       yield (wlist[5],wlist[3]),1
       yield (wlist[5],wlist[2]),1
       yield (wlist[5],wlist[1]),1
       yield wlist[5],1
           
    def combiner(self,key,counts):
       yield key,sum(counts)
      
    def reducer(self,key,counts):
       freq = sum(counts)
       if type(key)==type(''):
           pmt_dict[key]=freq

       freq_dict[tuple(key)]=freq
       
 
class MRPhysicianPvalue(MRJob):
    def mapper(self,_,line):
        rec_list = line.split(',')
        # total probability over all payment type
        prob_dict = {}
        # diagnostic code
        d = rec_list[1]
        # procedure code
        p = rec_list[2]
        # birth year
        a = rec_list[3]
        # gender
        g = rec_list[4]
        # claim payment
        payment = int(rec_list[5])

        for pmt in pmt_dict:
            prob_d=prob_p=prob_a=prob_g=0
            if (pmt,d)in freq_dict:
                prob_d = freq_dict[(pmt,d)]/pmt_dict[pmt]
            if (pmt,p) in freq_dict:
                prob_p = freq_dict[(pmt,p)]/pmt_dict[pmt]
            if (pmt,a) in freq_dict:
                prob_a = freq_dict[(pmt,a)]/pmt_dict[pmt]
            if (pmt,g) in freq_dict:
                prob_g = freq_dict[(pmt,g)]/pmt_dict[pmt]
            prob_pmt = pmt_dict[pmt]/sum(pmt_dict.values())  
            prob_joint = prob_d*prob_p*prob_a*prob_g*prob_pmt
            prob_dict[pmt]=prob_joint
        
        prob_sum=sum(prob_dict.values())    
        prob_cond_dict_raw = {x:prob_dict[x]/prob_sum for x in prob_dict}
        #prob_cond_dict = self.smooth(prob_cond_dict_raw)

        yield rec_list[0],(payment,prob_cond_dict_raw)
    
    def reducer(self,NPI,claim_tuples):
        # the reducer implements a dynamic programming to compute the 
        # the probability that the number of max payments sent to this physician 
        # is great than or equal to observed number of max payments
        
        
        # sort the claim_tuples based on the first element of 
        # the tuple, the payment, to find out the maximum 
        # claim payment sent to the physician NPI
        claim_list = list(claim_tuples)
        order_pmt_list = sorted([x[0]for x in claim_list],reverse=True)
        
        max_payment = order_pmt_list[0]
        # next figure out the number of this max payment(num_max_payment)
        # among all number of payments(num_payment) sent to this
        # physician
        num_payment = len(claim_list)
        num_max_payment = 1
        
        for i in range(1,num_payment):
            if order_pmt_list[i]!= max_payment:
                num_max_payment = i
                break
        
        #dynamic programming to compute the probability that the number of
        #max payments sent to this physician is great than or equal to 
        #observed number of max payments(num_max_payment)
        
        #step 1: make a 2D table of size (num_payment+1)*(num_payment+1)
        #each value of which f[j][k] is the probability of j max payments 
        #among all k payments sent to this physician
        prob_table = [[0]*(num_payment+1) for i in range(num_payment+1)]
        #step 2: initialize the first row and first column of the table, which
        #are the base cases of the recursive relation of the dynamic
        #programming
        prob_table[0][0]=1
        
        for i in range(1,num_payment+1):
            prob_table[i][0]=0
        
        for i in range(1,num_payment+1):
            #(1-claim_list[i-1][1][str(max_payment)]) is the probability
            # that the ith claim payment sent to the physician is not equal to
            # the max payment. 
            prob_table[0][i] = (1-claim_list[i-1][1][str(max_payment)])*prob_table[0][i-1]
        
        #step 3: fill in other values of the 2D table based on the recursive 
        #relation of dynamic programming
        for j in range(1,num_payment+1):
            for k in range(1,num_payment+1):
                #the recursive relation where claim_list[i-1][1][str(max_payment)] 
                #is the probability that the ith claim payment sent to the 
                #physician equalsto the max payment, 
                #and 1-claim_list[i-1][1][str(max_payment)] is the probability 
                #of the opposite fact. 
                p1=claim_list[k-1][1][str(max_payment)]*prob_table[j-1][k-1]
                p2=(1-claim_list[k-1][1][str(max_payment)])*prob_table[j][k-1]
                prob_table[j][k] = p1+p2
                

        # step 4: compute the probability(pvalue) that that the number of
        # max payments sent to this physician is great than or equal to 
        # observed number of max payments
        pvalue= sum([prob_table[i][num_payment] for i in range(num_max_payment,num_payment+1)])
        #for i in range(num_max_payment,num_payment+1):
            #pvalue+=prob_table[i][num_payment]

        # step 5: compute the expected number of max payments
        expectation = sum([i*prob_table[i][num_payment] for i in range(1,num_payment+1)])
        #for j in range(1,num_payment+1):
            
        yield NPI, (pvalue, num_max_payment, expectation)
        
    def smooth(self,prob_dict):
        # an empty dictionay as the return dictionary 
        # after smoothing
        rv={}
        num = len(prob_dict)
        # number of zeros in the dictionary values list
        num_zero = sum(np.array(list(prob_dict.values()))==0)
        # smoothing
        for key in prob_dict:
            if prob_dict[key]==0:
                rv[key]=1.0/num
            else:
                rv[key]=prob_dict[key]*(1-num_zero*1.0/num)
        return rv
            

if __name__=='__main__':
    
    
    MRPatientCount.run()
    MRPhysicianPvalue.run()
    

    
   
        