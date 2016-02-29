from __pyosshell__ import *


HARTREE_TO_EV 	= 27.211396132
BOHR_TO_A	= 0.529189379
BOHR_TO_NM    	= 0.0529189379


POLARITY      = {}
POLARITY['H'] = 0.496
POLARITY['C'] = 1.334
POLARITY['N'] = 1.073
POLARITY['O'] = 0.837
POLARITY['S'] = 2.926
POLARITY['F'] = 0.44
POLARITY['Al'] = 5.5
POLARITY['Zn'] = 5.96
POLARITY['Cl'] = 1.44


PERIODIC_TABLE 		= {}
PERIODIC_TABLE[1] 	= 'H'
PERIODIC_TABLE[6] 	= 'C'
PERIODIC_TABLE[7] 	= 'N'
PERIODIC_TABLE[8] 	= 'O'
PERIODIC_TABLE[9]  	= 'F'
PERIODIC_TABLE[13]  = 'Al'
PERIODIC_TABLE[16] 	= 'S'
PERIODIC_TABLE[17]	= 'Cl'


class PeriodicTable(object):
	def __init__(self):
		self.dict = {}
	def __getitem__(self, key):
		return self.dict[key]
	def Add(self, **kwargs):
		element = Element(**kwargs)
		self.dict[kwargs['symbol']] = element
		self.dict[kwargs['Z']] = element

class Element(object):
	def __init__(self, **kwargs):
		self.symbol = kwargs['symbol']
		self.Z = kwargs['Z']
		self.mass = kwargs['mass']
		self.kwargs = kwargs
	def __str__(self):
		return self.symbol
	def __repr__(self):
		return self.symbol
	def __getitem__(self, key):
		return self.kwargs[key]

PTABLE = PeriodicTable()
PTABLE.Add(symbol='H',	Z=1,	mass=1.008,			polar=0.496)
PTABLE.Add(symbol='C',	Z=6,	mass=12.01,			polar=1.334)
PTABLE.Add(symbol='N',	Z=7,	mass=14.01,			polar=1.073)
PTABLE.Add(symbol='O',	Z=8,	mass=16.00,			polar=0.837)
PTABLE.Add(symbol='F',	Z=9,	mass=19.00,			polar=0.440)
PTABLE.Add(symbol='Si',	Z=14,	mass=28.09,			polar=4.09)
PTABLE.Add(symbol='S',	Z=16,	mass=32.07,			polar=2.926)
PTABLE.Add(symbol='Zn',	Z=30,	mass=65.39,			polar=5.96)
PTABLE.Add(symbol='Cl',	Z=17,	mass=35.45,			polar=1.44)


# =========================== #
# IMPORT / EXPORT POLAR SITES #
# =========================== #

class PolarSegment(object):
	def __init__(self, mpsfile=None, mps=None, name=None, state=None):
		self.name = name
		self.state = state
		# LOAD POLAR SITES
		self.mps = []
		assert (mps!=None) ^ (mpsfile!=None)
		if mpsfile != None:
			self.mpsfile = mpsfile
			self.mps = mpsfile_to_mps(mpsfile)
		elif mps != None:
			self.mps = mps
		else:
			assert False
		self.has_com = self.has_chrg = self.has_dpl = False
		# COMPUTE PROPERTIES
		self.CalcCom()
		self.CalcChrg()
		self.CalcDpl()
		return
	def CalcCom(self):
		com = np.array([0,0,0])
		for mp in self.mps:
			com = com + mp.xyz
		com = com / len(self.mps)
		self.com = com
		self.has_com = True
		return com
	def CalcChrg(self):
		Q = 0
		for mp in self.mps: Q += mp.qs[0]
		self.has_chrg = True
		self.chrg = Q
		return Q
	def CalcDpl(self, ref=None):
		# Requires positions in Angstrom
		if ref == None:
			assert self.has_com
			ref = self.com
		net_dpl = np.array([0,0,0])
		for mp in self.mps:
			net_dpl = net_dpl + mp.qs[0]*(mp.xyz-ref)/BOHR_TO_A
			if mp.k > 0:
				net_dpl = net_dpl + np.array([mp.qs[2], mp.qs[3], mp.qs[1]]) # order z-x-y
		self.dpl = net_dpl
		self.has_dpl = True
		return net_dpl
	def massless_inertia_tensor(self, ref=None, mp_name_mask=None):
		if ref == None:
			assert self.has_com
			ref = self.com
		R = ref
		I = np.zeros((3,3))
		E = np.identity(3)
		for mp in self.mps:
			if mp_name_mask != None and mp.e[0:1] not in mp_name_mask: continue
			r = mp.xyz
			I = I + np.dot(r-R,r-R)*E - np.outer(r-R,r-R)
		return I
	def orientation(self):
		inertia = self.massless_inertia_tensor()
		w,v = sorted_eigenvalues_vectors(inertia)
		return w,v
	def rotate_by(self, rmat, ref=None):
		if ref == None:
			ref = self.com
			assert self.has_com
		for mp in self.mps:
			mp.xyz = mp.xyz - ref
			mp.xyz = np.dot(rmat, mp.xyz)
			mp.xyz = mp.xyz + ref
		return
	def translate_by(self, shift):
		for mp in self.mps:
			mp.xyz = mp.xyz + shift
		return
	def append_to_xyzfile(self, ofs):
		for mp in self.mps:
			mp.write_xyz_line(ofs)
		return
	def scale_polarizabilities(self, factor):
		for mp in self.mps:
			for i in range(len(mp.p)):
				mp.p[i] = mp.p[i]*factor
		return
	def write_mps(self, mpsfile):
		mps_to_mpsfile(self.mps, mpsfile)
		return

