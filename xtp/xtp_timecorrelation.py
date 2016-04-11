#!/usr/bin/env python
import sqlite3
import sys
import numpy as np
#import scipy.stats as st
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.patches as mpatches
import argparse 
from matplotlib.pyplot import cm 
import itertools
import numpy.ma as ma
import os

class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


parser=MyParser(description="Calculates the time correlation function of the siteenergies and (optionally) the coupling constants for a number of state files")
parser.add_argument("-o","--optionfile",nargs="+",type=str,required=True, help="List of .sql files")
parser.add_argument("-f","--outputfile", default="timecorrelation.txt",type=str,help="File to print results to. Default: timecorrelation.txt")
parser.add_argument("-t","--type", default="hest",type=str,help="Specify which kind of Coupling to compare, e,h,s,t")
parser.add_argument("-p","--plot",action='store_const', const=1, default=0,help="Plot time correlation")
parser.add_argument("-J","--Jcoupling",action='store_const', const=1, default=0,help="calculate time correlation also for J")
parser.add_argument("-J","--Jlog",action='store_const', const=1, default=0,help="calculate Correlation for log(J) instead of J")

args=parser.parse_args()

def readoptionsfile(optionfile):
    print "Reading options from {}".format(optionfile)
    parser=lxml.XMLParser(remove_comments=True)
    tree = lxml.parse(optionfile,parser)
    root = tree.getroot()      
    sqlnames=[]
    times=[]
    states=np.array([15])
    for child in root:
        if child.tag=="entry":
            for distance in child:
                times.append(float(child.find("time")))
                sqlnames.append(child.find("sqlname"))
    #print distances,rotations

    sortedlist=sroted(zip(times,sqlnames))
    return sortedlist

carriers=[]
if "e" in args.type:
    carriers.append("electron")
if "h" in args.type:
    carriers.append("hole")
if "s" in args.type:
    carriers.append("singlet")
if "t" in args.type:
    carriers.append("triplet")

type2sql={"electron":["eAnion","e"],"hole":["eCation","h"],"singlet":["eSinglet","s"],"triplet":["eTriplet","t"]}

def readSql(sqlname,carrier):
    sqlstatement = 'SELECT  seg1, seg2,Jeff2{},  FROM pairs'.format(type2sql[carrier][1])
    con = sqlite3.connect(sqlname)
    with con:
        cur = con.cursor()
        cur.execute(sqlstatement)
        rows = cur.fetchall()
    ident  = []
    seg1 = []
    seg2   = []
    Jeff2   = []
   
    for row in rows:
        #print row
        ident.append(float(row[0]))
        seg1.append(float(row[1]))
        seg2.append(float(row[2]))
        Jeff2.append(float(row[3]))
        
    
    sql=np.array([seg1,seg2,Jeff2])       
    return sql



    
    
    



for carrier in carriers:
    "Reading files for carrier {}".format(carrier)
    i=1

    sqlref=readSql(args.sqlref,carrier)
    if any(sqlref[3]==0):
        print "For the carrier {} some couplings are zero. Are you sure this is the correct carrier. Skipping it".format(carrier)
        continue
    fig=plt.figure(i,figsize=(14,10))
    i+=1
    ax=fig.add_subplot(111)
    ax.set_title("Percolation of couplings for {} with threshold={}".format(carrier,args.threshold))
    numofrows=sqlref[0].shape[0]
    markerdistance=numofrows/30
    F=np.linspace(0,1,num=numofrows)
    for sqlfile in sqllist:
        print "Reading file {}".format(sqlfile)
        sqlcomp=readSql(sqlfile,carrier)
        if sqlref.shape==sqlcomp.shape:
            correlation=np.corrcoef([sqlref[3],sqlcomp[3]])[1,0]
            correlations.append(correlation)
            entropy=calcentropy(sqlref,sqlcomp)
            entropies.append(entropy)
            percolation=np.sort(sqlcomp[3])
            percolationthreshold=np.percentile(percolation,args.threshold*100)
            if sqlfile==args.sqlref:
                ax.plot(np.log10(percolation),F,label="{} p={:1.2e} eV**2".format(sqlfile,percolationthreshold),marker="x",markevery=markerdistance)
            else:
                ax.plot(np.log10(percolation),F,label="{} p={:1.2e} eV**2".format(sqlfile,percolationthreshold))

            
            percolations.append(percolationthreshold)
        else:
            print "SQLfile {0} and SQLfile {1} do not have the same shape, skipping SQLfile {1}".format(args.sqlref,sqlfile)
            continue

    header="#Sqlfile, correlation,entropy,percolation[eV**2] for {} with reference {}\n".format(carrier,args.sqlref)
    filename="{}_{}.txt".format(os.path.splitext(args.outputfile)[0],type2sql[carrier][1])
    #print results
    #print header
    #print filename
    with open(filename,"w") as f:
        f.write(header)
        for name,corr,entr,perc in zip(sqllist,correlations,entropies,percolations):
            f.write("{:30s} {:1.3f} {:1.3f} {:1.3e}\n".format(name,corr,entr,perc))

    
        
        
    ax.legend(loc="upper left")
    ax.set_xlabel("log10(Jeff2s [eV**2])")
    ax.set_ylabel("#Couplings[Jeff2<x]/#Couplings")    
    if args.plot==0:
        plt.tight_layout()
        fig.savefig("{}_{}.png".format(args.plotfile,type2sql[carrier][1]))
        plt.close()
    if args.plot!=0:
        plt.show()
        plt.close() 


            
            
            
            
          
