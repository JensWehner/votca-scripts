#!/usr/bin/env python

from __tools__ import MyParser
from __tools__ import XmlParser
#import matplotlib.pyplot as plt
import lxml.etree as lxml
import subprocess as sp
import numpy as np


parser=MyParser(description="Tool to create histogramm for iexcitoncl from jobfile")
parser.add_argument("--format",type=str,default="Hist_{}",help="Title of histogramm and filename")
parser.add_argument("--printing",action='store_const', const=1, default=0,help="Print histogramms to txt file")
parser.add_argument("--bins",type=int,default=50,help="Number of bins")
parser.add_argument("--jobfiles",type=str, nargs="+",required=True,help="Name of jobfile")
parser.add_argument("--min",type=int, default=-14,help="Minimum log10(J2) to still count")
args=parser.parse_args()

if type(args.jobfiles)==str:
    args.jobfiles=[args.jobfiles]
    
for i,jobfile in enumerate(args.jobfiles):
    job=[]
    toosmall=0
    print "Reading in {}".format(jobfile)
    root=XmlParser(jobfile)
    for entry in root.iter('job'): 
        status=entry.find("status").text
        if status=="COMPLETE":
            coupling=entry.find("output")[0][0].get("jABstatic")
            j2=float(coupling)**2
            #if j2>10**args.min:
            job.append(j2)
            #else:
                #toosmall+=1 
    
    job=np.array(job)
    if i==0:
        total=job
    else:
        total+=job
    print "Read in {} jobs".format(len(job))
    print "{} Jobs have a coupling below 10^{} eV**2".format(toosmall,args.min)
    value,bins=np.histogram(np.log10(job),args.bins,density=True)
    
    if args.printing:
        bins=0.5*(bins[1:]+bins[:-1])
        result=np.array([bins,value])
        np.savetxt(args.format.format(jobfile)+".txt",result.T,header="Number of Integrals; J2 [eV**2]")                
    else:
        print "Currently not implemented"


total=total/float(len(args.jobfiles))
value,bins=np.histogram(np.log10(total),args.bins,density=True)
bins=0.5*(bins[1:]+bins[:-1])
result=np.array([bins,value])
np.savetxt("Total_hist.txt",result.T,header="Number of Integrals; J2 [eV**2]")              

    