class MP(object):	
	def __init__(self, e = 'X', p = [0.0], k = 0, xyz = np.array([0,0,0]), qs = []):
		self.e 		= e
		if qs == []:
			self.qs 	= []
		else:
			self.qs		= qs
		self.p 		= p
		self.k		= int(k)
		self.xyz 	= xyz
	def add_q(self,q):
		self.qs.append(q)
	def set_qs(self,qs):
		self.qs = qs
	def set_p(self,p):
		self.p = p
	def get_q(self):
		return self.qs[0]
	def import_from_mp(self,mp):
		self.e = mp.e
		self.qs = mp.qs[:]
		self.k = mp.k
		self.p = mp.p[:]
		self.xyz = mp.xyz
	def write_mps_line(self, outt, iso = False, write_polar=True):
		outt.write('%1s %+4.7f %+4.7f %+4.7f Rank %1d \n' % (self.e,self.xyz[0],self.xyz[1],self.xyz[2],self.k))
		outt.write('      %+4.7f \n' % self.qs[0])
		if self.k > 0:
			outt.write('      %+4.7f %+4.7f %+4.7f\n' % (self.qs[1],self.qs[2],self.qs[3]))
		if self.k > 1:
			outt.write('      %+4.7f %+4.7f %+4.7f %+4.7f %+4.7f\n' % (self.qs[4],self.qs[5],self.qs[6],self.qs[7],self.qs[8]))
		if write_polar:
			if len(self.p) == 1:
				if iso:
					outt.write('    P %4.7f \n' % (self.p[0]))
				else:
					outt.write('    P %4.7f 0.0 0.0 %4.7f 0.0 %4.7f \n' % (self.p[0],self.p[0],self.p[0]))			
			else:
				outt.write('    P ')
				for p_i in self.p:
					outt.write('%+4.7f ' % p_i)
				outt.write(' \n')
	def write_xyz_line(self, outt):
		outt.write('%1s %+4.7f %+4.7f %+4.7f\n' % (self.e,self.xyz[0],self.xyz[1],self.xyz[2]))
	def p_tensor_eigensystem(self):	
		p_tensor = np.array( [ [self.p[0],self.p[1],self.p[2]],
	                           [self.p[1],self.p[3],self.p[4]],
	                           [self.p[2],self.p[4],self.p[5]] ])
		w,v = la.eig(p_tensor)
		return w,v
	def get_p_tensor(self):
		p_tensor = np.array( [ [self.p[0],self.p[1],self.p[2]],
	                           [self.p[1],self.p[3],self.p[4]],
	                           [self.p[2],self.p[4],self.p[5]] ])
		return p_tensor
	def rotate(self, rotmat, center=np.array([0,0,0])):
		# Not well tested (only for Q20 so far)
		self.xyz = self.xyz - center
		self.xyz = np.dot(rotmat, self.xyz)
		if self.k > 0:
			d = np.array([self.qs[2], self.qs[3], self.qs[1]]) # order z-x-y
			d = np.dot(rotmat, d)
		if self.k > 1:
			# Convert to cartesian moments
			Qzz =      self.qs[4]
			Qxx = -0.5*self.qs[4] + 0.5*3**0.5*self.qs[7]
			Qyy = -0.5*self.qs[4] - 0.5*3**0.5*self.qs[7]
			Qxy =  0.5*3**0.5*self.qs[8]
			Qxz =  0.5*3**0.5*self.qs[5]
			Qyz =  0.5*3**0.5*self.qs[6]
			Q = np.array([[Qxx,Qxy,Qxz],[Qxy,Qyy,Qyz],[Qxz,Qyz,Qzz]])			   
			# Rotate        
			rotmat_t = rotmat.transpose()  
			QR = np.dot(Q, rotmat)
			RQR = np.dot(rotmat_t, QR)
			# Convert back
			self.qs[4] =               RQR[2][2] # Q20
			self.qs[5] = 2. / 3.**0.5 * RQR[0][2] # Q21c
			self.qs[6] = 2. / 3.**0.5 * RQR[1][2] # Q21s
			self.qs[7] = 1. / 3.**0.5 * (RQR[0][0] - RQR[1][1]) # Q22c
			self.qs[8] = 2. / 3.**0.5 * RQR[0][1] # Q22s		
		self.xyz = self.xyz + center
		return
		
		

