from __future__ import division
import numpy as np


infile = 'SiteEnergies_IND0.dat'
outfile = 'sphere_de.dat'


class SegData(object):

	def __init__(self, ID, name, en, ec, itern, iterc, sphere, pos):
		
		self.id = ID
		self.name = name
		self.pos = pos
				
		self.en = en
		self.ec = ec
		self.de = ec - en
		
		self.itern = itern
		self.iterc = iterc		
		self.sphere = sphere	
		
		self.out_dict = {}



class DOS_Data(object):
	
	def __init__(self, infile):
		
		self.Pool = []
		self.Import(infile)
		
	def Import(self, infile):		
		
		intt = open(infile, 'r')
		
		for ln in intt.readlines():
			
			ln = ln.split()
			if ln == []:
				continue
			
			ID = int(ln[0])
			name = ln[1]
			
			en = float(ln[3])
			ec = float(ln[5])
			itern = float(ln[7])
			iterc = float(ln[9])
			sphere = int(ln[11])
			
			x = float(ln[12])
			y = float(ln[13])
			z = float(ln[14])
			pos = np.array([x,y,z])
			
			self.Pool.append(SegData(ID, name, en, ec, itern, iterc, sphere, pos))
	
	def sphere_de(self, outfile):
		
		outt = open(outfile, 'w')
		
		for data in self.Pool:
			outt.write('%4d %4.7f \n' % (data.sphere, data.de))
		
		outt.close()
			
			
dos_data = DOS_Data(infile)
dos_data.sphere_de(outfile)





 
