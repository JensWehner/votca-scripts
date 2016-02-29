from __future__ import division
import numpy as np
import sys   as sys


class Atom(object):
	
	def __init__(self, Z, pos):
		self.Z = Z
		self.pos = pos
		self.VdW = 8 # a.u.
		
	def DistFrom(self, pos):
		return np.dot(self.pos - pos, self.pos - pos)**0.5	


class ScalarField(object):
	def __init__(self, atoms, scalarfield, C0, Cx, Cy, Cz, Nx, Ny, Nz):
		self.atoms = atoms
		self.field = scalarfield
		self.C0 = C0
		self.Cx = Cx
		self.Cy = Cy
		self.Cz = Cz
		self.Nx = Nx
		self.Ny = Ny
		self.Nz = Nz
		
	def write_xyz(self, outfile):
		
		outt = open(outfile, 'w')
		
		slot = 0
		
		for i in range(self.Nx):
			for j in range(self.Ny):
				for k in range(self.Nz):
					xyz = self.C0 + i*self.Cx + j*self.Cy + k*self.Cz
					
					outt.write('%4.7f %4.7f %4.7f %4.7f \n' % (xyz[0], xyz[1], xyz[2], self.field[slot]))	
					
					slot += 1
		
		
		
	def testPos(self, pos):		
		for atom in self.atoms:
			if atom.DistFrom(pos) < atom.VdW:
				return False
		return True
	
	def Restrict_Outside_VdW(self):
		
		Field_Outside_VdW = []
		Outside = []
		Idcs = []
		
		idx = -1
		for i in range(self.Nx):
			for j in range(self.Ny):
				for k in range(self.Nz):
					idx += 1
					pos = self.C0 + i*self.Cx + j*self.Cy + k*self.Cz
					#if np.dot(pos,pos)**0.5 > 10:
					if self.testPos(pos):
						Field_Outside_VdW.append(self.field[idx])
						Outside.append(pos)
						Idcs.append(idx)
					else:
						pass
			PrintProgress(i)
		
		self.field = Field_Outside_VdW
		return Outside, Idcs
	
	def Restrict_Outside_VdW_Idcs(self, idcs):
		
		Field_Outside_VdW = []		
		for i in idcs:
			Field_Outside_VdW.append(self.field[i])
		
		self.field = np.array(Field_Outside_VdW)
			
			
def Printer(data):
	sys.stdout.write("\r"+data.__str__())
	sys.stdout.flush()


def PrintProgress(i):
	progress = 'Voxel x # ' + str(i)
	sys.stdout.write("\r"+progress.__str__())
	sys.stdout.flush()


def ArrayFromCube(infile):	
	
	print "Reading file", infile,
	
	atoms = []
	scalarfield = []
	
	C0 = None
	Cx = None
	Cy = None
	Cz = None
	Nx = None
	Ny = None
	Nz = None
	
	lineCount = 0
	atomCount = 0
	
	intt = open(infile, 'r')
	
	for ln in intt.readlines():
		
		lineCount += 1		
		ln = ln.split()

		# Empty line?
		if ln == []:
			continue		
			
		# Header line?
		elif lineCount <= 2:
			continue		
			
		# Cube origin
		elif lineCount == 3:
			atomCount = int(ln[0])
			C0 = np.array( [float(ln[1]), float(ln[2]), float(ln[3])] )		
			
		# Cube X Y Z
		elif lineCount == 4:
			Nx = int(ln[0])
			Cx = np.array( [float(ln[1]), float(ln[2]), float(ln[3])] )
		elif lineCount == 5:
			Ny = int(ln[0])
			Cy = np.array( [float(ln[1]), float(ln[2]), float(ln[3])] )
		elif lineCount == 6:
			Nz = int(ln[0])
			Cz = np.array( [float(ln[1]), float(ln[2]), float(ln[3])] )
		
		# Atom line
		elif len(ln) == 5:
			Z = int(ln[0])
			pos = np.array( [float(ln[2]), float(ln[3]), float(ln[4])] )
			atoms.append( Atom(Z,pos) )
		
		# Scalar-field line	
		else:
			for item in ln:			
				item = float(item)
				scalarfield.append(item)
	
	scalarfield = np.array(scalarfield)	
	print ":", len(scalarfield), "grid points."
	print "... Atoms               ", len(atoms)
	print "... Voxel numbers       ", Nx, Ny, Nz, " TOTAL ", Nx*Ny*Nz
	print "... Cube origin, axes   ", C0, Cx, Cy, Cz
	
	return ScalarField(atoms, scalarfield, C0, Cx, Cy, Cz, Nx, Ny, Nz) 


field = ArrayFromCube('DCV_0_esp_gdma.cube')
field.write_xyz('esp_0.xyz')






			
		
			
		
		
		
	
	