def assign_iso_polarizabilities(mps, iso_p_scale=1.):
	global POLARITY
	for mp in mps:
		iso_p = POLARITY[mp.e]
		if mp.e != 'H': iso_p *= iso_p_scale
		mp.set_p([iso_p])
	return

def e_xyz_to_mps(e,xyz,scale = 1.0):
	global POLARITY	
	
	mps = []
	assert len(e) == len(xyz)	
	for i in range(len(e)):		
		mps.append( MP(e[i],[scale*POLARITY[e[i]]],0,xyz[i],qs=[0]) )
	return mps		

def atm_rsd_xyz_to_gro(atm, rsd, xyz, gro = 'out.gro'):
	assert False


def mps_from_mpsfile(mpsfile, iso_p_scale=1.):
	return mpsfile_to_mps(mpsfile, iso_p_scale)


def mpsfile_to_mps(mpsfile, iso_p_scale=1.):
	
	intt = open(mpsfile,'r')
	
	mps = []
	
	xyz_conv = 1.
	count = -1
	for ln in intt.readlines():
		
		sp = ln.split()
		if sp == [] or sp[0] == '!' or sp[0][0] == '!': continue
		
		if sp[0] == 'Units':
			if sp[1] == 'angstrom':
				xyz_conv = 1.
			elif sp[1] == 'bohr':				
				global BOHR_TO_A
				xyz_conv = BOHR_TO_A
				print sp[0], sp[1], xyz_conv
			elif sp[1] == 'nanometer':
				global NM_TO_A
				xyz_conv = 10.
			else:
				print sp[1]
				assert(False) # Invalid unit in .mps file
				
		elif len(sp) == 6:
			e = sp[0]
			k = sp[5]
			x = float(sp[1])*xyz_conv
			y = float(sp[2])*xyz_conv
			z = float(sp[3])*xyz_conv
			xyz = np.array([x,y,z])
			
			count += 1
			mps.append(MP(e = e, k = k, xyz = xyz))
			
		elif sp[0] == 'P':
		
			scale = iso_p_scale
			if mps[count].e == 'H':
				scale = 1.
		
			if len(sp) == 2:
				p = [float(sp[1])*scale]
				
			else:
				assert len(sp) == 7
				p = [ float(sp[i])*scale for i in range(1,7) ]
			assert len(mps) == count + 1
			mps[count].set_p(p)
		
		else:
			for q in [ float(s) for s in sp ]:
				assert len(mps) == count + 1
				mps[count].add_q(q)
				
	return mps
	
	
def mps_to_mpsfile(mps, outfile, units = 'angstrom', iso = False, write_polar=True):
	Q = 0.0
	D = np.array([0,0,0])
	for mp in mps:
		Q += mp.qs[0]
		D = D + mp.xyz*mp.qs[0]/BOHR_TO_A
		if mp.k > 0:
			D = D + np.array([mp.qs[2], mp.qs[3], mp.qs[1]])
	outt = open(outfile,'w')
	outt.write('! GENERATED BY __QMSHELL__::mps_to_mpsfile\n')
	outt.write('! N=%d Q=%+1.7f D(approx.)=%+1.7f %+1.7f %+1.7f\n' % (len(mps), Q, D[0], D[1], D[2]))
	outt.write('Units %1s\n' % units)
	if units != 'angstrom': assert False
	for mp in mps:
		mp.write_mps_line(outt,iso,write_polar)
	outt.close()
	return
	
def mps_to_xyzfile(mps, outfile):
	outt = open(outfile,'w')
	outt.write('%1d\n' % len(mps))
	outt.write('GENERATED BY __QMSHELL__::mps_to_xyzfile\n')
	for mp in mps:
		mp.write_xyz_line(outt)
	return
		


# ========================= #
# ANALYSIS                  #
# ========================= #

