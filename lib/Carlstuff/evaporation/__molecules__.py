from 	__future__ 		import division
from 	__proptions__ 	import *

import 	numpy 			as np
import  sys             as sys


class Population(object):
	
	def __init__(self, grofile=None, topfile=None, verbose = True, pop=None, pop_struct=None):
		
		if pop != None:
			assert grofile == None and topfile == None
			self.import_from_pop(pop)
			return
		
		self.t	        = 0.000
		self.box_float  = None
		self.box_str    = ' 0.000 0.000 0.000 '
		
		self.grofile    = grofile
		self.topfile	= topfile
		
		if topfile != None:
			self.pop_struct = struct_from_topfile(topfile) # [ [mol, nrMol, nrAtoms], ... ]
		else:
			if pop_struct == None:
				raise AssertionError('<Population> constructor: topfile = pop_struct = None')
			self.pop_struct = pop_struct
		self.mols 	    = []
		
		self.a			= None
		self.b			= None
		self.c			= None
		
		if verbose:
			print "Read + load %1s using %1s: " % (grofile, topfile),
		self.parse_gro(grofile, self.pop_struct)
		if verbose:	
			print "%1d molecules with %1d atoms at t = %1.1f" % (len(self.mols),self.atom_count(),self.t)
	
	def import_from_pop(self,pop):
		# Low-level copy constructor
		self.t = pop.t
		self.box_float = pop.box_float
		self.box_str = pop.box_str
		self.a = pop.a
		self.b = pop.b
		self.c = pop.c
		self.grofile = pop.grofile
		self.topfile = pop.topfile
		self.mols = []
		for mol in pop.mols:
			newMol = Molecule(mol.Id,mol.name)
			self.mols.append(newMol)
			for atm in mol.atoms:
				newAtm = Atom('')			
				newAtm.fragId 	= atm.fragId
				newAtm.fragName	= atm.fragName
				newAtm.name		= atm.name
				newAtm.Id		= atm.Id
				newAtm.pos		= atm.pos
				newAtm.vel		= atm.vel			
				newMol.atoms.append(newAtm)
		self.update_top()
		return			
	
	def parse_gro(self, grofile, mol_nrMol_nrAtoms):	
		intt = open(grofile,'r')
		
		# Title, number of atoms
		title 		= intt.readline()
		time		= -1	
		nr_atoms 	= int(intt.readline().split()[0])
		
		# Extract time
		if 't=' in title:
			ln = title.split()
			for i in range(len(ln)):
				if ln[i] == 't=':
					self.t = float(ln[i+1])
					break
				else: pass
		
		# Check for self-consistency
		nr_sections = len(mol_nrMol_nrAtoms)		
		count = 0
		for i in range(nr_sections):
			section = mol_nrMol_nrAtoms[i] # [ ('C60',1,60), ('DCV4T',1,42) ]
			mol_name = section[0]
			nr_mols_sect = section[1]
			nr_atoms_mol = section[2]
			count += nr_mols_sect * nr_atoms_mol
		try:
			assert count == nr_atoms
		except AssertionError:
			print "%1s: Number of atoms in title does not match assumed structure." % grofile
			assert False
		
		# Process atoms
		doPrintWarn_notConsecutive = False
		id_counter = 0
		
		for i in range(nr_sections):
			section = mol_nrMol_nrAtoms[i]
			mol_name = section[0]
			nr_mols_sect = section[1]
			nr_atoms_mol = section[2]
			
			for j in range(nr_mols_sect):
			
				new_mol = self.create_mol(mol_name)
				
				for k in range(nr_atoms_mol):
					id_counter += 1
					groln = intt.readline()
					new_atom = new_mol.create_atom(groln)
					if new_atom.Id != id_counter % 100000:
						doPrintWarn_notConsecutive = True
					new_atom.Id = id_counter
		
		if doPrintWarn_notConsecutive:
			print "NOTE Atoms not numbered consecutively in %s." % grofile
		
		# Retrieve box information
		self.box_str = intt.readline()
		self.box_float = [ float(_str) for _str in self.box_str.split() ]
		
		if len(self.box_float) < 9:
			assert len(self.box_float) == 3
			self.box_float = [ self.box_float[0], self.box_float[1], self.box_float[2],
			                   0.0, 0.0, 0.0, 0.0, 0.0, 0.0 ]
		
		self.a = np.array([self.box_float[0],self.box_float[3],self.box_float[4]])
		self.b = np.array([self.box_float[5],self.box_float[1],self.box_float[6]])
		self.c = np.array([self.box_float[7],self.box_float[8],self.box_float[2]])
		
		intt.close()
	
	def write_top(self, path = './', overwrite = False, topfile = None, auto_header=False, joint_forcefield=''):
		
		if topfile == None:
			topfile = self.topfile
		
		if path == './' and topfile == self.topfile and os.path.isfile(path+topfile):
			topfile = topfile + '__new'
		
		outt = open(path+topfile,'w')
		
		if not auto_header:
			intt = open(self.topfile,'r')
			for ln in intt.readlines():
				if not 'molecules' in ln:
					outt.write(ln)
				else:
					break
			intt.close()
		else:
			system_name = ''
			unique_mols = []
			for item in self.pop_struct:
				molname = item[0]
				if not molname in unique_mols:
					unique_mols.append(molname)
			for name in unique_mols:
				system_name += name
				if name != unique_mols[-1]:
					system_name += '-'
			outt.write('; FORCEFIELD\n')
			if joint_forcefield != '':
				outt.write('#include "./FORCEFIELD/%s"\n' % joint_forcefield)
			else:
				outt.write('#include "./FORCEFIELD/default.itp"\n')
				for mol in unique_mols:
					outt.write('#include "./FORCEFIELD/%s_forcefield.itp"\n' % mol)
			outt.write('\n')
			outt.write('; MOLECULES\n')
			for mol in unique_mols:
				outt.write('#include "./FORCEFIELD/%s.itp"\n' % mol)
			outt.write('\n')
			outt.write('[ system ]\n')
			outt.write('%s\n' % system_name)
			outt.write('\n')
				
		
		outt.write('[ molecules ]\n')
		for item in self.pop_struct:
			outt.write('%-10s %5d\n' % (item[0],item[1]))
		outt.close()
		
		if overwrite:
			os.system('mv %1s %1s' % (path+topfile, self.topfile))
		
		return
		
	def write_gro(self, path = './', grofile = None):
		
		if grofile == None:
			grofile = self.grofile
		if path == './' and grofile == None:
			grofile = grofile + '__new'
		
		outt = open(path+grofile,'w')
		
		outt.write('CREATED FROM POPULATION t= %4.7f\n' % (self.t))
		outt.write('%5d\n' % (self.atom_count()))
		for mol in self.mols:
			mol.append_to_gro(outt)

		outt.write('%2.5f %2.5f %2.5f %2.5f %2.5f %2.5f %2.5f %2.5f %2.5f\n' \
		   % (self.a[0], self.b[1], self.c[2], self.a[1], self.a[2], self.b[0], self.b[2], self.c[0], self.c[1]))
		
		outt.close()
		return
	
	def atom_count(self):		
		count = 0
		for mol in self.mols:
			count += mol.atom_count()
		return count
	
	def mol_count(self):
		return len(self.mols)
		
	def get_all_mol(self, molname):
		mols = []
		for mol in self.mols:
			if mol.name == molname:
				mols.append(mol)
		return mols
	
	def get_atom_ids(self, molname):
		ids = []
		for mol in self.mols:
			if mol.name == molname:
				for atom in mol.atoms:
					ids.append(atom.Id)
		return ids
		
	def create_mol(self,name):		
		self.mols.append(Molecule(len(self.mols)+1,name))
		return self.mols[-1]
		
	def print_info(self, verbose = False):
		
		for mol in self.mols:
			mol.print_info()
			if verbose:
				for atom in mol.atoms:
					atom.print_info()

	def box_vectors(self):
		
		while len(self.box_float) < 9:
			self.box_float.append(0.000)
		
		box_x = np.array([self.box_float[0],self.box_float[3],self.box_float[4]])
		box_y = np.array([self.box_float[5],self.box_float[1],self.box_float[6]])
		box_z = np.array([self.box_float[7],self.box_float[8],self.box_float[2]])
		
		return box_x, box_y, box_z
		
	def reciprocal_box_vectors(self):
		V = self.box_volume()
		self.ra = 2.*np.pi/V * np.cross(self.b, self.c)
		self.rb = 2.*np.pi/V * np.cross(self.c, self.a)
		self.rc = 2.*np.pi/V * np.cross(self.a, self.b)
		return self.ra, self.rb, self.rc
	
	def append_pop(self, pop):
		# User: call ::update_top afterwards
		for mol in pop.mols:
			self.mols.append(mol)
		self.pop_struct += pop.pop_struct
		return
	
	def append_mol(self, mol):
		
		off_id = self.atom_count()
		
		for atom in mol.atoms:
			atom.Id += off_id
		
		mol.Id = len(self.mols)+1
		self.mols.append(mol)
		
		if self.pop_struct == []:
			self.pop_struct.append( [mol.name, 1, len(mol.atoms)] )
		elif mol.name == self.pop_struct[-1][0]:
			self.pop_struct[-1][1] += 1
		else:
			self.pop_struct.append( [mol.name, 1, len(mol.atoms)] )
		
		#self.mols[-1].write_gro('inserted.gro')
		
	def remove_mol(self, mol, check_if_contained=False):
		# User: call ::update_top afterwards
		if check_if_contained:
			contained = mol in self.mols
			if not contained:
				print "No such molecule in system:", mol.Id, mol.name
				return
		self.mols.remove(mol)
		return
	
	def remove_all(self):
		self.mols = []
		self.update_top()
		return
	
	def update_top(self):
		
		self.pop_struct = []
		if self.mols == []:
			return
			
		self.pop_struct.append( [self.mols[0].name,0,len(self.mols[0].atoms)] )
		
		molCounter = 0
		frgCounter = 0
		atmCounter = 0
		for mol in self.mols:
			molCounter += 1
			mol.Id = molCounter
			# Update IDs
			for frg in mol.frags:
				frgCounter += 1
				frg.Id = frgCounter
			for atm in mol.atoms:
				atmCounter += 1
				atm.Id = atmCounter
			# Update top structure
			if self.pop_struct[-1][0] == mol.name:
				self.pop_struct[-1][1] += 1
			else:
				self.pop_struct.append( [mol.name,1,len(mol.atoms)] )
		return
	
	def fragment(self):
		for mol in self.mols:
			mol.fragment()
		return
	
	def make_dict(self):
		for mol in self.mols:
			mol.make_dict()
		return		
		
	def r_pbc(self, r1, r2):	
		r_tp = r2 - r1
		r_dp = r_tp - self.c*round(r_tp[2]/self.c[2])
		r_sp = r_dp - self.b*round(r_dp[1]/self.b[1])
		r_12 = r_sp - self.a*round(r_sp[0]/self.a[0])
		return r_12
	
	def center(self, c=np.array([0,0,0]), use_pbc=True, spec='mols'):
		if spec == 'mols':
			for mol in self.mols:
				com = mol.com()
				dr_dir = com - c
				if use_pbc:
					dr_pbc = self.r_pbc(c,com)
				else:
					dr_pbc = dr_dir
				shift = dr_pbc - dr_dir
				mol.shift(shift)
		elif spec == 'atms':
			for mol in self.mols:
				for atom in mol.atoms:
					com = atom.pos
					dr_dir = com - c
					if use_pbc:
						dr_pbc = self.r_pbc(c,com)
					else:
						dr_pbc = dr_dir
					shift = dr_pbc - dr_dir
					atom.pos = atom.pos + shift
		else:
			raise AssertionError('Invalid spec argument')
		return
	
	def unfold(self):
		for mol in self.mols:
			ref = mol.atoms[0].pos
			for atom in mol.atoms:
				dr_dir = ref - atom.pos
				dr = self.r_pbc(atom.pos, ref)
				atom.pos = atom.pos + dr_dir - dr
		return
	
	def shift(self, vec):
		for mol in self.mols:
			mol.shift(vec)
		return
		
	def rotate_by(self, rmat, ref=None, rot_box_as_matrix=False, fix_box=True, rot_box=True):
		# Transform molecules
		for mol in self.mols:
			mol.rotate_by(rmat, ref)
		# Transform box
		if rot_box and rot_box_as_matrix:
			B = np.array([ self.a, self.b, self.c ])
			R = rmat
			Rt = R.transpose()		
			BRt = np.dot(B, Rt)
			RBRt = np.dot(R, BRt)		
			self.a = RBRt[0]
			self.b = RBRt[1]
			self.c = RBRt[2]
		elif rot_box:
			self.a = np.dot(rmat, self.a)
			self.b = np.dot(rmat, self.b)
			self.c = np.dot(rmat, self.c)
		else:
			pass
		
		if fix_box:
			X = np.array([1,0,0])
			Y = np.array([0,1,0])
			Z = np.array([0,0,1])
			xa = abs(np.dot(self.a, X))
			xb = abs(np.dot(self.b, X))
			xc = abs(np.dot(self.c, X))
			ya = abs(np.dot(self.a, Y))
			yb = abs(np.dot(self.b, Y))
			yc = abs(np.dot(self.c, Y))
			za = abs(np.dot(self.a, Z))
			zb = abs(np.dot(self.b, Z))
			zc = abs(np.dot(self.c, Z))
			
			in_box = [self.a, self.b, self.c]
			out_box = []
			in_idcs = [0,1,2]
			out_idcs = []
			xs = [xa,xb,xc]
			xmax = max(xs)
			xidx = xs.index(xmax)
			in_idcs.remove(xidx)
			out_idcs.append(xidx)
			out_box.append(in_box[xidx])
			
			ys = [ya,yb,yc]
			ymax = max(ys)
			yidx = ys.index(ymax)
			if not yidx in in_idcs:
				ymax = max(ys)
				raise RuntimeError("Could not fix simulation box (x<>y)")
			in_idcs.remove(yidx)
			out_idcs.append(yidx)
			out_box.append(in_box[yidx])
			
			zs = [za,zb,zc]
			zmax = max(zs)
			zidx = zs.index(zmax)
			if not zidx in in_idcs:
				raise RuntimeError("Could not fix simulation box (x<>y<>z)")			
			in_idcs.remove(zidx)
			out_idcs.append(zidx)
			out_box.append(in_box[zidx])
			
			self.a = out_box[0]
			self.b = out_box[1]
			self.c = out_box[2]
			
			if self.a[0] < 0.: self.a = - self.a
			if self.b[1] < 0.: self.b = - self.b
			if self.c[2] < 0.: self.c = - self.c
		
		return
		
	def fix_box(self):
		X = np.array([1,0,0])
		Y = np.array([0,1,0])
		Z = np.array([0,0,1])
		xa = abs(np.dot(self.a, X))
		xb = abs(np.dot(self.b, X))
		xc = abs(np.dot(self.c, X))
		ya = abs(np.dot(self.a, Y))
		yb = abs(np.dot(self.b, Y))
		yc = abs(np.dot(self.c, Y))
		za = abs(np.dot(self.a, Z))
		zb = abs(np.dot(self.b, Z))
		zc = abs(np.dot(self.c, Z))
		
		in_box = [self.a, self.b, self.c]
		out_box = []
		in_idcs = [0,1,2]
		out_idcs = []
		xs = [xa,xb,xc]
		xmax = max(xs)
		xidx = xs.index(xmax)
		in_idcs.remove(xidx)
		out_idcs.append(xidx)
		out_box.append(in_box[xidx])
		
		ys = [ya,yb,yc]
		ymax = max(ys)
		yidx = ys.index(ymax)
		if not yidx in in_idcs:
			ymax = max(ys)
			raise RuntimeError("Could not fix simulation box (x<>y)")
		in_idcs.remove(yidx)
		out_idcs.append(yidx)
		out_box.append(in_box[yidx])
		
		zs = [za,zb,zc]
		zmax = max(zs)
		zidx = zs.index(zmax)
		if not zidx in in_idcs:
			raise RuntimeError("Could not fix simulation box (x<>y<>z)")			
		in_idcs.remove(zidx)
		out_idcs.append(zidx)
		out_box.append(in_box[zidx])
		
		self.a = out_box[0]
		self.b = out_box[1]
		self.c = out_box[2]
		
		if self.a[0] < 0.: self.a = - self.a
		if self.b[1] < 0.: self.b = - self.b
		if self.c[2] < 0.: self.c = - self.c
		return
	
	def get_dimensions(self, mode='atom'):
		p0 = self.mols[0].atoms[0].pos
		if mode == 'mol': p0 = self.mols[0].com()
		x_min = p0[0]; x_max = p0[0]
		y_min = p0[1]; y_max = p0[1]
		z_min = p0[2]; z_max = p0[2]
		for mol in self.mols:
			if mode == 'mol': com = mol.com()
			for atom in mol.atoms:
				p0 = atom.pos
				if mode == 'mol': p0 = com
				x = p0[0]; y = p0[1]; z = p0[2]
				if x < x_min: x_min = x
				elif x > x_max: x_max = x
				if y < y_min: y_min = y
				elif y > y_max: y_max = y
				if z < z_min: z_min = z
				elif z > z_max: z_max = z
		r_min = np.array([x_min,y_min,z_min])
		r_max = np.array([x_max,y_max,z_max])
		return r_min, r_max
	
	def com(self):
		com = np.array([0,0,0])
		for mol in self.mols:
			for atom in mol.atoms:
				com = com + atom.pos
		com = com / self.atom_count()
		return com
		
	def box_volume(self):
		return np.dot(self.a, np.cross(self.b,self.c))

