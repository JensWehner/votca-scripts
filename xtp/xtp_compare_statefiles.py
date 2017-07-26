#!/usr/bin/env python
import sqlite3
import sys
import numpy as np
#import scipy.stats as st
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.patches as mpatches
import argparse as ap
from matplotlib.pyplot import cm 
import itertools
import numpy.ma as ma
import os

parser=ap.ArgumentParser(description="Compare statefiles")
parser.add_argument("-f1","--sqlfile1", help="Statefile 1 .sql file")
parser.add_argument("-f2","--sqlfile2", help="Statefile 2 .sql file")
parser.add_argument('-d',"--difference", type=int,default=0,help="Difference between couplings in log10 at which pairs shoudl be written to file.")
parser.add_argument("--difffile", default="errorpairs.txt",help="File to write pairs to")
parser.add_argument("-p","--plot",action='store_const', const=1, default=0,help="Plot histogramms, otherwise save pictures to file")
parser.add_argument("--save",action='store_const', const=1, default=0,help="Save histogramm data to file")
parser.add_argument("--plotfile", default="Compare.png",help="Filebeginning and type for histogramm files")
parser.add_argument("--type", default=-1,type=int,nargs="+",help="Type of pairs to compare, to have all enter negative value, default all")
parser.add_argument("-c","--carrier", default="s",type=str,choices=['e','h','s','t'],help="Specify which kind of Coupling to compare,Default s")
args=parser.parse_args()

args.plotfile,extension=os.path.splitext(args.plotfile)
def entropycalc(array1,array2):

	array1=array1/np.sum(array1)
	array2=array2/np.sum(array2)
	result=np.sum(array1*ma.log(array1/array2))
	return result



def readSql(sqlname,pairtype):
		sqlstatement = 'SELECT id, seg1, seg2,Jeff2{},drX,drY,drZ,type  FROM pairs'.format(args.carrier)
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
		pairs=[]
		for row in rows:
			#print row
			ident.append(float(row[0]))
			seg1.append(float(row[1]))
			seg2.append(float(row[2]))
			Jeff2.append(float(row[3]))
		   
			x.append(float(row[4]))
			y.append(float(row[5]))
			z.append(float(row[6]))
			pairs.append(int(row[7]))
		r=np.sqrt(np.array(x)**2+np.array(y)**2+np.array(z)**2)
		sql=np.array([ident,seg1,seg2,Jeff2,r,pairs])   
		pairs=np.array(pairs)
		if pairtype>=0:
			print "Reading {} for pairtype {}".format(sqlname,pairtype)
			return sql[:,(pairs==pairtype)]
			
		return sql


sql1list=[]
sql2list=[]
if type(args.type)==int:
	args.type=[args.type]

for pairtype in args.type:
	
	sql1temp=readSql(args.sqlfile1,pairtype)
	sql2temp=readSql(args.sqlfile2,pairtype)
	sql1=sql1temp[:,(sql1temp[3]>0)]
	sql2=sql2temp[:,(sql2temp[3]>0)]

	if sql1.shape!=sql2.shape:
		print "Sql files have different shapes. Exiting"
		sys.exit()
	#print np.array([sql1[3]/sql2[3]]).T

	if args.difference!=0:
		a=np.absolute(np.log10(sql1[3])-np.log10(sql2[3]))

		b=sql1[0:3]

		c=b[:,(a>args.difference)].T
		print "There are {} of {} pairs ( {:3.4f}% ) which have a bigger difference than 1E{} eV**2 for pairtype {}.".format(c.shape[0],a.shape[0],float(c.shape[0])/float(a.shape[0])*100,args.difference,pairtype)
		with open(args.difffile,'a') as f:
			np.savetxt(f,c,header="Pair id, seg1 id, seg2 id for a difference of 1E{} eV**2 for pairtype {}.".format(args.difference,pairtype),fmt="%.0f")
	sql1list.append(sql1)
	sql2list.append(sql2)

sql1=np.hstack(sql1list)
sql2=np.hstack(sql2list)	

#TO DOOOOO +++++++++++++++++++++++++++++= binning data according to r for both and then calculate entropy over each bin

coupling1=np.log(sql1[3])
r1=sql1[4]
coupling2=np.log(sql2[3])
r2=sql2[4]
binsJ=int(0.5*np.sqrt(coupling1.size))
binsr=int(0.5*np.sqrt(r1.size))
print [binsr,binsJ]
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
print "Jensen-Shannon divergence S={:2.4f}".format(entropy)
#====================

upperlimit=np.maximum(sql2[3].max(),sql1[3].max())
lowerlimit=np.minimum(sql2[3].min(),sql1[3].min())

if lowerlimit < 1E-15:
	lowerlimit =1E-15
print np.log10(lowerlimit), np.log10(upperlimit)


#==============1================
fig1 = plt.figure(1)
ax = fig1.add_subplot(111)
ax.set_title(args.sqlfile1)

nbins = 100
H, xedges, yedges = np.histogram2d(sql1[4],np.log10(sql1[3]),bins=nbins,normed=True)
 
# H needs to be rotated and flipped
H = np.rot90(H)
H = np.flipud(H)
 
# Mask zeros
Hmasked1 = np.ma.masked_where(H==0,H) # Mask pixels with a value of zero
#Hmasked=np.log10(Hmasked)

a=ax.pcolormesh(xedges,yedges,Hmasked1)#,vmin=-0.8,vmax=1.2)
cbar = fig1.colorbar(a)
cbar.ax.set_ylabel('Counts')

if args.plot==0:
	fig1.savefig(args.plotfile+"_"+args.sqlfile1+extension)
	plt.close()