def calculate_q_d_Q(mps,ref = [0,0,0],auto = True,d_int2ext = 1./0.20822678,q_int2ext = 1./0.20822678):
	
	# Reference frame for DMA
	ref = np.array(ref)	
	com = np.array([0,0,0])
	magn_sum = 0
	N = 0
	for mp in mps:
		com = com + mp.xyz
		magn_sum += mp.get_q()
		N += 1
	com = com / N
	if auto:
		ref = com
	#print "Q00", magn_sum
	#print "COM", com
	#print "REF", ref
	
	# Unit conversion
	D_CONV = d_int2ext
	Q_CONV = q_int2ext
	
	q   = 0	
	
	dx 	= 0
	dy 	= 0
	dz  = 0	
	
	qxx = 0
	qxy = 0
	qxz = 0
	qyy = 0
	qyz = 0
	qzz = 0	
	
	for mp in mps:
		mp.xyz = mp.xyz - ref
	
	
	for mp in mps:
	
		q   += mp.get_q()
		
		dx	+= mp.get_q() * mp.xyz[0]
		dy  += mp.get_q() * mp.xyz[1]
		dz  += mp.get_q() * mp.xyz[2]
	
		qxx += mp.get_q() * ( 1.5*mp.xyz[0]*mp.xyz[0] - 0.5*np.dot(mp.xyz,mp.xyz) )
		qxy += mp.get_q() * ( 1.5*mp.xyz[0]*mp.xyz[1] )
		qxz += mp.get_q() * ( 1.5*mp.xyz[0]*mp.xyz[2] )
		
		qyy += mp.get_q() * ( 1.5*mp.xyz[1]*mp.xyz[1] - 0.5*np.dot(mp.xyz,mp.xyz) )
		qyz += mp.get_q() * ( 1.5*mp.xyz[1]*mp.xyz[2] )
		
		qzz += mp.get_q() * ( 1.5*mp.xyz[2]*mp.xyz[2] - 0.5*np.dot(mp.xyz,mp.xyz) )


	for mp in mps:
		mp.xyz = mp.xyz + ref
	
	print "L = 0"
	print "%+4.7f" % (q)
	print "L = 1"
	print "%+4.7f %+4.7f %+4.7f" % (dx*D_CONV,dy*D_CONV,dz*D_CONV)
	print "L = 2"
	print "%+4.7f %+4.7f %+4.7f" % (qxx*Q_CONV,qxy*Q_CONV,qxz*Q_CONV)
	print "%+4.7f %+4.7f %+4.7f" % (qxy*Q_CONV,qyy*Q_CONV,qyz*Q_CONV)
	print "%+4.7f %+4.7f %+4.7f" % (qxz*Q_CONV,qyz*Q_CONV,qzz*Q_CONV)
	
	#print "TRACE", qxx+qyy+qzz	
	#print "MAGNI", (qxx**2+qyy**2+qzz**2+qxy**2+qxz**2+qyz**2)**0.5
	
	d = np.array( [ dx, dy, dz ] )
	Q = np.array( [ [qxx,qxy,qxz],
	                [qxy,qyy,qyz],
	                [qxz,qyz,qzz] ] )
	w,v = la.eig(Q)
	print w
	print v
	return q, d, Q
	
	

# ========================= #
# INTERACTION WITH GAUSSIAN #
# ========================= #

