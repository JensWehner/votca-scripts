import numpy as np
import numpy.linalg as lg
import copy 
from __xtpAtom__ import atom
class molecule:
	def __init__(self):
		self.pos=np.array([0,0,0])
		self.id=""
		self.name=""
		self.atomlist=[]
		self.coG=None
		self.homo=None
		self.lumo=None
		self.Egroundstate=None
		self.DFTenergies=None
		self.QPenergies=None
		self.Singlets=None
		self.Triplets=None
		self.osc=None
		self.TrDip=None
		self.TripletCTpop=None
		self.SingletCTpop=None
		self.SingletCharge=None
		self.TripletCharge=None

	def getEnergy(self,level):
		index=np.where(self.DFTenergies[0]==level)
		energy=self.DFTenergies.T[index][0][1:]
		return energy


	def calccoG(self):
			
		self.coG=self.calcgeomean()
		self.pos=self.coG	
	

	def __add__(self,other):
		atomlist=[]
		for i in self.atomlist:
			atomlist.append(i)
		for i in other.atomlist:
			atomlist.append(i)
		newMol=molecule()
		newMol.atomlist=atomlist
		newMol.calccoG()	
		return newMol

	def setName(self,name):
		self.name=name

	def setId(self,molid):
		self.id=molid

	def addHomoLumo(self,homo,lumo):
		self.homo=homo
		self.lumo=lumo
	
	def addEgroundstate(self,E):
		self.Egroundstate=E


	def addDFTenergies(self,energies):
		self.DFTenergies=energies


	def addQPenergies(self,energies):
		self.QPenergies=energies
	
	def addSinglets(self,energies,osc,Trdip):
		self.Singlets=energies
		self.osc=osc
		self.TrDip=Trdip

	def addTriplets(self,energies):
		self.Triplets=energies

	def addFragmentsSinglet(self,CTpop,charge):
		self.SingletCTpop=CTpop
		self.SingletCharge=charge
	def addFragmentsTriplet(self,CTpop,charge):
		self.TripletCTpop=CTpop
		self.TripletCharge=charge
	
	def copy(self):
		return copy.deepcopy(self)

	def shift(self,shift):

		for i in self.atomlist:
			i.shift(shift)
		self.calccoG()

	def updateatom(self,atom):
		for a in self.atomlist:
			if all(np.isclose(a.pos,atom.pos)) and a.type==atom.type:
				a=atom
				return
		self.atomlist.append(atom)
		return
				

	def calcQ(self):
		q=0
		for i in self.atomlist:
			q+=i.q
		return q

	def calcgeomean(self):
		mean=np.zeros(3)
		for i in self.atomlist:
			mean+=i.pos
		mean=mean/float(len(self.atomlist))
		return mean

	def calcDmonopoles(self):
		mean=self.calcgeomean()
		d=np.zeros(3)
		for i in self.atomlist:
			d+=(i.pos-mean)*i.q
		
		return d

	def rotate(self,rotation,r=None):
		axis=rotation[0:3]
		angle=rotation[-1]*np.pi/180.0
		#print angle
		norm=axis/lg.norm(axis)
		crossproduktmatrix=np.array([[0,-norm[2],norm[1]],[norm[2],0,-norm[0]],[-norm[1],norm[0],0]])
		R=np.cos(angle)*np.identity(3)+np.sin(angle)*crossproduktmatrix+(1-np.cos(angle))*np.outer(norm,norm)
		#print R 
		self.calccoG()
		if r==None:
			save=self.coG
			self.shift(-save)
			for i in self.atomlist:
				i.pos=np.dot(R,i.pos)	
			self.shift(save)
		else:
			save=r-self.coG
			self.shift(-save)
			for i in self.atomlist:
				i.pos=np.dot(R,i.pos) 
			self.shift(np.dot(R,i.pos))	
		self.calccoG()
			
	def writexyz(self,filename,header=True):
		with open(filename,"w") as f:
			if header!=False:
				f.write("{}\n".format(len(self.atomlist)))
				if type(header)==str:
					f.write("#{} {} {}\n".format(self.name,self.id,header))
				else:
					f.write("#{} {} Created by Python Script\n".format(self.name,self.id))
				
			for atom in self.atomlist:
				f.write(atom.xyzline())

	def writemps(self,filename,header=False):
		d=self.calcDmonopoles()
		with open(filename,"w") as f: 
			if type(header)==str:
				f.write("!{} {} {}\n".format(self.name,self.id,header))
			else:
				f.write("!{} {} Created by Python Script\n".format(self.name,self.id))
			f.write("! N={} Q[e]={:+1.7f} D[e*nm]={:+1.7e} {:+1.7e} {:+1.7e}\n".format(len(self.atomlist),self.calcQ(),d[0]*0.1,d[1]*0.1,d[2]*0.1))
			f.write("Units angstrom\n")
			for atom in self.atomlist:
				f.write(atom.mpsentry())

	def readxyzfile(self,filename):
			noofatoms=None
			with open(filename,"r") as f:
				for line in f.readlines():
					if line[0]=="#":
						continue
					entries=line.split()
					if len(entries)==0:
						continue
					elif len(entries)==1:
						noofatoms=int(entries[0])
					elif len(entries)==4:
						name=entries[0]
						pos=np.array(entries[1:],dtype=float)
						
						self.atomlist.append(atom(name,pos))
			self.calccoG()
			return

	def readmps(self,filename):
		line1=False
		line2=False
		conversion=False
		d=None
		quad=None
		q=None
		r=None
		element=None
		with open(filename,"r") as f:
	
			for line in f.readlines():
				a=line.split()
				if "Units angstrom" in line:
					conversion=1
				elif "Units bohr" in line:
					conversion=0.52917721092
				elif "Rank" in line:
					#print line
					element=a[0]
					rank=int(a[5])
					if conversion!=False:
						r=conversion*np.array(a[1:4],dtype=float) 
					line1=True
				elif len(a)==1 and line1:
					q=float(a[0])
					line2=True
				elif len(a)==3 and line1 and line2:
					d=np.array(a[0:3],dtype=float) 
					line3=True
				elif len(a)==5 and line1 and line2 and line3 and "P" not in line:
					quad=np.array(a[0:],dtype=float) 
					line3=True
				elif "P" in line and line1 and line2:
					p=np.array(a[1:],dtype=float)
					#print p
					ptensor=np.array([[p[0],p[1],p[2]],[p[1],p[3],p[4]],[p[2],p[4],p[5]]])
					line1=False
					line2=False
					line3=False
					at=atom(element,r)
					if quad==None:
						quad=np.zeros(5)
					if d==None:
						d=np.zeros(3)
					at.setmultipoles(q,d,quad,ptensor)
					self.updateatom(at)
		
		self.calccoG()
		
		return