class Molecule(object):
	
	def __init__(self, Id=None, name=None, clone=None):
		if Id != None and name != None:
			self.Id	   = Id
			self.name  = name
			self.frags = []
			self.frag_dict = {}
			self.atoms = []
		else:
			self.Id = None
			self.name = None
			self.frags = []
			self.frag_dict = {}
			self.atoms = []
			
		if clone != None:
			self.import_from(clone)
	
	def import_from(self, other):
		self.Id = other.Id
		self.name = other.name
		self.atoms = []
		self.frags = []
		self.frag_dict = {}
		for atom in other.atoms:
			self.atoms.append(Atom(''))
			self.atoms[-1].import_from(atom)
		if other.frags != []:
			self.fragment()
			self.make_dict()
		return
		
	def create_atom(self,groln,offset=0):		
		self.atoms.append(Atom(groln,offset))
		return self.atoms[-1]
		
	def create_fragment(self, fragId, fragName):
		self.frags.append(Frag(fragId,fragName))
	
	def append_atom(self, atom):
		self.atoms.append(atom)
		return
	
	def fragment(self):
		prev_frag_id = self.atoms[0].fragId - 1
		this_frag_id = self.atoms[0].fragId
		for atom in self.atoms:
			this_frag_id = atom.fragId
			if prev_frag_id != this_frag_id:
				self.create_fragment(atom.fragId,atom.fragName)
				self.frag_dict[atom.fragName] = self.frags[-1]
			prev_frag_id = this_frag_id
			self.frags[-1].add_atom(atom)
		return	
	
	def make_dict(self):
		for frag in self.frags:
			frag.make_dict()
		return
	
	def atom_count(self):
		return len(self.atoms)
	
	def import_from(self, mol):
		self.Id		= mol.Id		
		self.name	= mol.name
		self.frags	= []
		
		for atom in mol.atoms:			
			new_atom = Atom('')
			new_atom.import_from(atom)			
			self.atoms.append(new_atom)
	
	def print_info(self):
		print "Id %-5d %-15s -> No. atoms = %5d" % (self.Id, self.name, len(self.atoms))
		
	def com(self):
		com = np.array([0,0,0])
		for atom in self.atoms:
			com = com + atom.pos
		com = com / len(self.atoms)
		return com
		
	def com_vel(self):
		ms = { 'H' : 1, 'C' : 12, 'N' : 14, 'O' : 16, 'S' : 35 }
		com_vel = np.array([0,0,0])
		M = 0.0
		for atom in self.atoms:
			try:
				m = ms[atom.name[0:1]]
			except KeyError:
				print "WARNING Undefined mass for '%s'. Using default m=12u." % (atom.name)
				m = 12
			com_vel = com_vel + m * atom.vel
			M += m
		com_vel = com_vel / M
		return com_vel
	
	def get_dimensions(self):
		p0 = self.atoms[0].pos
		x_min = p0[0]; x_max = p0[0]
		y_min = p0[1]; y_max = p0[1]
		z_min = p0[2]; z_max = p0[2]
		for atom in mol.atoms:
			p0 = atom.pos
			x = p0[0]; y = p0[1]; z = p0[2]
			if x < x_min: x_min = x
			elif x > x_max: x_max = x
			if y < y_min: y_min = y
			elif y > y_max: y_max = y
			if z < z_min: z_min = z
			elif z > z_max: z_max = z
		r_min = np.array([x_min,y_min,z_min])
		r_max = np.array([x_max,y_max,z_max])
		return r_min, r_max
	
	def mass(self):		
		ms = { 'H' : 1, 'C' : 12, 'N' : 14, 'O' : 16, 'S' : 35, 'Ir' : 192 }		
		m = 0.0
		for atom in self.atoms:
			try:
				m += ms[atom.name[0:1]]		
			except KeyError:
				print "WARNING No mass for atom '%s'. Using default 12." % (atom.name)
				m += 12
		return m		
		
	def shift(self,shift):
		for atom in self.atoms:
			atom.pos = atom.pos + shift
		return
	
	def boost(self,dv):
		for atom in self.atoms:
			atom.vel = atom.vel + dv
		return
		
	def write_gro(self,grofile, offset_id = 0, box = None):
		outt = open(grofile,'w')
		outt.write('%1s\n' % self.name)
		outt.write('%3d\n' % len(self.atoms))
		for atom in self.atoms:
			atom.write_gro_ln(outt, offset_id)	
		if box == None:	
			outt.write(' 0.000 0.000 0.000 \n')
		else:
			for x in box:
				outt.write(' %1.5f' % x)
			outt.write('\n')
		outt.close()

	def write_com_gro_ln(self,outt,spec = 'ATM'):
		outt.write('%5d%3s%7s%5d' % (self.Id, self.name, spec, self.Id % 100000))		
		com = self.com()		
		for i in range(3):
			x = com[i]
			if x*x >= 100.000:
				outt.write(' %+1.3f' % x)
			else:
				outt.write('  %+1.3f' % x)				 
		outt.write('\n')
		return

	def append_to_gro(self,outt,offset_id = 0):
		for atom in self.atoms:
			atom.write_gro_ln(outt, offset_id)
		return
	
	def massless_inertia_tensor(self, ref = None, atom_name_mask=None):
		if ref == None:
			ref = self.com()
		R = ref
		I = np.zeros((3,3))
		E = np.identity(3)
		for atom in self.atoms:
			if atom_name_mask != None and atom.name[0:1] not in atom_name_mask: continue
			r = atom.pos
			I = I + np.dot(r-R,r-R)*E - np.outer(r-R,r-R)
		return I
	
	def rotate_by(self, R, ref=None):
		if ref == None:
			ref = self.com()
		for atom in self.atoms:
			atom.pos = atom.pos - ref
		for atom in self.atoms:
			atom.pos = np.dot(R, atom.pos)
		for atom in self.atoms:
			atom.pos = atom.pos + ref
		return
		
	def translate_by(self, T):
		for atom in self.atoms:
			atom.pos = atom.pos + T
		return
		
	def get_dimensions(self):
		p0 = self.atoms[0].pos
		x_min = p0[0]; x_max = p0[0]
		y_min = p0[1]; y_max = p0[1]
		z_min = p0[2]; z_max = p0[2]
		for atom in self.atoms:
			p0 = atom.pos
			x = p0[0]; y = p0[1]; z = p0[2]
			if x < x_min: x_min = x
			elif x > x_max: x_max = x
			if y < y_min: y_min = y
			elif y > y_max: y_max = y
			if z < z_min: z_min = z
			elif z > z_max: z_max = z
		r_min = np.array([x_min,y_min,z_min])
		r_max = np.array([x_max,y_max,z_max])
		return r_min, r_max
		
			