def mps_from_log(logfile,mpsfile = None,p1_scale = 1.,unit = 'angstrom',reorder = [], optimised_xyz = True, return_rank = False):
	
	
	intt = open(logfile,'r')
	
	# Retrieve coordinates
	
	xyz = []
	elem = []
	q = []
	d = []
	
	e, xyz = e_xyz_from_log(logfile, optimised_xyz)
	
	
	# Retrieve charges
	
	rank = -1
	
	
	while True:
		ln = intt.readline()
		if 'Fitting point charges' in ln:
			if 'point dipoles' in ln:
				rank = 1
				intt.readline() # The dipole moment will be constrained ...
			else:
				rank = 0
			
			intt.readline() # Charges from ESP fit, RMS=   0.01869 RRMS=   0.95283:
			intt.readline() # Charge=   0.00000 Dipole=     0.4115    -1.2194    -1.5867 Tot=     2.0430
			intt.readline() #              1
			
			if rank == 1:
				intt.readline() # Charges Point Dipoles (au)
			break
	
	while True:
		ln = intt.readline().split()
		
		if rank == 0:		
			if len(ln) == 3:
				e = ln[1]
				q_e = float(ln[2])
				elem.append(e)
				q.append(q_e)
			else:
				break
		
		elif rank == 1:
			if len(ln) == 6:
				e = ln[1]
				q_e = float(ln[2])
				dx = float(ln[3])
				dy = float(ln[4])
				dz = float(ln[5])
				d_e = np.array([dx,dy,dz])
				elem.append(e)
				q.append(q_e)
				d.append(d_e)
			else:
				break
		else:
			print rank
			assert False # Rank?		
	
	intt.close()
	
	# Sanity checks
	
	try:
		assert len(xyz) == len(elem) == len(q)
	except AssertionError:
		print len(xyz),len(elem),len(q)
		assert False
		
	if rank == 0: assert len(d) == 0
	elif rank == 1: assert len(d) == len(xyz)
	
	
	# Establish order
	
	if len(reorder) > 0:
		
		order = [ int(i) for i in reorder ]	
		
		try:	
			assert len(xyz) == len(order)
		except AssertionError:
			print len(xyz),len(order)
			assert False
			
			
		for i in range(1,len(xyz)+1):
			assert order.count(i) == 1
		
	else:
		#print "Not reordering atoms for .mps output"
		order = [ i for i in range(1,len(xyz)+1) ]
		
	order_dict = {}
	for i in range(len(order)):
		# IDX(MP) : IDX(QM)
		order_dict[order[i]] = i
	
	# Assemble into .mps file
	
	if mpsfile != None:
		outt = open(mpsfile,'w')
	
		outt.write('! CREATED BY __QMSHELL__PY FROM LOGFILE %1s \n' % logfile)
		outt.write('! P1_SCALE %1.1f \n' % p1_scale)
		outt.write('Units %1s \n' % unit)
	
		for i in range(len(xyz)):
	
			idx = order_dict[i+1]
		
			assert order.count(idx+1) == 1
		
			x = xyz[idx][0]
			y = xyz[idx][1]
			z = xyz[idx][2]
			p = POLARITY[elem[idx]] * p1_scale
			
			if rank == 0:
				outt.write('%2s %+4.7f %+4.7f %+4.7f Rank 0 \n' % (elem[idx],x,y,z))
				outt.write('      %+4.7f\n' % q[idx])
				outt.write('    P %+4.7f\n' % p)
			elif rank == 1:
				outt.write('%2s %+4.7f %+4.7f %+4.7f Rank 1 \n' % (elem[idx],x,y,z))
				outt.write('      %+4.7f\n' % q[idx])
				# ATTENTION: Order of dipole components is z,x,y
				outt.write('      %+4.7f %+4.7f %+4.7f\n' % (d[idx][2],d[idx][0],d[idx][1]))
				outt.write('    P %+4.7f\n' % p)
	
		outt.close()
	
	mps = []
	for i in range(len(elem)):
		if rank == 0:
			mps.append(MP(elem[i], [POLARITY[elem[i]]*p1_scale], 0, xyz[i], [q[i]]))
		elif rank == 1:
			mps.append(MP(elem[i], [POLARITY[elem[i]]*p1_scale], 0, xyz[i], [q[i],d[i][2],d[i][0],d[i][1]]))
	if return_rank:
		return mps, rank
	else:
		return mps
	

def normal_termination(logfile):
	
	tail = command_as_string('tail -n 1 %1s' % logfile)
	if 'Normal termination' in tail:
		return True
	else:
		return False	


def e_xyz_from_xyz(xyzfile):
	e = []
	xyz = []
	intt = open(xyzfile,'r')
	N = intt.readline().split()[0]
	N = int(N)
	intt.readline()
	for i in range(N):
		ln = intt.readline().split()
		e.append(ln[0])
		x = float(ln[1])
		y = float(ln[2])
		z = float(ln[3])
		xyz.append(np.array([x,y,z]))
	intt.close()
	return e, xyz
	

def e_xyz_to_xyz(e,xyz,outfile):
	assert len(e) == len(xyz)
	outt = open(outfile,'w')
	outt.write('%1d\n\n' % len(e))	
	for i in range(len(e)):
		outt.write('%2s %+1.7f %+1.7f %+1.7f\n' % (e[i],xyz[i][0], xyz[i][1], xyz[i][2]))
	outt.close()


def e_xyz_from_com(comfile):
	e = []
	xyz = []
	intt = open(comfile,'r')
	while True:
		ln = intt.readline()
		sp = ln.split()
		if sp == []:
			continue
		if sp[0][0] == '%':
			continue
		if sp[0][0:2] == '#p':
			break
		
	intt.readline()
	intt.readline()
	intt.readline()
	intt.readline()	
	while True:
		ln = intt.readline()
		ln = ln.split()
		if len(ln) != 4 or not ln[0] in 'HCNOFS':
			break
		
		e.append(ln[0])
		x = float(ln[1])
		y = float(ln[2])
		z = float(ln[3])
		xyz.append(np.array([x,y,z]))	
	return e, xyz
		

