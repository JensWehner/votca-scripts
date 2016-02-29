from	__future__		import division
from 	__pyosshell__	import *
from 	__proptions__	import *
from	__mdpassist__	import *
from 	__molecules__ 	import *



class System(object):
	
	def __init__(self, grofile, topfile, ndxfile, ctrlfile, histfile, cmdlineopt, verbose=True):			
		
		# ==========================================================
		# Set Population -> Set Options -> Set History -> Evaporator
		# ==========================================================
		
		self.grofile 	= grofile
		self.topfile 	= topfile
		self.ndxfile	= ndxfile
		self.ctrlfile 	= ctrlfile
		self.histfile 	= histfile
		
		# System components
		self.pop 		= Population(grofile,topfile,verbose)
		self.opt 		= dict_from_bracket_file(ctrlfile)
		self.cmdlineopt = cmdlineopt
		self.hst 		= file_to_table(histfile)
		self.tag 		= self.opt['SYSTEM']['tag'][0]
		self.evp 		= None
		
		# Time-keeping
		self.set_time(0.0,0.0)
		
		# System dimensions
		self.a     		= None
		self.b	   		= None
		self.n     		= None
		self.a_min 		= None
		self.a_max 		= None
		self.b_min 		= None
		self.b_max 		= None
		self.n_min 		= None
		self.n_max 		= None
		
		# Injection point
		self.in_pt 		= None
		self.in_dir 	= None
		self.xy_inj_pts = []
		
		# Density profile
		self.hst_n_d 	= None
		
		# System groups
		self.fze_idcs 	= []
		self.sub_idcs 	= []
		self.thf_idcs 	= []
		self.iph_idcs 	= []
	
	def set_time(self,t_in,t_run):
	
		self.pop.t				= t_in
		self.opt['MDP']['T'] 	= [t_run]
		return
	
	
	def set_dimensions(self):	
		
		# ==========================================================
		# () set_dimensions -> get_injection_point -> evaporate_mol
		# ==========================================================
		
		self.a = normVector(np.array(self.opt['SUBSTRATE']['a']))
		self.b = normVector(np.array(self.opt['SUBSTRATE']['b']))
		self.n = normVector(np.array(self.opt['SUBSTRATE']['n']))
		
		a_dist = []
		b_dist = []
		n_dist = []
		
		for mol in self.pop.mols:
			for atom in mol.atoms:
				a_dist.append( np.dot(atom.pos,self.a) )
				b_dist.append( np.dot(atom.pos,self.b) )
				n_dist.append( np.dot(atom.pos,self.n) )
		
		self.a_min = min(a_dist)
		self.a_max = max(a_dist)
		self.b_min = min(b_dist)
		self.b_max = max(b_dist)
		self.n_min = min(n_dist)
		self.n_max = max(n_dist)
		return
	
	def get_height_profile(self, outfile = 'system_height_profile.dat'):
		
		x_res = self.opt['SYSTEM']['res_x'][0]
		y_res = self.opt['SYSTEM']['res_y'][0]
		
		# Convert triclinic to cartesian frame for analysis
		self.a = normVector(np.array(self.opt['SUBSTRATE']['a']))
		self.b = normVector(np.array(self.opt['SUBSTRATE']['b']))
		self.n = normVector(np.array(self.opt['SUBSTRATE']['n']))
		
		skewed_to_cart = np.array( [ [self.a[0], self.b[0], self.n[0]],
		                             [self.a[1], self.b[1], self.n[1]],
		                             [self.a[2], self.b[2], self.n[2]] ] )
		                             
		cart_to_skewed = np.linalg.inv(skewed_to_cart)
		
		
		pos_in_skewed  = []
		height_in_skewed = []
		for mol in self.pop.mols:
			for atom in mol.atoms:			
				skewed = np.dot(cart_to_skewed,atom.pos)				
				pos_in_skewed.append( np.array([skewed[0],skewed[1]]) )	
				height_in_skewed.append( skewed[2] )
				#atom.pos = np.dot(cart_to_skewed,atom.pos) # Messing up
				
		base_h = min(height_in_skewed)
		# XY Height profile
		i_j_xy, i_j_n, i_j_h, ij_xy, ij_n, RES_X, RES_Y = \
		     list2hist_2d_height(pos_in_skewed, height_in_skewed, x_res, y_res, PROC_H = calc_avg, RETURN_2D = '2d1d')
		
		x_s = []
		y_s = []
		h_s = []
		for i in range(len(i_j_xy)):
			for j in range(len(i_j_xy[i])):
				x_s.append(i_j_xy[i][j][0])
				y_s.append(i_j_xy[i][j][1])
				h_s.append(i_j_h[i][j]-base_h)
		xm = min(x_s); xM = max(x_s)
		ym = min(y_s); yM = max(y_s)
		hm = min(h_s); hM = max(h_s)
		
		outt = open(outfile,'w')
		outt.write('# X %2.3f %2.3f Y %2.3f %2.3f H %2.3f %2.3f\n' % (xm,xM,ym,yM,hm,hM))
		for i in range(len(i_j_xy)):
			for j in range(len(i_j_xy[i])):
				outt.write('%4.7f %4.7f %4.7f %4d\n' % (i_j_xy[i][j][0],i_j_xy[i][j][1], i_j_h[i][j]-base_h, i_j_n[i][j]))
			outt.write('\n')
		outt.close()
		return
		
	
	def xy_density(self):
		# Figure out substrate molecules	
		self.auto_group()

		x_res = self.opt['SYSTEM']['res_x'][0]
		y_res = self.opt['SYSTEM']['res_y'][0]
		
		# Convert triclinic to cartesian frame for analysis
		self.a = normVector(np.array(self.opt['SUBSTRATE']['a']))
		self.b = normVector(np.array(self.opt['SUBSTRATE']['b']))
		self.n = normVector(np.array(self.opt['SUBSTRATE']['n']))
		
		skewed_to_cart = np.array( [ [self.a[0], self.b[0], self.n[0]],
		                             [self.a[1], self.b[1], self.n[1]],
		                             [self.a[2], self.b[2], self.n[2]] ] )
		                             
		cart_to_skewed = np.linalg.inv(skewed_to_cart)
		
		
		pos_in_skewed  = []
		for mol in self.pop.mols:
			if mol.Id in self.mol_sub_idcs: continue
			for atom in mol.atoms:			
				skewed = np.dot(cart_to_skewed,atom.pos)				
				pos_in_skewed.append( np.array([skewed[0],skewed[1]]) )	
				#atom.pos = np.dot(cart_to_skewed,atom.pos) # Messing up
		
		# XY Height profile
		xy_2d, z_2d, xy, z, x_res, y_res = list2hist_2d(pos_in_skewed, x_res, y_res, RETURN_2D = '2d1d')	
		
		print "=== XY Height profile === dx %1.3f dy %1.3f" % (x_res, y_res)
		if len(z) < 101:
			for x in range(len(z_2d)):
				for y in range(len(z_2d[x])):
					print "%4d " % (z_2d[x][y]),
				print ""
		else:
			print "-> see  system_height_profile.dat"
			
		outt = open('system_height_profile.dat','w')		
		outt.write('# MIN MAX %4.7f %4.7f\n' % (min(z),max(z)))
		for ix in range(len(xy_2d)):
			for iy in range(len(xy_2d[ix])):
				outt.write('%+4.7f %+4.7f %+4.7f\n' % (xy_2d[ix][iy][0],xy_2d[ix][iy][1],z_2d[ix][iy]))
			outt.write('\n')
		outt.close() 
		
		# XY insertion probability
		h_min = min(z)
		h_max = max(z)
		
		if h_min == h_max:
			print "h_min == h_max => Homogeneous insertion."
			z = [ 1 for h in z ]
		else:
			print "Linear insertion weighting in place."
			z = [ 1 - (h - h_min) / (h_max - h_min) for h in z ]
		Z = sum(z)
		p = [ h / sum(z) for h in z ]
		
		# Cumulative probability
		cum_p = []
		for i in range(len(p)):
			cum_p_i = 0.0
			for j in range(i,len(p)):
				cum_p_i += p[j]
			cum_p.append(cum_p_i)
		cum_p.append(0)
				
		# TRJCONV -f in -o out -pbc atom -ur tric before anything happens
		# !!! NEED TO CORRECT FOR REAL RESOLUTION IN X AND Y  !!!
		# (list2hist_2d adapts this to fit an integer number of bins into [min,max])
		
		self.xy_inj_pts = []
		
		print "Performing binary search to generate injection points ..."
		for i in range(100):
			rnd = np.random.uniform()			
			idx = binary_search_idx(rnd,cum_p)
			
			ab = xy[idx]
			a = (ab[0] - 0.5*x_res) + np.random.uniform() * (x_res)
			b = (ab[1] - 0.5*y_res) + np.random.uniform() * (y_res)
			
			ab = np.array([a,b,0])
			ab_cart = np.dot(skewed_to_cart,ab)	
			self.xy_inj_pts.append(ab_cart)
		
		#outt = open('inj_pts.xyz','w')
		#outt.write('10000\n\n')
		#for pt in inj_ab_comp_s:
		#	outt.write('P %4.7f %4.7f 0.000\n' % (pt[0],pt[1]))
		#outt.close()			
		return
	
	def get_injection_point(self):
		
		# Measure extension of system along n axis (i.e. substrate normal)
		self.set_dimensions()
		
		# If not done yet, calc inj pts from xy density as to avoid piling
		if self.xy_inj_pts == []:
			self.xy_density()
		
		safety_radius = self.opt['SYSTEM']['rad'][0]
		injection_height = self.opt['SUBSTRATE']['h'][0]
		
		# n-vector coefficient describing height above lower substrate plane
		nc = self.n_min + injection_height
		
		print "Shifting",
		while nc < self.n_max + 2*safety_radius:
			nc += 2*safety_radius # [nm]			
			print "...",
		print " - Done."
		
		# Exceeds maximum allowed height?
		try:
			obey_h_max = self.opt['SUBSTRATE']['obey_h_max'][0]
		except KeyError:
			obey_h_max = False
		
		if nc - self.n_min > self.opt['SUBSTRATE']['h_max'][0]:
			if obey_h_max:
				return False
			else:
				print "NOTE Max. injection height exceeded - ignore ",
				print "(empty space, if present, may harm parallelization)."
			
		ipt_ab = self.xy_inj_pts.pop(0) # in substrate plane
		ipt_n  = nc * self.n            # along substrate normal
		
		self.in_pt = ipt_ab + ipt_n
		self.in_dir = - self.n
		
		return True
	
	def get_injection_point_simple(self):
		
		self.set_dimensions()
		
		safety_radius = self.opt['SYSTEM']['rad'][0]
		injection_height = self.opt['SUBSTRATE']['h'][0]
	
		ac = np.random.uniform(self.a_min,self.a_max)
		bc = np.random.uniform(self.b_min,self.b_max)
		nc = self.n_min + injection_height
		
		while nc < self.n_max + 2*safety_radius:
			print "Shifting..."
			nc += 2*safety_radius # [nm]			
		
		# Exceeds maximum allowed height?
		if nc - self.n_min > self.opt['SUBSTRATE']['h_max'][0]:
			return False
		
		ipt_ab = ac * self.a + bc * self.b
		ipt_n  = nc * self.n
		
		self.in_pt = ipt_ab + ipt_n	
		self.in_dir = - self.n
		
		return True
	
	def evaporate_mol(self, evap_mol):
		
		del self.evp
		self.evp = Evaporator(self.opt['EVAPORANT_%1s' % evap_mol])
		
		ret_pt = self.get_injection_point()
		if not ret_pt:
			print "Cancelled injection: reached maximum allowed h."
			return False
	
		try:
			const_vel = self.opt['EVAPORANT_%s' % evap_mol]['const_vel'][0]
			enforce_const_vel = True
		except KeyError:
			const_vel = None
			enforce_const_vel = False
	
		new_mol = self.evp.create_mol(self.in_pt, self.in_dir, enforce_const_vel, const_vel)
		self.pop.append_mol(new_mol)
		return True
		
	def group_system(self):
	
		# ==========================================================
		# Update dimensions -> density profile -> group system
		# ==========================================================
		
		auto = False
		
		try:
			auto_group = self.opt['SYSTEM']['auto_group'][0]
			if auto_group == 'yes':
				auto = True
		except KeyError:
			pass
		
		if auto:
			self.auto_group()
		else:
			self.set_dimensions()	
			self.get_density_profile()
			self.evaluate_density_profile()			
		return
		
	def get_density_profile(self, write_to_file=True):
		
		n_dp = self.n
		z_dp = []
		
		# Collect projections
		for mol in self.pop.mols:
			for atom in mol.atoms:
				z_dp.append( np.dot(n_dp, atom.pos) )	
				
		# Create histogram
		min_z = self.n_min
		max_z = self.n_max
		res_z = self.opt['SYSTEM']['res'][0]
		bin_z = int((max_z-min_z)/res_z + 0.5) + 1
		hst_z = [ 0 for i in range(bin_z) ]
		
		for z in z_dp:		
			bin = int((z-min_z)/res_z + 0.5)	
			hst_z[bin] += 1
			
		max_d = max(hst_z)
		hst_z = [ d / max_d for d in hst_z ]		
		
		# Store results
		self.hst_n_d = [ [min_z+bin*res_z,hst_z[bin]] for bin in range(len(hst_z)) ]
		
		if write_to_file:
			outt = open('%1s_density_profile.dat' % (self.grofile[:-4]), 'w')
			outt.write("# == DENSITY PROFILE ==\n")
			for n_d in self.hst_n_d:
				outt.write("%-+02.3f nm    %1.7f\n" % (n_d[0], n_d[1]))
			outt.close()
		return
		
	def evaluate_density_profile(self):
		
		if len(self.hst_n_d) == 0:
			self.get_density_profile()
		
		smooth_n_d = []
		
		for bin in range(1,len(self.hst_n_d)-1):
			smooth_n = self.hst_n_d[bin][0]
			smooth_d = 1/3. * (self.hst_n_d[bin-1][1] + self.hst_n_d[bin][1] + self.hst_n_d[bin+1][1])
			smooth_n_d.append([smooth_n,smooth_d])
		
		sub_idcs = []
		thf_idcs = []
		iph_idcs = []
		
		thf_start_d = self.opt['THINFILM']['density_start'][0]
		iph_start_d = self.opt['INTERPHASE']['density_start'][0]
		
		thf_start_n = None
		iph_start_n = None
		
		iph_set = False
		thf_set = False
		
		smooth_n_d.reverse()
		prev_n = smooth_n_d[0][0]
		prev_d = smooth_n_d[0][1]
		
		for s in smooth_n_d:
			n = s[0]
			d = s[1]
			
			if not iph_set and d > iph_start_d:
				iph_set = True
				iph_start_n = prev_n
			if not thf_set and d > thf_start_d:
				thf_set = True
				thf_start_n = prev_n
			else:
				pass
			
			prev_n = n
			prev_d = d
			
		print "thf everything farther along normal than", thf_start_n
		print "iph     ...      ...      ...        ...", iph_start_n
		
		self.fze_idcs = []
		self.sub_idcs = []
		self.thf_idcs = []
		self.iph_idcs = []
		
		sub_first = int(self.opt['SUBSTRATE']['first'][0]+0.5)
		sub_last  = int(self.opt['SUBSTRATE']['last'][0]+0.5)
		fze_first = int(self.opt['FREEZE']['first'][0]+0.5)
		fze_last  = int(self.opt['FREEZE']['last'][0]+0.5)
		
		outt = open('groups_next_iter.gro','w')
		outt.write('GROUP ASSIGNMENT FZE SUB THF IPH\n')
		outt.write('%7d\n' % self.pop.atom_count())
		
		for mol in self.pop.mols:
			
			proj = np.dot(self.n,mol.com())
			
			for atom in mol.atoms:
			
				# Substrate atom?
				if atom.Id >=  sub_first and atom.Id <= sub_last:
					self.sub_idcs.append(atom.Id) 
					atom.write_gro_ln(outt, fragName = 'SUB')
					continue
				
				# Frozen atom?
				if atom.Id >= fze_first and atom.Id <= fze_last:
					self.fze_idcs.append(atom.Id)
					atom.write_gro_ln(outt, fragName = 'FZE')
					continue
								
				if proj >= iph_start_n:
					# Interphase ...
					self.iph_idcs.append(atom.Id)
					atom.write_gro_ln(outt, fragName = 'IPH')
					
				else:
					# Thin film ...
					self.thf_idcs.append(atom.Id)
					atom.write_gro_ln(outt, fragName = 'THF')
					
		outt.write('%1s' % self.pop.box_str)
		outt.close()
		
		print "[ freeze     ] :", len(self.fze_idcs)
		print "[ substrate  ] :", len(self.sub_idcs)
		print "[ thinfilm   ] :", len(self.thf_idcs)
		print "[ interphase ] :", len(self.iph_idcs)	

	def auto_box(self):
		
		try:
			auto_scale = int(self.opt['SYSTEM']['auto_box'][0])
		except KeyError:
			auto_scale = -1
			
		if auto_scale < 1: return
		
		a_dist = []
		b_dist = []
		n_dist = []
		
		for mol in self.pop.mols:
			for atom in mol.atoms:
				a_dist.append( np.dot(atom.pos,self.a) )
				b_dist.append( np.dot(atom.pos,self.b) )
				n_dist.append( np.dot(atom.pos,self.n) )
		
		self.a_min = min(a_dist)
		self.a_max = max(a_dist)
		self.b_min = min(b_dist)
		self.b_max = max(b_dist)
		self.n_min = min(n_dist)
		self.n_max = max(n_dist)
		
		assert auto_scale in [1,2,3]
		print "Auto-scale box ..."
		print "Ctrl: Evap. normal coincides with axis %d (1<>a, 2<>b, 3<>c)" % auto_scale
		
		cutoff_corr = 2*float(self.opt['MDP']['_CUTOFF'][0])
		print "Apply cut-off correction: %+2.3f" % cutoff_corr
		
		if auto_scale == 3:			
			prev_length = magnitude(self.pop.c)
			new_length = self.n_max - self.n_min + cutoff_corr
			self.pop.c = self.pop.c / prev_length * new_length			
			print "Scaled box vector from %2.3fnm to %2.3fnm" % (prev_length, new_length)
		else:
			assert False # Not implemented
		
		# Shift system		
		shift_vec = - self.n / magnitude(self.n) * (self.n_min - 0.5*cutoff_corr)
		print "Shift system by", shift_vec
		for mol in self.pop.mols:
			mol.shift(shift_vec)
		
		return

	def estimate_bulk_z(self):
		# TODO Use this function at the beginning of ::auto_group()
		self.set_dimensions()
		self.get_density_profile(write_to_file=False)		
		hst_n_d = self.hst_n_d
		hst_n_d.reverse()		
		z_bulk_min = hst_n_d[-1][0]
		z_bulk_max = hst_n_d[-1][0]		
		for n_d in self.hst_n_d:			
			if n_d[1] < 0.5:
				continue
			else:
				z_bulk_max = n_d[0]
				break		
		hst_n_d.reverse()		
		return z_bulk_min, z_bulk_max

	def auto_group(self):	
		
		print "Auto-group: Use freeze group = %s" % (not self.cmdlineopt.nofreeze)
		
		self.set_dimensions()
		self.get_density_profile()
		
		hst_n_d = self.hst_n_d
		hst_n_d.reverse()
		
		z_bulk_min = hst_n_d[-1][0]
		z_bulk_max = hst_n_d[-1][0]
		
		for n_d in self.hst_n_d:			
			if n_d[1] < 0.5:
				continue
			else:
				z_bulk_max = n_d[0]
				break
		
		hst_n_d.reverse()
		
		print "Bulk extends over %1.2fnm." % (z_bulk_max - z_bulk_min)
		
		# MIN	 z_bulk_fze	    z_bulk_sub	    z_bulk_thf             MAX
		# FREEZE ---------|SUBSTRATE ----| THINFILM -----|INTERPHASE ----|
		
		z_bulk_sub = z_bulk_max - 2.5 * self.opt['SYSTEM']['rad'][0]
		z_bulk_fze = z_bulk_sub - 2.5 * self.opt['SYSTEM']['rad'][0]
		
		print "MIN   z_bulk_fze|    z_bulk_sub|     z_bulk_thf|            MAX|"
		print "FREEZE ---------|SUBSTRATE ----| THINFILM -----|INTERPHASE ----|"
		print " %1.3f  %1.3f |       %1.3f |        %1.3f |        %1.3f |" % (z_bulk_min,z_bulk_fze,z_bulk_sub,z_bulk_max,self.hst_n_d[-1][0])
		
		outt = open('auto_group.gro','w')
		outt.write('GROUP ASSIGNMENT FZE SUB THF IPH\n')
		outt.write('%7d\n' % self.pop.atom_count())
		
		self.iph_idcs = []
		self.thf_idcs = []
		self.sub_idcs = []
		self.fze_idcs = []

		self.mol_sub_idcs = []
		
		# List of molecules forced frozen
		fze_idcs_forced = range(int(self.opt['FREEZE']['first'][0]),int(self.opt['FREEZE']['last'][0]+1))
		if fze_idcs_forced != [0]:
			print "Freezing all molecules with ID in (%d ... %d), as requested." % (fze_idcs_forced[0],fze_idcs_forced[-1])
		
		for mol in self.pop.mols:			
			prj = np.dot(mol.com(), self.n)			
			grp = 'nogroup'			
			if prj > z_bulk_max:
				# Interphase
				grp = 'iph'				
				com_vel = mol.com_vel()
				z_prj_vel = np.dot(com_vel,self.n)
				if z_prj_vel > 0.0 and prj > z_bulk_max + 2:
					for atom in mol.atoms:
						atom.vel = atom.vel - 2*z_prj_vel * self.n
					print "Boosted reflected molecule ID %1d (%1s)" % (mol.Id, mol.name)
					print "... v", com_vel, " ->", mol.com_vel()				
			elif prj > z_bulk_sub:
				# Thin film
				grp = 'thf'
			elif prj > z_bulk_fze:
				# Substrate
				grp = 'sub'
			else:
				# Freeze
				if self.cmdlineopt.nofreeze == True:
					grp = 'sub'
				else:
					grp = 'fze'					
			if mol.Id in fze_idcs_forced:
				# Forced frozen
				grp = 'fze'
				print "Freezing mol %d %s" % (mol.Id, mol.name)
				
			for atom in mol.atoms:
				atom.write_gro_ln(outt, fragName = grp.upper())				
				if grp == 'fze':
					self.fze_idcs.append(atom.Id)
				elif grp == 'sub':
					self.sub_idcs.append(atom.Id)
				elif grp == 'thf':
					self.thf_idcs.append(atom.Id)
				elif grp == 'iph':
					self.iph_idcs.append(atom.Id)

			# Containers for moleculer ID's (used in ::xy_density)
			if grp == 'sub':
				self.mol_sub_idcs.append(mol.Id)
		
		outt.write('%1s' % self.pop.box_str)
		outt.close()
		
		print "Auto-grouped system based on cell population:"
		print "[ freeze     ] :", len(self.fze_idcs)
		print "[ substrate  ] :", len(self.sub_idcs)
		print "[ thinfilm   ] :", len(self.thf_idcs)
		print "[ interphase ] :", len(self.iph_idcs)
		
		
		return	
	
	def assemble_here(self, path = None):
		
		# ==========================================================
		# Path -> gro/top/ndx -> ctrl/hist -> grompp.mdp/qmd.sh
		# ==========================================================		
		
		# Determine path if not supplied
		here = os.getcwd()		
		if path == None and '_' in here.split('/')[-1]:
			orig = here.split('/')[-1]
			stem = orig.split('_')[0]			
			Iter = int(orig.split('_')[1])
			path = '../%1s_%1d/' % (stem, Iter+1)
		elif path == None:
			path = './ASSEMBLE/'
		else:
			if path[-1] == '/':
				pass
			else:
				path = path + '/'
		
		# Create directory, if necessary
		try:
			os.chdir(path)
			os.chdir(here)
		except OSError:
			os.mkdir(path)
		
		print "Assemble system in %1s" % path
		
		# Write system.top, system.gro
		self.pop.write_top(path)
		self.pop.write_gro(path)		
		
		# Write system.ndx
		outt = open(path+self.ndxfile,'w')
		outt.write('[ freeze ]\n')
		for i in range(len(self.fze_idcs)):
			if i % 10 == 0:
				outt.write('\n')
			outt.write('%7d ' % self.fze_idcs[i])		
		outt.write('\n\n')
		
		outt.write('[ substrate ]\n')
		for i in range(len(self.sub_idcs)):
			if i % 10 == 0:
				outt.write('\n')
			outt.write('%7d ' % self.sub_idcs[i])		
		outt.write('\n\n')
		
		outt.write('[ thinfilm ]\n')
		for i in range(len(self.thf_idcs)):
			if i % 10 == 0:
				outt.write('\n')
			outt.write('%7d ' % self.thf_idcs[i])		
		outt.write('\n\n')
			
		outt.write('[ interphase ]\n')
		for i in range(len(self.iph_idcs)):
			if i % 10 == 0:
				outt.write('\n')
			outt.write('%7d ' % self.iph_idcs[i])		
		outt.write('\n\n')
		outt.close()
		
		# Copy system.ctrl
		os.system('cp ./%1s %1s' % (self.ctrlfile, path+self.ctrlfile))		
		
		# Write system.hist
		os.system('cp ./%1s %1s' % (self.histfile, path+self.histfile))		
		
		# Write grompp.mdp
		
		MD = MD_Operator()

		# ==========================================================
		# MDP first order                        
		# ==========================================================

		# Time step, span [ps]
		dt 		= self.opt['MDP']['dt'][0]
		T  		= self.opt['MDP']['T'][0]
		dt_out	= self.opt['MDP']['dt_out'][0]

		# Input files
		_t      = self.topfile
		_c      = self.grofile
		_n		= self.ndxfile

		# Convenience
		tag		= 't_%1d_%1s' % (self.pop.t, self.tag)		
		
		# Temperatures
		Tfze = self.opt['FREEZE']['ref_t'][0]
		Tsub = self.opt['SUBSTRATE']['ref_t'][0]
		Tthf = self.opt['THINFILM']['ref_t'][0]
		Tiph = self.opt['INTERPHASE']['ref_t'][0]
		
		# Other
		maxwarn = self.opt['MDP']['maxwarn'][0]
		
		# Override ctrl-options from command line arguments
		if self.cmdlineopt.tag != None:
			tag = 'T%d_%s_%d' % (self.pop.t, self.cmdlineopt.tag, os.getpid())
			print "Override tag, new tag = %s" % tag
		if self.cmdlineopt.temperature != None:
			Tsub = self.cmdlineopt.temperature
			Tthf = self.cmdlineopt.temperature
			print "Override coupling temperature (sub,thf) from ctrl-file, new T =", Tsub 
		if self.cmdlineopt.maxwarn != None:
			maxwarn = self.cmdlineopt.maxwarn
			print "Override max. accepted grompp warnings, maxwarn =", maxwarn
		
		MD.Set('_DT',				dt)
		MD.Set('_NSTEPS',			int(T/dt+0.5))
		MD.Set('_LOGOUT',			int(dt_out/dt+0.5))
		MD.Set('_XTCOUT',			int(dt_out/dt+0.5))		


		# ==========================================================
		# MDP second order                
		# ==========================================================
		
		for key in self.opt['MDP'].keys():
			if not key[0:1] == '_':
				continue
			else:
				MD.Set(key, self.opt['MDP'][key][0])
		
		
		
		MD.Set('_TC_GRPS',			'freeze   substrate thinfilm interphase')
		MD.Set('_TAU_T',			'%1.3f  %1.3f   %1.3f  %1.3f     ' % (self.opt['FREEZE']['tau_t'][0],
		                                                                  self.opt['SUBSTRATE']['tau_t'][0], 
																	      self.opt['THINFILM']['tau_t'][0],
																		  self.opt['INTERPHASE']['tau_t'][0]))
		MD.Set('_REF_T',			'%1.3f  %1.3f   %1.3f  %1.3f     ' % (Tfze,
		                                                                  Tsub, 
																		  Tthf,
																		  Tiph))
		
		MD.Set('_COMM_GRPS',        'substrate thinfilm')
		MD.Set('_ENERGYGRPS',       'freeze substrate thinfilm interphase')
		if self.opt['FREEZE']['freeze_dim'][0].replace(' ','') == 'YYY':
			MD.Set('_ENERGYGRP_EXCL', 	'freeze freeze')
		else:
			MD.Set('_ENERGYGRP_EXCL', 	' ')
		MD.Set('_FREEZEGRPS', 		'freeze')
		MD.Set('_FREEZEDIM', 		self.opt['FREEZE']['freeze_dim'][0])

		MD.Tag(tag)


		# ==========================================================
		# MDP third order                                           
		# ==========================================================


		mdrun_cmd  = MD.gen_mdrun_cmd(
					                _s = 'topol.tpr',
						            _o = 'traj.trr',
						            _x = 'traj.xtc',
						            _c = 'confout.gro',
						            _cpo = 'state.cpt',
						            _cpt = 18,
						            _maxh = 36,
						            _d = self.opt['MDP']['precision'][0])



		grompp_cmd = MD.gen_grompp_cmd(
					                 _c = _c,
						             _p = _t,
						             _f = 'grompp.mdp',
						             _n = _n,
						             _o = 'topol.tpr',
						             _maxnum = maxwarn)

		MD.write_grompp_mdp(path+'grompp.mdp')
		MD.write_qmd_sh(path+'qmd.sh',self.cmdlineopt.username)
		
		outt = open(path+'mdp.sh','w')
		outt.write('#! /bin/bash\n')
		outt.write(grompp_cmd)
		outt.write('\n')
		outt.close()
		
		outt = open(path+'run.sh','w')
		outt.write('#! /bin/bash\n')
		outt.write(mdrun_cmd)
		outt.write('\n')
		outt.close()