class Frag(object):
	
	def __init__(self, fragId, fragName):		
		self.name = fragName
		self.Id = fragId
		self.atoms = []
		
	def atom_count(self):
		return len(self.atoms)
		
	def add_atom(self, atom):
		self.atoms.append(atom)
		
	def make_dict(self):		
		self.atom_dict = { }
		for atom in self.atoms:
			self.atom_dict[atom.name] = atom
		return

	def com(self, skip = ''):
		com = np.array([0,0,0])
		substract = 0
		for atom in self.atoms:
			if atom.name == skip:
				substract += 1
			else:
				com = com + atom.pos
		com = com / (len(self.atoms)-substract)
		return com


class Atom(object):
	
	def __init__(self, ln, offset=0):	
	
		if ln == '':
			self.fragId 	= -1
			self.fragName	= -1
			self.name		= 'noname'
			self.Id			= -1
			self.pos		= np.array([0,0,0])
			self.vel		= np.array([0,0,0])
		else:			
			self.fragId		   	= int( ln[0:5] )
			self.fragName	 	= ln[5:8].strip()
			self.name	 		= ln[8:15].strip()
			self.Id			   	= int(ln[15:20]) - offset

			x  = float( ln[20:28] )
			y  = float( ln[28:36] )
			z  = float( ln[36:44] )		
			self.pos = np.array( [x,y,z] )
			self.vel = np.array( [0,0,0] )
		
			vx = ln[44:52].strip()
			vy = ln[52:60].strip()
			vz = ln[60:68].strip()
		
			if vx != '' and vy != '' and vz != '':
				self.vel = np.array([float(vx),float(vy),float(vz)])		
	
	def import_from(self,atom):
		
		self.fragId		= atom.fragId
		self.fragName	= atom.fragName
		self.name		= atom.name
		self.Id			= atom.Id
		self.pos		= atom.pos
		self.vel		= atom.vel
	
	def write_gro_ln(self,outt,offset_id = 0, fragName = ''):	
		Id = self.Id + offset_id
		if fragName == '':
			fragName = self.fragName
		outt.write('%5d%3s%7s%5d' % (self.fragId, fragName, self.name, Id % 100000))
		for i in range(3):
			x = self.pos[i]
			if ('%+1.3f' % x) == '+10.000' or ('%+1.3f' % x) == '-10.000':
				outt.write(' %+1.3f' % x)
			elif x >= 9.9999 or x <= -9.9999:
				outt.write(' %+1.3f' % x)
			else:
				outt.write('  %+1.3f' % x)
		if self.vel != None:	
			for i in range(3):
				v = float(self.vel[i])
				if ('%+1.3f' % v) == '+10.0000' or ('%+1.3f' % v) == '-10.0000':
					outt.write('%+1.3f' % v)
				elif v >= 9.99999 or x <= -9.99999: 
					outt.write('%+1.4f' % v)
				else:
					outt.write(' %+1.4f' % v) 
		outt.write('\n')
		
		
	def print_info(self):
		print "    %5d %5s %5d %5s" % (self.Id, self.name, self.fragId, self.fragName)
		
		
		