def polarizability_from_log(logfile, do_assert=True):

	global BOHR_TO_A
	BOHR3_TO_A3 = BOHR_TO_A**3

	if do_assert:
		assert normal_termination(logfile)
	
	intt = open(logfile,'r')
	
	while True:
		ln = intt.readline()
		if 'SCF Polarizability' in ln:
			break
		else:
			pass
	
	tmp = intt.readline()
	
	tmp = intt.readline()
	tmp = tmp.replace('D','e')
	pxx = float(tmp.split()[1]) * BOHR3_TO_A3
	
	tmp = intt.readline()
	tmp = tmp.replace('D','e')	
	pxy = float(tmp.split()[1]) * BOHR3_TO_A3
	pyy = float(tmp.split()[2]) * BOHR3_TO_A3
	
	tmp = intt.readline()
	tmp = tmp.replace('D','e')
	pxz = float(tmp.split()[1]) * BOHR3_TO_A3
	pyz = float(tmp.split()[2]) * BOHR3_TO_A3
	pzz = float(tmp.split()[3]) * BOHR3_TO_A3
	
	return [ pxx, pxy, pxz, pyy, pyz, pzz ]	
	

def command_as_table(command):
	exe(command+' > command_as_string.temp')
	intt = open('command_as_string.temp')
	out = []
	for ln in intt.readlines():
		out.append(ln)
	intt.close()
	exe('rm command_as_string.temp')
	return out	



def e_xyz_from_log(logfile, optimised_xyz = True, soft_criterion = False, xyz_trigger = None):
	
	try: 
		intt = open(logfile,'r')
		intt.close()
	except IOError:
		print "Logfile %1s does not exist. Return." % logfile
		raise IOError
		return
	
	trig1 = command_as_table('cat %1s | grep "Z-Matrix orientation:"' % logfile)
	trig2 = command_as_table('cat %1s | grep "Standard orientation:"' % logfile)
	trig3 = command_as_table('cat %1s | grep "Input orientation:"'    % logfile)
	
	if len(trig1) > 0:
		xyz_trigger = 'Z-Matrix orientation:'
	elif len(trig2) > 0:
		xyz_trigger = 'Standard orientation:'
	elif len(trig3) > 0:
		xyz_trigger = 'Input orientation:'
	else:
		assert False # No xyz trigger established
	print "Chose trigger '%s'" % xyz_trigger
	
	
	finished = normal_termination(logfile)
	if not finished:
		print "WARNING: Error termination in %1s. Defaulting to input coordinates." % logfile	
		optimised_xyz = False
		
	e   = []
	xyz = []
	
	intt = open(logfile,'r')

	if optimised_xyz:
		# Opt job?
		while True:
			ln = intt.readline()
			if '#' in ln and not 'opt' in ln:
				optimised_xyz = False
				print "WARNING: No optimised coordinates available in %1s. Defaulting to input coordinates." % logfile
				break
			
			elif '#' in ln and 'opt' in ln:
				print "LOGFILE %1s: %1s" % (logfile, ln[:-1])
				break
		
		if optimised_xyz:
			# Read until converged...
			while True:
				ln = intt.readline()
				
				if 'Converged?' in ln:
					conv1 = intt.readline().split()[-1]
					conv2 = intt.readline().split()[-1]
					conv3 = intt.readline().split()[-1]
					conv4 = intt.readline().split()[-1]
					
					if not soft_criterion:
						if conv1 == 'YES' and conv2 == 'YES' and conv3 == 'YES' and conv4 == 'YES':
							break
					elif soft_criterion:
						if conv1 == 'YES' and conv2 == 'YES' and conv4 == 'YES':
							break
				
				if 'termination' in ln:
					if not soft_criterion:
						print "WARNING: Optimization not fully converged in %1s. Defaulting to soft criterion." % logfile
						e, xyz = e_xyz_from_log(logfile, optimised_xyz, True)
						return e, xyz
					else:
						print "WARNING: Optimization not converged in %1s. Defaulting to input coordinates." % logfile
						optimised_xyz = False
						intt.close()
						intt = open(logfile,'r')
			
			if optimised_xyz:
				while True:
					ln = intt.readline()
					if xyz_trigger == None:
						if 'Standard orientation:' in ln or 'Z-Matrix orientation:' in ln:
							break
					else:
						if xyz_trigger in ln:
							break
				
				intt.readline()
				ln = intt.readline()
				assert 'Center' in ln
				assert 'Atomic' in ln
				intt.readline()
				intt.readline()
				
				global PERIODIC_TABLE
				
				while True:
					ln = intt.readline().split()
					if '----' in ln[0]:
						break
					
					Z = int(ln[1])
					
					e.append(PERIODIC_TABLE[Z])					
					x = float(ln[3])
					y = float(ln[4])
					z = float(ln[5])
					xyz.append(np.array([x,y,z]))
					
			
			
	if not optimised_xyz:
		# Find beginning
		while True:
			ln = intt.readline()
			if 'Charge' in ln and 'Multiplicity' in ln:
				break		
		# Read positions
		while True:
			ln = intt.readline()
			sp1 = ln.split()
			sp2 = ln.split(',')
			if len(sp1) == 4:
				e.append(sp1[0])
				x = float(sp1[1])
				y = float(sp1[2])
				z = float(sp1[3])
				xyz.append(np.array([x,y,z]))
			elif len(sp2) == 5:
				# Comma separated (geom=allcheck)
				e.append(sp2[0])
				x = float(sp2[2])
				y = float(sp2[3])
				z = float(sp2[4])
				xyz.append(np.array([x,y,z]))		
			else:
				break
	
	return e, xyz