class Evaporator(object):
	
	def __init__(self, opt_evaporant):
		
		self.grofile = opt_evaporant['gro'][0]
		self.topfile = opt_evaporant['top'][0]
		
		self.pop = Population(self.grofile,self.topfile)
		self.opt = opt_evaporant
		
		self.ref_t = self.opt['ref_t'][0]				
		
	def create_mol(self, start_here, fly_along, enforce_const_vel = False, const_vel = None):
		
		new_mol = Molecule(-1,'noname')		
		new_mol.import_from(self.pop.mols[0])		
		new_mol.shift(-new_mol.com()+start_here)
		
		# Generate velocity in nm/ps
		mol_mass = new_mol.mass()
		mag_v = 1e-3 * ( 2 * 1.38e-23 * self.ref_t / mol_mass / 1.67e-27 )**0.5
		if enforce_const_vel:
			print "Enforcing constant CoM velocity for molecule %s:" % new_mol.name
			print "v(CoM)=%1.3f nm/ps <=> T=%1.3fK" % (const_vel, (const_vel/mag_v*self.ref_t)) 
			mag_v = const_vel
		com_v = mag_v * fly_along
		new_mol.boost(com_v)
		
		com = new_mol.com()
		x = com[0]; 	y = com[1]; 	z = com[2]
		vx = com_v[0];	vy = com_v[1];	vz = com_v[2]
		print "Created molecule %1s: r = %1.3f %1.3f %1.3f, v = %1.4f %1.4f %1.4f" % (new_mol.name, x,y,z,vx,vy,vz)
	
		return new_mol
	