def SingleMoleculeFromGro(grofile, offset=0):	
	molecule = Molecule(0,grofile[:-4])	
	intt = open(grofile,'r')
	header = intt.readline()
	size = int(intt.readline().split()[0])	
	for i in range(size):		
		groln = intt.readline()
		molecule.create_atom(groln, offset)	
	box = np.array([ float(x) for x in intt.readline().split() ])
	return molecule, box


def ibin(x): return sum([ord(x[j])<<(24-j*8) for j in range(4)])


def last_from_xtc(trjfile = 'traj.xtc',  outfile = 'last.gro', 
                   topfile = 'topol.tpr', index = '',
                   propt = '-pbc mol -ur tric', echo = '0'):

	f = open(trjfile)
	
	# Tag: magic number and number of atoms
	tag = f.read(8)  
	
	# Size of frame in bytes                 
	n = 92 + ibin(f.read(84)[-4:])       

	# This should contain a complete frame
	f.seek(-5*n/4, 2)       
	
	# Read in remaining part       
	frame = f.read()   
	
	# Find the tag               
	frame = frame[frame.index(tag):]  

	# Open the output file
	open('traj_last_frame_temp.xtc',"w").write(frame)
	
	if index.strip() != '':
		index = '-n '+index
	
	os.system('echo %1s | trjconv -f traj_last_frame_temp.xtc -o %1s -s %1s %1s %1s' % (echo, outfile, topfile, index, propt))	
	os.system('rm traj_last_frame_temp.xtc')

