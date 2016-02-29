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

	def gen_mdrun_cmd(self,
	                        _s = 'topol.tpr',
		                    _o = 'traj.trr',
		                    _x = 'traj.xtc',
		                    _c = 'confout.gro',
		                    _cpo = 'state.cpt',
		                    _cpt = 18,
		                    _maxh = 36,
		                    _d = '_d'):	

		cmd = 'mdrun%0s -s %1s -o %1s -x %1s -c %1s -cpo %1s -cpt %1d -maxh %1d' \
			   % (_d,_s,_o,_x,_c,_cpo,_cpt,_maxh)	
	
		self.mdrun_cmd = cmd
		return cmd
	
	
	
	def gen_grompp_cmd(self,
	                         _c = 'conf.gro',
		                     _p = 'topol.top',
		                     _f = 'grompp.mdp',
		                     _n = '',
		                     _o = 'topol.tpr',
		                     _maxnum = 0):
	
		# Index file?
		if _n != '':
			_n = '-n '+_n+' '
	
		cmd = 'grompp -c %1s -p %1s -f %1s %0s-o %1s -maxwarn %1d' \
			   % (_c,_p,_f,_n,_o,_maxnum)
		
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
	
	def write_grompp_mdp(self,outfile = 'grompp.mdp', fill = True):
	
		print "Generating MDP file",
	
		outt = open(outfile,'w')

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
ewald_geometry           = 3d
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
			auto_replace(outfile,subs,reps)
		else:
			print "..."


	def write_qmd_sh(self, outfile = 'qmd.sh', username = getpass.getuser()):
		
		write_qsub_sh_template(outfile, username)
		
		auto_replace(outfile,
		    ['_DESCRIPTION','_GROMPP_CMD','#_MDRUN_CMD','_USERNAME'],
		    [self.tag,self.grompp_cmd,self.mdrun_cmd,username])
		

