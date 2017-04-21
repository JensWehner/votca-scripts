#!/usr/bin/env python
import sys
import numpy as np
import lxml.etree as lxml
import argparse

parser=argparse.ArgumentParser(description="Creates an aux basis set from a votca xtp basisset file")
parser.add_argument('-f',"--basisfile",type=str,required=True,help="xtp basissetfile")
parser.add_argument('-g',"--grouping",type=float,default=0.1,help="Cutoff at which basisfunctions are grouped together in deviation from the arithmetic mean; Default 0.1")
parser.add_argument('-c',"--cutoff",type=float,default=60,help="Cutoff for very localised basisfunctions; Default 60")
parser.add_argument('-l',"--lmax",type=int,default=4,help="maximum angular momentum in aux basisset: Default:4")

args=parser.parse_args()

if args.lmax>6:
	print "ERROR: Higher order functions than H (L=6) are not implemented"
	sys.exit()



class basisfunction(object):

	def __init__(self,decay,L):
		self.decay=decay
		self.L=L



class collection(object):

	def __init__(self):
		self.functions=[]
		self.com=0
		self.decay=0
		
	def addbasisfunction(self,function):
		self.functions.append(function)
		self.calcmean()
		self.calcdecay()
		return

	def addcollection(self,collection):
		self.functions+=collection.functions
		self.calcmean()
		self.calcdecay()
		return

	def calcmean(self):
		mean=0
		for i in self.functions:
			mean+=i.decay
		mean=mean/len(self.functions)
		self.com=mean		
		return


	def size(self):
		return len(self.functions)

	def calcdecay(self):
		decay=1
		for i in self.functions:
			decay=decay*i.decay
		self.decay=decay**(1/float(len(self.functions)))

		return

	def popbasisfunction(self):
		keep=[]
		pop=[]
		for i in self.functions:
			outside=isclose(i,self)
			if outside:
				pop.append(i)
			else:
				keep.append(i)
		self.functions=keep
		return pop

	def shellstring(self):
		Ls=[]
		for f in self.functions:
			if f.L not in Ls:
				Ls.append(f.L)
		Ls.sort()
		L2Shelltype={0:"S",1:"P",2:"D",3:"F",4:"G",5:"H",6:"I"}
		string=""
		for l in Ls:
			string+=L2Shelltype[l]
		return string
		

def isclose(function,collection):
	inside=False
	for f in collection.functions:
		if (abs(np.log(function.decay)-np.log(f.decay))<args.grouping*(1+np.log(function.L+1))):
			inside=True
			break
	#inside=((abs(function.decay-collection.decay)/collection.decay)<args.grouping)
	return inside


def isclosecol(col1,col2):
	inside=False
	for f in col1.functions:
		for g in col2.functions:
			if(abs(np.log(f.decay)-np.log(g.decay))<args.grouping):
				inside=True
				break
	return inside

def ShelltypetoL(shelltype):
	Shelltype2L={"S":0,"P":1,"D":2,"F":3,"G":4,"H":5,"I":6}

	return Shelltype2L[shelltype]

def createauxfunctions(basisfunctions):
	auxfunctions=[]
	for i in xrange(len(basisfunctions)):
		for j in xrange(i,len(basisfunctions)):
			decay=basisfunctions[i].decay+basisfunctions[j].decay	
			L=basisfunctions[i].L+basisfunctions[j].L
			if(L>args.lmax):
				continue
			if(decay>args.cutoff):
				continue
			auxfunctions.append(basisfunction(decay,L))

	print "{} aux functions created".format(len(auxfunctions))
	return auxfunctions

def sortauxfunctions(auxfunctions):
	Lmax=0
	for function in auxfunctions:
		if(function.L)>Lmax:
			Lmax=function.L
	print "Maximum angular momentum in aux basisset is {}".format(Lmax)
	functionsperL=[]
	for i in range(Lmax+1):
		functionsperL.append([])

	for function in auxfunctions:
		functionsperL[function.L].append(function)

	for i,L in enumerate(functionsperL):
		print "{} functions have L={}".format(len(L),i)
	return functionsperL

def readinbasisset(xmlfile):

	print "Parsing  {}\n".format(xmlfile)
	parser=lxml.XMLParser(remove_comments=True)
	tree = lxml.parse(xmlfile,parser)
	root = tree.getroot()
	print "Basisset name is {}".format(root.get("name"))
	for element in root.iter('element'): 
		
		processelement(element)	
	return

def clusterfunctionsperL(functions):
	functions.sort(key=lambda function: function.decay,reverse=True)
	collections=[]
	for function in functions:
		if not collections:
			#print "New"
			firstcollection=collection()
			firstcollection.addbasisfunction(function)
			collections.append(firstcollection)
		else:
			for col in collections:
				if isclose(function,col):
					#print "CLOSE",col.decay,function.decay
					col.addbasisfunction(function)
					break
			else:
					newcollection=collection()
					newcollection.addbasisfunction(function)
					collections.append(newcollection)
					
			
	print "Reduced functions from {} to {}".format(len(functions),len(collections))
	for i,col in enumerate(collections):
		print "{} Functions: {} Decay {}".format(i,col.size(),col.decay)
	return collections

def clustercollections(collections):
	collections.sort(key=lambda col: col.decay,reverse=True)
	finalshells=[]
	for col in collections:
		if not finalshells:
			finalshells.append(col)
		else:
			for shell in finalshells:
				if isclosecol(shell,col):
					shell.addcollection(col)
					break
			else:
				finalshells.append(col)
	print "Reduced functions from {} to {}".format(len(collections),len(finalshells))
	for i,col in enumerate(finalshells):
		print "{} Functions: {} Decay {} Type {}".format(i,col.size(),col.decay, col.shellstring())
	return finalshells
			
	



def processelement(elementxml):
		print "\nReading element {}".format(elementxml.get("name"))
		basisfunctions=[]
		for shell in elementxml.iter('shell'):
			for constant in shell.iter('constant'):
				decay=float(constant.get("decay"))
				for contraction in constant.iter("contractions"):
					shelltype=contraction.get("type")
					basisfunctions.append(basisfunction(decay,ShelltypetoL(shelltype)))

		print "Found {} basisfunctions".format(len(basisfunctions))
		auxfunctions=createauxfunctions(basisfunctions)
		functionsperL=sortauxfunctions(auxfunctions)
		collections=[]
		for L,functions in enumerate(functionsperL):
			print "Clustering L={}".format(L)
			collections+=clusterfunctionsperL(functions)
		shells=clustercollections(collections)
		finalshells=clustercollections(shells)
		
			

		
readinbasisset(args.basisfile)
	
	
	




		
		
	
	
	