def energy_from_log(logfile, unit = 'eV'):
	
	tail = command_as_string('cat %1s | grep "SCF Done" | tail -n 1' % logfile)
	tail = tail.split()
	energy_au    = float(tail[4])
	energy_eV    = energy_au*27.211396132
	energy_kJmol = energy_au*2625.49962
    
	if unit == 'eV':
		return energy_eV
	elif unit == 'au':
		return energy_au
	elif unit == 'kJmol':
		return energy_kJmol
	else:
		print "No such unit: %1s." % unit
		assert False
    


# ========================= #
# CTRL FILE CREATOR         #
# ========================= #

def write_com_file(comfile, e, xyz, proc = 8, mem = 8, cmd = '#p opt b3lyp/6-31g nosymm', chrg_mult = '0 1'):
	tag = comfile[:-4]
	outt = open('%1s.com' % tag, 'w')
	outt.write('%1snprocshared=%1d\n' % ('%',proc))
	outt.write('%1smem=%1dGB\n' % ('%',mem))
	outt.write('%1schk=%1s.chk\n' % ('%',tag))
	outt.write('%1s\n' % cmd)
	outt.write('\n')
	outt.write('%1s\n' % tag.upper())
	outt.write('\n')
	outt.write('%1s\n' % chrg_mult)	
	for i in range(len(e)):
		outt.write('%2s %+4.7f %+4.7f %+4.7f\n' % (e[i],xyz[i][0],xyz[i][1],xyz[i][2]))
	outt.write('\n')
	outt.close()
	return

def write_qg09_file(description, command, outfile='qg09.sh'):
	if description[0:1] in '0123456789': description = 'Q' + description
	outt = open(outfile,'w')
	outt.write('''#!/bin/tcsh
#
#$ -pe PE_8 8
#$ -o out
#$ -e err
#$ -cwd
#$ -j y
#$ -m eab
#$ -M poelking@mpip-mainz.mpg.de
#$ -N {tag:s}

set workdir=`pwd`
echo "Workdir is $workdir"

source /sw/linux/intel/composerxe-2011.0.084/bin/compilervars.csh intel64
source ~/g09_init

# create local scratch
if ( ! -d /usr/scratch/poelking ) then
    mkdir /usr/scratch/poelking
endif

set jno=0
while ( -d /usr/scratch/poelking/job_$jno ) 
    set jno = `expr $jno + 1`
end
set jobdir="/usr/scratch/poelking/job_$jno"
mkdir $jobdir
rm -rf $jobdir/*
mkdir $jobdir/temp

echo "Jobdir is $jobdir"

# copy stuff to local scratch
rsync -ar $workdir/* $jobdir --exclude "*.out" --exclude "*.chk" --exclude "*.log"

cd $jobdir

{cmd:s}

cd ..
#sync back
rsync -ar $jobdir/* $workdir --exclude "*.out" --exclude "temp"

#clean
rm -rf $jobdir
'''.format(tag=description.upper(), cmd=command))
	
	outt.close()
	#auto_replace('qg09.sh', ['DESCRIPTION','COMMAND'], [description,command])
	return outfile
	
	
