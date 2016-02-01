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


parser=MyParser(description="Calculates Jensen Entropy and correlation for many statefiles with reference to another one.")
parser.add_argument("-f","--sqlref",type=str,required=True, help="Reference .sql file")
parser.add_argument("-l","--sqlfilelist",nargs="+",type=str,required=True, help="List of .sql files")
parser.add_argument("-o","--outputfile", default="Correlation.txt",type=str,help="File to print results to. Default: Correlation.txt")
parser.add_argument("-t","--type", default="hest",type=str,help="Specify which kind of Coupling to compare, e,h,s,t")
parser.add_argument("--threshold", default=0.5,type=float,help="Percolationthreshold, Default=0.5")
parser.add_argument("-p","--plot",action='store_const', const=1, default=0,help="Plot percolation, otherwise save to file")
parser.add_argument("--plotfile", default="Percolation",help="Filename for Percolation ")
args=parser.parse_args()
#print args.show
if type(args.sqlfilelist)==str:
    args.sqlfilelist=[args.sqlfilelist]

sqllist=[args.sqlref]+args.sqlfilelist

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
    sqlstatement = 'SELECT id, seg1, seg2,Jeff2{},drX,drY,drZ  FROM pairs'.format(type2sql[carrier][1])
    con = sqlite3.connect(sqlname)
    with con:
        cur = con.cursor()
        cur.execute(sqlstatement)
        rows = cur.fetchall()
    ident  = []
    seg1 = []
    seg2   = []
    Jeff2   = []
    x=[]
    y=[]
    z=[]
    for row in rows:
        #print row
        ident.append(float(row[0]))
        seg1.append(float(row[1]))
        seg2.append(float(row[2]))
        Jeff2.append(float(row[3]))
        x.append(float(row[4]))
        y.append(float(row[5]))
        z.append(float(row[6]))
    r=np.sqrt(np.array(x)**2+np.array(y)**2+np.array(z)**2)
    sql=np.array([ident,seg1,seg2,Jeff2,r])       
    return sql

def entropycalc(array1,array2):

    array1=array1/np.sum(array1)
    array2=array2/np.sum(array2)
    result=np.sum(array1*ma.log(array1/array2))
    return result

def calcentropy(sql1,sql2):
    coupling1=np.log(sql1[3])
    r1=sql1[4]
    coupling2=np.log(sql2[3])
    r2=sql2[4]
    binsJ=int(0.5*np.sqrt(coupling1.size))
    binsr=int(0.5*np.sqrt(r1.size))
    hist1,redges,jedges=np.histogram2d(r1,coupling1,bins=[binsr,binsJ],normed=True)
    hist2,bla,bla2=np.histogram2d(r2,coupling2,bins=[redges,jedges],normed=True)
    entropy=0
    for q,p in zip(hist1.T,hist2.T):
    #https://en.wikipedia.org/wiki/Jensen%E2%80%93Shannon_divergence
        M=0.5*(q+p)
        m=ma.masked_where(M==0,M)
        p=ma.masked_where(p==0,p)
        q=ma.masked_where(q==0,q)
        result=0.5*entropycalc(p,m)+0.5*entropycalc(q,m)
        if type(result)==np.float64:
            entropy+=result
    entropy=entropy/float(binsr)
    return entropy


    
    
    



for carrier in carriers:
    "Reading files for carrier {}".format(carrier)
    i=1
    entropies=[]
    correlations=[]
    percolations=[]
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


            
            
            
            
          
