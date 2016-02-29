#! /usr/bin/env python
import os
import numpy as np


mpsfile = 'dcv4t.mps'
outfile = mpsfile[:-4]+'_reordered.mps'
reorder = 'reorder_dcv4t.dat'
units   = 'bohr'





class MP(object):	
	def __init__(self, e = 'X', p = '0.0', k = 0, xyz = np.array([0,0,0]), qs = [0]):
		self.e 		= e
		self.qs 	= []
		self.p 		= p
		self.k		= int(k)
		self.xyz 	= xyz
	def add_q(self,q):
		self.qs.append(q)
	def set_p(self,p):
		self.p = p
	def import_from_mp(self,mp):
		self.e = mp.e
		self.qs = mp.qs
		self.k = mp.k
		self.p = mp.p
		self.xyz = mp.xyz
	def write_mps_line(self, outt):
		outt.write('%1s %4.7f %4.7f %4.7f Rank %1d \n' % (self.e,self.xyz[0],self.xyz[1],self.xyz[2],self.k))
		outt.write('      %4.7f \n' % self.qs[0])
		if self.k > 0:
			outt.write('      %4.7f %4.7f %4.7f\n' % (self.qs[1],self.qs[2],self.qs[3]))
		if self.k > 1:
			outt.write('      %4.7f %4.7f %4.7f %4.7f %4.7f\n' % (self.qs[4],self.qs[5],self.qs[6],self.qs[7],self.qs[8]))
		outt.write('    P %4.7f \n' % self.p)
			

def mpsfile_to_mps(mpsfile):
	
	intt = open(mpsfile,'r')
	
	mps = []
	
	for ln in intt.readlines():
		
		sp = ln.split()
		if ln == [] or sp[0] == '!' or sp[0][0] == '!': continue
		
		if sp[0] == 'Units': continue
		
		elif len(sp) == 6:
			e = sp[0]
			k = sp[5]
			x = float(sp[1])
			y = float(sp[2])
			z = float(sp[3])
			xyz = np.array([x,y,z])
			
			mps.append(MP(e = e, k = k, xyz = xyz))
			
		elif sp[0] == 'P':
			p = float(sp[1])
			mps[-1].set_p(p)
		
		else:
			for q in [ float(s) for s in sp ]:
				mps[-1].add_q(q)
				
	return mps
	

def reorder_mps(mps, reorderfile = 'nofile'):
	
	if reorderfile == 'nofile':
		reorder = [ i+1 for i in range(len(mps)) ]
	else:
		reorder = []
		intt = open(reorderfile,'r')
		for ln in intt.readlines():
			ln = ln.split()
			if ln == []:
				continue
			reorder.append(int(ln[0]))
	
	
	mps_re = []
	for i in range(len(mps)):
		mps_re.append(MP())
	
	if len(reorder) > 0:
		
		order = [ int(i) for i in reorder ]	
		
		try:	
			assert len(mps) == len(order)
		except AssertionError:
			assert False # Reorder table does not match .mps-file
			
			
		for i in range(1,len(mps)+1):
			assert order.count(i) == 1 # Some index in reorder occurs multiple times
		
	else:
		print "Not reordering atoms for .mps output"
		order = [ i for i in range(1,len(xyz)+1) ]
		
	order_dict = {}
	for i in range(len(order)):
		# IDX(MP) : IDX(QM)
		order_dict[order[i]] = i
		
	for i in range(len(mps_re)):
		
		idx = order_dict[i+1]		
		mps_re[i].import_from_mp(mps[idx])
	
	return mps_re
	


				
mps = mpsfile_to_mps(mpsfile)
mps = reorder_mps(mps,reorder)

outt = open(outfile,'w')
outt.write('! REORDERED FROM %1s\n' % mpsfile)
outt.write('!\n')
outt.write('Units %1s\n' % units)
for mp in mps:
	mp.write_mps_line(outt)
outt.close()


	