def write_qg03_file(description, command, outfile='qg03.sh', queue='PE_8', procs=8, source='~/g03_init'):
	if description[0:1] in '0123456789': description = 'Q' + description
	outt = open(outfile,'w')
	outt.write('''#!/bin/tcsh
#
#$ -pe {queue:s} {procs:d}
#$ -o out
#$ -e err
#$ -cwd
#$ -j y
#$ -m eab
#$ -M poelking@mpip-mainz.mpg.de
#$ -N {tag:s}

set workdir=`pwd`
echo "Workdir is $workdir"

source /sw/linux/intel/composerxe-2011.0.084/bin/compilervars.csh intel64
source {source:s}

# create local scratch
if ( ! -d /usr/scratch/poelking ) then
    mkdir /usr/scratch/poelking
endif

set jno=0
while ( -d /usr/scratch/poelking/job_$jno ) 
    set jno = `expr $jno + 1`
end
set jobdir="/usr/scratch/poelking/job_$jno"
mkdir $jobdir
rm -rf $jobdir/*
mkdir $jobdir/temp

echo "Jobdir is $jobdir"

# copy stuff to local scratch
rsync -ar $workdir/* $jobdir --exclude "*.out" --exclude "*.log"

cd $jobdir

{cmd:s}

cd ..
#sync back
rsync -ar $jobdir/* $workdir --exclude "*.out" --exclude "temp"

#clean
rm -rf $jobdir
'''.format(tag=description.upper(), source=source, cmd=command, queue=queue, procs=procs))
	
	outt.close()
	#auto_replace('qg03.sh', ['DESCRIPTION','COMMAND'], [description,command])
	return outfile




def move_cube_file(cubefile_in, cubefile_out, vec_angstrom=np.array([0,0,0])):
	ifs = open(cubefile_in, 'r')
	ofs = open(cubefile_out, 'w')
	# Write comment lines
	ofs.write(ifs.readline())
	ofs.write(ifs.readline())
	# Number of atoms & origin, shift the latter
	origin_ln = ifs.readline()
	sp = origin_ln.split()
	N = int(sp[0])
	ox = float(sp[1])
	oy = float(sp[2])
	oz = float(sp[3])	
	sx = vec_angstrom[0]/BOHR_TO_A
	sy = vec_angstrom[1]/BOHR_TO_A
	sz = vec_angstrom[2]/BOHR_TO_A	
	ofs.write('{0:4d} {1:+1.7f} {2:+1.7f} {3:+1.7f}\n'.format(N, ox+sx, oy+sy, oz+sz))
	# Three lines for grid
	ofs.write(ifs.readline())
	ofs.write(ifs.readline())
	ofs.write(ifs.readline())
	# Atom lines
	for i in range(N):
		atom_ln = ifs.readline()
		sp = atom_ln.split()
		v = int(sp[0])
		q = float(sp[1])
		x = float(sp[2]) + sx
		y = float(sp[3]) + sy
		z = float(sp[4]) + sz
		ofs.write('{0:4d} {1:+1.7f} {2:+1.7f} {3:+1.7f} {4:+1.7f}\n'.format(v, q, x, y, z))
	# Copy the rest
	for ln in ifs.readlines():
		ofs.write(ln)
	ofs.close()
	ifs.close()
	return
	
def write_cube_header(mps, cubefile='mps.cube', res_bohr=0.15, overhead_bohr=10):
	# Calculate dimensions
	xs = []
	ys = []
	zs = []
	for mp in mps:
		x = mp.xyz[0]
		y = mp.xyz[1]
		z = mp.xyz[2]
		xs.append(x)
		ys.append(y)
		zs.append(z)
	xmin = min(xs)
	xmax = max(xs)
	ymin = min(ys)
	ymax = max(ys)
	zmin = min(zs)
	zmax = max(zs)
	
	dx = xmax-xmin
	dy = ymax-ymin
	dz = zmax-zmin	
	
	dx /= BOHR_TO_A
	dy /= BOHR_TO_A
	dz /= BOHR_TO_A
	
	dx += overhead_bohr
	dy += overhead_bohr
	dz += overhead_bohr
	
	# Grid setup
	nx = int(math.ceil(dx/res_bohr))
	ny = int(math.ceil(dy/res_bohr))
	nz = int(math.ceil(dz/res_bohr))
	
	ox = -0.5*dx
	oy = -0.5*dy
	oz = -0.5*dz
	
	# Write cubefile
	ofs = open(cubefile, 'w')
	ofs.write(' GENERATED BY __QMSHELL__::<write_cube_header>\n')
	ofs.write(' Electrostatic potential, SCF density, ...\n')	
	
	ofs.write('{0:4d} {1:+1.7f} {2:+1.7f} {3:+1.7f}\n'.format(len(mps), ox, oy, oz))
	ofs.write('{0:4d} {1:+1.7f} {2:+1.7f} {3:+1.7f}\n'.format(nx, res_bohr, 0, 0))
	ofs.write('{0:4d} {1:+1.7f} {2:+1.7f} {3:+1.7f}\n'.format(ny, 0, res_bohr, 0))
	ofs.write('{0:4d} {1:+1.7f} {2:+1.7f} {3:+1.7f}\n'.format(nz, 0, 0, res_bohr))
	
	ofs.close()
	
	
	
	
	
	
	
	
	
	