def StackPop(pop, Na = 1, Nb = 1, Nc = 1, Sa = 1, Sb = 1, Sc = 1):
	
	stencil = Population(pop=pop)
	
	a = pop.a
	b = pop.b
	c = pop.c
	
	sys.stdout.write('Stacking %dx%dx%d\n' % (Na,Nb,Nc))
	
	if Na==0 or Nb==0 or Nc==0:
		print '... Zero population'
		pop.remove_all()
		pop.update_top()
		return pop
	
	sys.stdout.flush()
	stackCount = 0
	for i in range(Na):
		for j in range(Nb):
			for k in range(Nc):
				stackCount += 1
				sys.stdout.write('\r... na x nb x nc = %2d x %2d x %2d ' % (i+1,j+1,k+1))				
				#if stackCount % 40 == 0:
					#sys.stdout.write('\n')
				sys.stdout.flush()
				if i == j == k == 0: continue
				pbc_shift = (i)*a*Sa + (j)*b*Sb + (k)*c*Sc
				pop_pbc = Population(pop=stencil)
				for mol in pop_pbc.mols:
					mol.shift(pbc_shift)
				pop.append_pop(pop_pbc)
	print ""
	pop.a = Na*pop.a
	pop.b = Nb*pop.b
	pop.c = Nc*pop.c
		
	pop.update_top()
	return pop
				

COVRAD_TABLE_NM = {}
COVRAD_TABLE_NM['H'] = 0.031
COVRAD_TABLE_NM['C'] = 0.076
COVRAD_TABLE_NM['N'] = 0.071
COVRAD_TABLE_NM['O'] = 0.066
COVRAD_TABLE_NM['Se'] = 0.120
COVRAD_TABLE_NM['S'] = 0.105
COVRAD_TABLE_NM['Zn'] = 0.122


