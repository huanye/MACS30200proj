#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 26 15:17:40 2017

@author: huanyeliu
"""
from mrjob.job import MRJob
import numpy as np

freq_gender={}
pmt_dict={}
freq_bth={}
freq_proc={}
freq_diag={}
class MRPatientCount(MRJob):
    
    def mapper(self,_,line):
        wlist = line.split(',')
        yield (wlist[5],'gender'),wlist[4]
        yield (wlist[5],'birth_year'),wlist[3]
        yield (wlist[5],'proc'),wlist[2]
        yield (wlist[5],'diag'),wlist[1]
        yield wlist[5],1
           
      
    def reducer(self,key,counts):
        if type(key)==type(''):
            pmt_dict[key]=sum(counts)
        else:
            temp={}
            for a in list(counts):
                if a not in temp:
                    temp[a]=0
                temp[a]+=1
            if key[1]=='gender':
                freq_gender[key[0]]=max(list(temp.values()))
            if key[1]=='birth_year':
                freq_bth[key[0]]=max(list(temp.values()))
            if key[1]=='proc':
                freq_proc[key[0]]=max(list(temp.values()))
            if key[1]=='diag':
                freq_diag[key[0]]=max(list(temp.values()))
        

if __name__=='__main__':
    
    
    MRPatientCount.run()
    for key in freq_gender:
        freq_gender[key]=freq_gender[key]/pmt_dict[key]
    for key in freq_bth:
        freq_bth[key]=freq_bth[key]/pmt_dict[key]
    for key in freq_proc:
        freq_proc[key]=freq_proc[key]/pmt_dict[key]
    for key in freq_diag:
        freq_diag[key]=freq_diag[key]/pmt_dict[key]
    norm = sum(pmt_dict.values())
    for key in pmt_dict:
        pmt_dict[key]=pmt_dict[key]/norm
    outfile=open('para.csv','w')
    outfile.write('PMT,Pr(PMT),max{Pr(G|PMT)},max{Pr(B|PMT)},max{Pr(P|PMT)},max{Pr(D|PMT)}')
    outfile.write('\n')
    for key in pmt_dict:
        outfile.write(key)
        outfile.write(',')
        outfile.write(str(pmt_dict[key]))
        outfile.write(',')
        if key in freq_gender:
            outfile.write(str(freq_gender[key]))
        else:
            outfile.write('0')
        outfile.write(',')
        if key in freq_gender:
            outfile.write(str(freq_bth[key]))
        else:
            outfile.write('0')
        outfile.write(',')
        if key in freq_gender:
            outfile.write(str(freq_proc[key]))
        else:
            outfile.write('0')
        outfile.write(',')
        if key in freq_gender:
            outfile.write(str(freq_diag[key]))
        else:
            outfile.write('0')
        outfile.write('\n')        
    outfile.close()
        
    
    

    
   
        