#==============2================

fig2 = plt.figure(2)
ax = fig2.add_subplot(111)
ax.set_title(args.sqlfile2)



H, xedges, yedges = np.histogram2d(sql2[4],np.log10(sql2[3]),bins=nbins,normed=True)
 
# H needs to be rotated and flipped
H = np.rot90(H)
H = np.flipud(H)
 
# Mask zeros
Hmasked2 = np.ma.masked_where(H==0,H) # Mask pixels with a value of zero
#Hmasked=np.log10(Hmasked)

a=ax.pcolormesh(xedges,yedges,Hmasked2)#,vmin=-0.8,vmax=1.2)
cbar = fig2.colorbar(a)
cbar.ax.set_ylabel('Counts')

if args.plot==0:
	fig2.savefig(args.plotfile+"_"+args.sqlfile1+extension)
	plt.close()

fig3 = plt.figure(3)
ax = fig3.add_subplot(111)

ax.set_title("Distance vs Coupling/Jensen-Shannon divergence={:.3f}".format(entropy))
ax.set_xlabel("Distance [nm]")
ax.set_ylabel("Jeff2s [eV**2]")

#ax.set_ylim([ np.log10(lowerlimit), np.log10(upperlimit)])
markers=[".","x","v","^","D"]
for sqla,sqlb,pairtype,marker in itertools.izip(sql1list,sql2list,args.type,markers):
	ax.scatter(sqla[4],np.log10(sqla[3]),label="{}_{}".format(args.sqlfile1,pairtype),color="red",marker=marker) 
	ax.scatter(sqlb[4],np.log10(sqlb[3]),label="{}_{}".format(args.sqlfile2,pairtype),color="blue",marker=marker)	   
ax.legend()
if args.plot==0:
	fig3.savefig(args.plotfile+"_Dist_coup"+extension)
	plt.close()

if args.save:
	np.savetxt("sql1hist.dat",sql1.T,header="Data from {} pair id,seg1,seg2,Jeff2{},r,pairtype".format(args.sqlfile1,args.carrier),fmt=['%4d','%4d','%4d','%3.5e','%3.5e','%1d'] )
	np.savetxt("sql2hist.dat",sql2.T,header="Data from {} pair id,seg1,seg2,Jeff2{},r,pairtype".format(args.sqlfile2,args.carrier),fmt=['%4d','%4d','%4d','%3.5e','%3.5e','%1d'] )
	

fig4=plt.figure(4)
ax=fig4.add_subplot(111)
ax.set_title("Comparison of coupling constants for statefiles")
ax.set_xlabel(args.sqlfile1)
ax.set_ylabel(args.sqlfile2)

#ax.set_xlim([ np.log10(lowerlimit), np.log10(upperlimit)])
#ax.set_ylim([  np.log10(lowerlimit), np.log10(upperlimit)])

color=cm.rainbow(np.linspace(0,1,len(args.type)))
if False:
	for sqla,sqlb,pairtype,c in zip(sql1list,sql2list,args.type,color):
		correlation=np.corrcoef([np.log10(sqla[3]),np.log10(sqlb[3])])
		correlation2=np.corrcoef([sqla[3],sqlb[3]])
		print correlation
		print correlation2
		ax.plot(np.log10(sqla[3]),np.log10(sqlb[3]),',',label="singlets_type{}_corr={:+.3f}".format(pairtype,correlation[1,0]),c=c,markersize=1,marker="o",markeredgecolor=c,alpha=0.3)
	ax.legend(loc="upper left",markerscale=10,numpoints=1)


sort1=np.log10(np.sort(sql1[3]))
sort2=np.log10(np.sort(sql2[3]))
F=np.linspace(0,1,num=sort1.size)
minimum=max(np.percentile(sort1,0.3),np.percentile(sort2,0.3))
maximum=min(sort1[-1],sort2[-1])
binrange=[[minimum,maximum],[minimum,maximum]]
#print binrange
nbins = 50
H, xedges, yedges = np.histogram2d(np.log10(sql1[3]),np.log10(sql2[3]),bins=nbins,normed=True,range=binrange)
#print H
# H needs to be rotated and flipped
H = np.rot90(H)
H = np.flipud(H)
ax.set_xlim(binrange[0])
ax.set_ylim(binrange[1])
# Mask zeros
Hmasked = np.ma.masked_where(H==0,H) # Mask pixels with a value of zero
Hmasked=np.log10(Hmasked)

a=ax.pcolormesh(xedges,yedges,Hmasked)
cbar = fig4.colorbar(a)
cbar.ax.set_ylabel('Counts')

   
#ax.plot(np.log10(sql1[4]),np.log10(sql2[4]),',',label="electrons",color="red",marker="o",markersize=1,markeredgecolor="red")

ax.plot(binrange[0],binrange[1],color="black") 


if args.plot==0:
	fig4.savefig(args.plotfile+"_coup1_vs_coup2"+extension)
	plt.close()

correlation=np.corrcoef([np.log10(sql1[3]),np.log10(sql2[3])])
correlation2=np.corrcoef([sql1[3],sql2[3]])
print correlation
print correlation2



fig5=plt.figure(5)
ax=fig5.add_subplot(111)	
ax.plot(sort1,F,label=args.sqlfile1)
ax.plot(sort2,F,label=args.sqlfile2) 
#ax.set_xscale("log")
ax.legend(loc="upper left")	   
if args.plot==0:
	fig5.savefig(args.plotfile+"_percolation"+extension)
	plt.close()
if args.plot!=0:
	plt.show()
	plt.close()
			
			
			
			
		  
