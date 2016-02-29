from __pyosshell__ import *
from __cluster__   import *


class MD_Operator(object):
	
	def __init__(self):
		
		seed 			= int(np.random.uniform(1,1000000)+0.5)
		
		self.verbose 	= True
		
		self.mdrun_cmd 	= ''
		self.grompp_cmd = ''
		self.tag 		= 'MD_'
		
		self.opt ={'_INTEGRATOR' : 'md',      		# steep md sd ...
		           '_DT'         : 0.001,     
		           '_NSTEPS'     : 100000,
		           '_TINIT'		 : 0,
		           
			       '_TRROUT'     : 0,
			       '_LOGOUT'     : 1000,
			       '_XTCOUT'     : 1000,
			       
			       '_PBC'        : 'xyz',     		# no xy xyz
			       '_CUTOFF'     : 1.2,       
			       '_COULOMB'    : 'PME',
			       '_EWDGEOM'    : '3d',
			       '_NSTLIST'	 : 10,
			       '_NS_TYPE'    : 'grid',
			       
			       '_COMM_MODE'  : 'linear',        # none linear angular
			       '_NSTCOMM'	 : 10,
			       '_COMM_GRPS'	 : ' ',
			       
			       '_TCOUPL'     : 'Berendsen',     # no Berendsen Nose-Hoover v-rescale
			       '_TC_GRPS'    : 'System',
			       '_TAU_T'      : 2,
			       '_REF_T'      : 300,
			       
			       '_PCOUPLING'  : 'Berendsen',		# no Berendsen Parrinello-Rahman MTTK
			       '_PCOUPLTYPE' : 'anisotropic',   # isotropic semiisotropic anisotropic
			       '_TAU_P'      : '1.0 1.0 1.0 0.0 0.0 0.0',
			       '_COMPRESSIBILITY' : '4.5e-5 4.5e-5 4.5e-5 0.0 0.0 0.0',
			       '_REF_P'      : '1.0 1.0 1.0 0.0 0.0 0.0',
			       
			       '_ANNEALING'  : 'no',            # no single periodic
			       '_ANNEAL_NPOINTS' : '',
			       '_ANNEAL_TIME'    : '',
			       '_ANNEAL_TEMP'    : '',
			       
			       '_GEN_VEL'    : 'yes',           # none hbonds all-bonds h-angles all-angles
			       '_GEN_TEMP'    : 300,
			       '_SEED'       : seed,
			       
			       '_CONSTRAINTS'       : 'all-bonds',
			       '_ACC_GRPS'          : '',
			       '_ACCELERATE'        : '',       # a_x a_y a_z for each group
			       '_ENERGYGRP_EXCL'    : '', 
			       '_ENERGYGRPS'        : '',  
			       '_FREEZEDIM'         : '',    
			       '_FREEZEGRPS'        : ''}       # Y Y N N N N for two groups
		
		self.command_dict = {\
			'in_gro' : 'conf.gro',
			'top' : 'topol.top',
			'ndx' : '',
			'mdp' : 'grompp.mdp',
			'tpr' : 'topol.tpr',
			'trr' : 'traj.trr',
			'xtc' : 'traj.xtc',
			'cpt' : 'state.cpt',
			'out_gro' : 'confout.gro',
			'cpt_time' : 18,
			'wall_time' : 36,
			'prec' : '_d',
			'maxwarn' : 0}
	
	def set_input_gro_top(self, in_gro, in_top):
		self.command_dict['in_gro'] = in_gro
		self.command_dict['top'] = in_top
		return
	def set_index_file(self, ndx):
		if ndx != None:
			self.command_dict['ndx'] = '-n %s' % ndx
		return
	def set_single_precision(self):
		self.command_dict['prec'] = ''
	def set_maxwarn(self, maxwarn):
		self.command_dict['maxwarn'] = maxwarn
	def set_output_prefix(self, sfx):
		self.command_dict['out_gro'] = '%s_out.gro' % sfx
		self.command_dict['mdp'] = '%s.mdp' % sfx
		self.command_dict['tpr'] = '%s.tpr' % sfx
		self.command_dict['trr'] = '%s.trr' % sfx
		self.command_dict['xtc'] = '%s.xtc' % sfx
		self.command_dict['cpt'] = '%s.cpt' % sfx
		return
	
	def silence(self):
		self.verbose = False
	
	def Set(self,key,value):		
		try:
			self.opt[key] = value
			if self.verbose:
				print "MD: Set %-20s = %-20s" % (key, str(value))
		except KeyError:
			print "No such key", key, "in options"
			assert False
	
	def Tag(self,tag):
		self.tag = tag
	
	def set_integrator(self, integrator):
		self.Set('_INTEGRATOR', integrator)
		return
	def set_nsteps_dt(self, nsteps, dt):
		self.Set('_NSTEPS', nsteps)
		self.Set('_DT', dt)
		return
	def set_single_precision(self, use_single):
		self.command_dict['prec'] = ''
		return
	def configure_for_pop(self, pop, cutoff_target=1.2, coulomb_type='PME', ewald_geometry='3d'):
		# Adjust cutoff if necessary
		cut = cutoff_target
		if pop != None:
			x = pop.a[0]
			y = pop.b[1]
			z = pop.c[2]
			dims = [abs(x),abs(y),abs(z)]
			max_cut = min(dims)*0.49
		else:
			max_cut = cut
		if max_cut < cut:
			print "Reducing cutoff to largest possible value, rc=", max_cut
			self.Set('_CUTOFF', max_cut)
		else:
			self.Set('_CUTOFF', cut)
		self.Set('_COULOMB', coulomb_type)
		self.Set('_EWDGEOM', ewald_geometry)
		return
	def set_freeze_groups(self, groups, dims='Y Y Y'):
		group_str = ''
		if type(groups) != str:
			for g in groups:
				group_str += g + ' '
		else:
			group_str = groups
		self.Set('_FREEZEDIM', dims)
		self.Set('_FREEZEGRPS', group_str)
		return		
	def set_com_groups(self, groups, mode='linear'):
		group_str = ''
		if type(groups) != str:
			for g in groups:
				group_str += g + ' '
		else:
			group_str = groups
		self.Set('_COMM_GRPS', group_str)
		self.Set('_COMM_MODE', mode)
		return
	def set_t_coupling_groups(self, groups, tau_ts, ref_ts, t_type='v-rescale'):
		group_str = ''
		if type(groups) != str:
			for g in groups:
				group_str += g + ' '
		else:
			group_str = groups
		tau_str = ''
		if type(tau_ts) != str:
			for t in tau_ts:
				tau_str += '%+1.3f ' % t
		else:
			tau_str = tau_ts
		ref_str = ''
		if type(ref_ts) != str:
			for t in ref_ts:
				ref_str += '%+1.3f ' % t
		else:
			ref_str = ref_ts
		print group_str
		self.Set('_TC_GRPS', group_str)
		self.Set('_TAU_T', tau_str)
		self.Set('_REF_T', ref_str)
		self.Set('_TCOUPL', t_type)
		return
	def set_p_coupling(self, tau_p='5.0 5.0 5.0 0.0 0.0 0.0', typ='anisotropic', method='Berendsen', 
		compressibility='4.5e-5 4.5e-5 4.5e-5 0.0 0.0 0.0', ref_p='1.0 1.0 1.0 0.0 0.0 0.0', apply=True):
		if not apply:
			self.Set('_PCOUPLING', 'no')
			return
		self.Set('_PCOUPLING', method)
		self.Set('_PCOUPLTYPE', typ)
		self.Set('_TAU_P', tau_p)
		self.Set('_COMPRESSIBILITY', compressibility)
		self.Set('_REF_P', ref_p)
		return
	def set_annealing(self, ts, Ts, mode='single', apply=True):
		if not apply: return
		assert len(ts) == len(Ts)		
		ts_str = ''
		Ts_str = ''
		for t,T in zip(ts,Ts):
			ts_str += '%+1.3f ' % t
			Ts_str += '%+1.3f ' % T
		self.Set('_ANNEALING', mode)
		self.Set('_ANNEAL_NPOINTS', len(ts))
		self.Set('_ANNEAL_TIME', ts_str)
		self.Set('_ANNEAL_TEMP', Ts_str)
		return
	def set_gen_velocity(self, gen='yes'):
		self.Set('_GEN_VEL', gen)
		return
	
	def gen_mdrun_cmd(self,
	                        _s = None, #'topol.tpr',
		                    _o = None, #'traj.trr',
		                    _x = None, #'traj.xtc',
		                    _c = None, #'confout.gro',
		                    _cpo = None, #'state.cpt',
		                    _cpt = None, #18,
		                    _maxh = None, #36,
		                    _d = None):	
		
		if _s != None:
			self.command_dict['tpr'] = _s
		if _o != None:
			self.command_dict['trr'] = _o
		if _x != None:
			self.command_dict['xtc'] = _x
		if _c != None:
			self.command_dict['out_gro'] = _c
		if _cpo != None:
			self.command_dict['cpt'] = _cpo
		if _cpt != None:
			self.command_dict['cpt_time'] = _cpt
		if _maxh != None:
			self.command_dict['wall_time'] = _maxh
		if _d != None:
			self.command_dict['prec'] = _d
		
		#cmd = 'mdrun%0s -s %1s -o %1s -x %1s -c %1s -cpo %1s -cpt %1d -maxh %1d' \
		#	   % (_d,_s,_o,_x,_c,_cpo,_cpt,_maxh)	
		
		cmd = 'mdrun{prec} -s {tpr} -o {trr} -x {xtc} -c {out_gro} -cpo {cpt} -ctp {cpt_time} -maxh {wall_time}'.format(\
			**self.command_dict)
		
		self.mdrun_cmd = cmd
		return cmd
	
	
	
	def gen_grompp_cmd(self,
	                         _c = None, #'conf.gro',
		                     _p = None, #'topol.top',
		                     _f = None, #'grompp.mdp',
		                     _n = None, #'',
		                     _o = None, #'topol.tpr',
		                     _maxnum = None):
		
		if _c != None and _c != '':
			self.command_dict['in_gro'] = _c
		if _p != None and _p != '':
			self.command_dict['top'] = _p
		if _f != None and _f != '':
			self.command_dict['mdp'] = _f
		if _n != None and _n != '':
			self.set_index_file(_n)
		if _o != None and _o != '':
			self.command_dict['tpr'] = _o
		if _maxnum != None:
			self.command_dict['maxwarn'] = _maxnum
		
		# Index file?
		#if _n != '':
		#	_n = '-n '+_n+' '
	
		#cmd = 'grompp -c %1s -p %1s -f %1s %0s-o %1s -maxwarn %1d' \
		#	   % (_c,_p,_f,_n,_o,_maxnum)
			   
		cmd = 'grompp -c {in_gro} -p {top} -f {mdp} {ndx} -o {tpr} -maxwarn {maxwarn}'.format(\
			**self.command_dict)
		
		self.grompp_cmd = cmd		
		return cmd
	
	
	def auto_grompp(self, tpr = 'topol.tpr', maxwarn = 1):		
		extDict = dict_by_ext()		
		gro = extDict['gro']
		top = extDict['top']
		if not 'grompp.mdp' in os.listdir('./'):	
			self.write_grompp_mdp()
		self.gen_grompp_cmd(gro,top,_o=tpr,_maxnum=maxwarn)
		sig = os.system('%s &> /dev/null' % self.grompp_cmd)
		if sig:
			print "Grompp failed"
			sys.exit(1)
		os.system('rm grompp.mdp mdout.mdp')
		return		 
	
	def write_grompp_mdp(self,outfile = None, fill = True):
		if outfile != None:
			self.command_dict['mdp'] = outfile

		print "Generating MDP file",
		outt = open(self.command_dict['mdp'],'w')
		outt.write('''; CREATED BY __MDSHELL__PY
; RUN CONTROL PARAMETERS
integrator               = _INTEGRATOR
; Start time and timestep in ps
tinit                    = _TINIT
dt                       = _DT
nsteps                   = _NSTEPS
; For exact run continuation or redoing part of a run
init_step                = 0
; mode for center of mass motion removal
;comm-mode                 = None
;comm-mode                = None
comm-mode                = _COMM_MODE
;comm-mode                = Angular
; number of steps for center of mass motion removal
nstcomm                  = _NSTCOMM
; group(s) for center of mass motion removal
comm-grps                = _COMM_GRPS

; LANGEVIN DYNAMICS OPTIONS
; Temperature, friction coefficient (amu/ps) and random seed
bd-fric                  = 0.5
ld-seed                  = _SEED

; ENERGY MINIMIZATION OPTIONS
; Force tolerance and initial step-size
emtol                    = 1 
emstep                   = 0.01
; Max number of iterations in relax_shells
niter                    = 20
; Step size (1/ps^2) for minimization of flexible constraints
fcstep                   = 0
; Frequency of steepest descents steps when doing CG
nstcgsteep               = 1000
nbfgscorr                = 10

; OUTPUT CONTROL OPTIONS
; Output frequency for coords (x), velocities (v) and forces (f)
nstxout                  = _TRROUT
nstvout                  = _TRROUT 
nstfout                  = _TRROUT
; Checkpointing helps you continue after crashes
nstcheckpoint            = 0
; Output frequency for energies to log file and energy file
nstlog                   = _LOGOUT
nstenergy                = _LOGOUT
; Output frequency and precision for xtc file
nstxtcout                = _XTCOUT
xtc-precision            = 1000
; This selects the subset of atoms for the xtc file. You can
; select multiple groups. By default all atoms will be written.
xtc-grps                 = 
; Selection of energy groups
energygrps               = _ENERGYGRPS

; NEIGHBORSEARCHING PARAMETERS
; nblist update frequency
nstlist                  = _NSTLIST
; ns algorithm (simple or grid)
ns_type                  = _NS_TYPE
; Periodic boundary conditions: xyz (default), no (vacuum)
; or full (infinite systems only)
pbc                      = _PBC
;pbc                      = xyz
;pbc                      = no
; nblist cut-off        
rlist                    = _CUTOFF

; OPTIONS FOR ELECTROSTATICS AND VDW
; Method for doing electrostatics
;coulombtype              = Cut-off
coulombtype              = _COULOMB
;coulombtype             = PME
rcoulomb-switch          = 0
rcoulomb                 = _CUTOFF
; Dielectric constant (DC) for cut-off or DC of reaction field
epsilon-r                = 1
; Method for doing Van der Waals
vdw-type                 = Cut-off
; cut-off lengths       
rvdw-switch              = 0
rvdw                     = _CUTOFF
; Apply long range dispersion corrections for Energy and Pressure
;DispCorr                 = EnerPres
; Extension of the potential lookup tables beyond the cut-off
table-extension          = 1
; Spacing for the PME/PPPM FFT grid
fourierspacing           = 0.12
; FFT grid size, when a value is 0 fourierspacing will be used
fourier_nx               = 0
fourier_ny               = 0
fourier_nz               = 0
; EWALD/PME/PPPM parameters
pme_order                = 4
ewald_rtol               = 1e-05
ewald_geometry           = _EWDGEOM
epsilon_surface          = 0
optimize_fft             = no

; GENERALIZED BORN ELECTROSTATICS
; Algorithm for calculating Born radii
gb_algorithm             = Still
; Frequency of calculating the Born radii inside rlist
nstgbradii               = 1
; Cutoff for Born radii calculation; the contribution from atoms
; between rlist and rgbradii is updated every nstlist steps
rgbradii                 = 2
; Salt concentration in M for Generalized Born models
gb_saltconc              = 0

; IMPLICIT SOLVENT (for use with Generalized Born electrostatics)
implicit_solvent         = No

; OPTIONS FOR WEAK COUPLING ALGORITHMS
; Temperature coupling  
Tcoupl                    = _TCOUPL
;Tcoupl                   = Berendsen
;Tcoupl                   = nose-hoover
; Groups to couple separately
tc-grps                  = _TC_GRPS
; Time constant (ps) and reference temperature (K)
tau_t                    = _TAU_T
ref_t                    = _REF_T
; Pressure coupling    
;Pcoupl                 = Parrinello-Rahman
Pcoupl                    = _PCOUPLING
;Pcoupl                   = no
Pcoupltype               = _PCOUPLTYPE
; Time constant (ps), compressibility (1/bar) and reference P (bar)
tau_p                    = _TAU_P
compressibility          = _COMPRESSIBILITY
ref_p                    = _REF_P
; Random seed for Andersen thermostat
andersen_seed            = _SEED

; SIMULATED ANNEALING  
; Type of annealing for each temperature group (no/single/periodic)
annealing                = _ANNEALING
; Number of time points to use for specifying annealing in each group
annealing_npoints        = _ANNEAL_NPOINTS
; List of times at the annealing points for each group
annealing_time           = _ANNEAL_TIME
; Temp. at each annealing point, for each group.
annealing_temp           = _ANNEAL_TEMP

; GENERATE VELOCITIES FOR STARTUP RUN
;gen_vel                  = no
gen_vel                  = _GEN_VEL
gen_temp                 = _GEN_TEMP
gen_seed                 = _SEED

; OPTIONS FOR BONDS    
;constraints              = none
constraints              = _CONSTRAINTS
; Type of constraint algorithm
constraint-algorithm     = Lincs
; Do not constrain the start configuration
unconstrained-start      = no
; Use successive overrelaxation to reduce the number of shake iterations
Shake-SOR                = no
; Relative tolerance of shake
shake-tol                = 1e-04
; Highest order in the expansion of the constraint coupling matrix
lincs-order              = 4
; Number of iterations in the final step of LINCS. 1 is fine for
; normal simulations, but use 2 to conserve energy in NVE runs.
; For energy minimization with constraints it should be 4 to 8.
lincs-iter               = 8
; Lincs will write a warning to the stderr if in one step a bond
; rotates over more degrees than
lincs-warnangle          = 30
; Convert harmonic bonds to morse potentials
morse                    = no

; ENERGY GROUP EXCLUSIONS
; Pairs of energy groups for which all non-bonded interactions are excluded
energygrp_excl           = _ENERGYGRP_EXCL

; NMR refinement stuff 
; Distance restraints type: No, Simple or Ensemble
disre                    = No
; Force weighting of pairs in one distance restraint: Conservative or Equal
disre-weighting          = Conservative
; Use sqrt of the time averaged times the instantaneous violation
disre-mixed              = no
disre-fc                 = 1000
disre-tau                = 0
; Output frequency for pair distances to energy file
nstdisreout              = 100
; Orientation restraints: No or Yes
orire                    = no
; Orientation restraints force constant and tau for time averaging
orire-fc                 = 0
orire-tau                = 0
orire-fitgrp             = 
; Output frequency for trace(SD) to energy file
nstorireout              = 100
; Dihedral angle restraints: No, Simple or Ensemble
dihre                    = No
dihre-fc                 = 1000
dihre-tau                = 0
; Output frequency for dihedral values to energy file
nstdihreout              = 100

; Free energy control stuff
free-energy              = no
init-lambda              = 0
delta-lambda             = 0
sc-alpha                 = 0
sc-sigma                 = 0.3

; Non-equilibrium MD stuff
acc-grps                 = _ACC_GRPS
accelerate               = _ACCELERATE
freezegrps               = _FREEZEGRPS
freezedim                = _FREEZEDIM
cos-acceleration         = 0

; Electric fields      
; Format is number of terms (int) and for all terms an amplitude (real)
; and a phase angle (real)
E-x                      = 
E-xt                     = 
E-y                      = 
E-yt                     = 
E-z                      = 
E-zt                     = 

; User defined thingies
user1-grps               = 
user2-grps               = 
userint1                 = 0
userint2                 = 0
userint3                 = 0
userint4                 = 0
userreal1                = 0
userreal2                = 0
userreal3                = 0
userreal4                = 0			
''')
		outt.close()
		
		if fill:
			print "- setting MD options."
			self.opt['_SEED'] = int(np.random.uniform(1,1000000)+0.5)
			subs = [ key                for key in self.opt.keys() ]
			reps = [ str(self.opt[key]) for key in self.opt.keys() ]
			auto_replace(self.command_dict['mdp'],subs,reps)
		else:
			print "..."


	def write_qmd_sh(self, outfile = 'qmd.sh', username = getpass.getuser(), queue='PE_8', procs=8):
		
		write_qsub_sh_template(outfile, username, queue=queue, procs=procs)
		
		auto_replace(outfile,
		    ['_DESCRIPTION','_GROMPP_CMD','#_MDRUN_CMD','_USERNAME'],
		    [self.tag,self.grompp_cmd,self.mdrun_cmd,username])
		

