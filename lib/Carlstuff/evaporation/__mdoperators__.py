from __mdpassist__ import *


"""
mdrun_cmd  = md_steep.gen_mdrun_cmd(
	                        _s = 'topol.tpr',
		                    _o = 'traj.trr',
		                    _x = 'traj.xtc',
		                    _c = 'confout.gro',
		                    _cpo = 'state.cpt',
		                    _cpt = 18,
		                    _maxh = 36,
		                    _d = '_d')



grompp_cmd = md_steep.gen_grompp_cmd(
	                         _c = _c,
		                     _p = _t,
		                     _f = 'grompp.mdp',
		                     _n = _n,
		                     _o = 'topol.tpr',
		                     _maxnum = 0)

print grompp_cmd
print mdrun_cmd
"""


md_steep = MD_Operator()
md_steep.silence()

# ============================================================== #
# FIRST ORDER INPUT                                              #
# ============================================================== #

md_steep.Set('_INTEGRATOR',		'steep')
md_steep.Set('_DT',				0.001)
md_steep.Set('_NSTEPS',			100000)

md_steep.Set('_TRROUT',			0)
md_steep.Set('_LOGOUT',			100)
md_steep.Set('_XTCOUT',			100)


# ============================================================== #
# SECOND ORDER INPUT                                             #
# ============================================================== #

md_steep.Set('_PBC',				'xyz')
md_steep.Set('_CUTOFF',			 1.2)
md_steep.Set('_COULOMB',			'PME')
md_steep.Set('_NSTLIST',			'10')

md_steep.Set('_COMM_MODE',        'linear')
md_steep.Set('_COMM_GRPS',		' ')

md_steep.Set('_TCOUPL',			'no')
md_steep.Set('_TC_GRPS',			'System')
md_steep.Set('_TAU_T',			1.0)
md_steep.Set('_REF_T',			10) 

md_steep.Set('_PCOUPLING',		'no')	# !	
md_steep.Set('_PCOUPLTYPE' ,	 	'isotropic')    # !
md_steep.Set('_TAU_P'      , 		'5.0 5.0 5.0 0.0 0.0 0.0') # 1.0 1.0 1.0
md_steep.Set('_COMPRESSIBILITY' , '4.5e-5 4.5e-5 4.5e-5 0.0 0.0 0.0')
md_steep.Set('_REF_P'      , 		'1.0 1.0 1.0 0.0 0.0 0.0')
	       
md_steep.Set('_ANNEALING'  , 		'no')         
md_steep.Set('_ANNEAL_NPOINTS','')
md_steep.Set('_ANNEAL_TIME',	'')
md_steep.Set('_ANNEAL_TEMP', 	'')
	       
md_steep.Set('_GEN_VEL'    , 		'yes')        
md_steep.Set('_GEN_TEMP'    , 	10)
			       
md_steep.Set('_CONSTRAINTS', 		'none')
md_steep.Set('_ACC_GRPS', 		'')
md_steep.Set('_ACCELERATE', 		'')    
md_steep.Set('_ENERGYGRP_EXCL', 	'')   
md_steep.Set('_FREEZEDIM', 		    '')    
md_steep.Set('_FREEZEGRPS', 		'')

md_steep.Tag('STEEP')



md_sd = MD_Operator()
md_sd.silence()

# ============================================================== #
# FIRST ORDER INPUT                                              #
# ============================================================== #

md_sd.Set('_INTEGRATOR',		'sd')
md_sd.Set('_DT',				0.001)
md_sd.Set('_NSTEPS',			100000)

md_sd.Set('_TRROUT',			0)
md_sd.Set('_LOGOUT',			1000)
md_sd.Set('_XTCOUT',			1000)


# ============================================================== #
# SECOND ORDER INPUT                                             #
# ============================================================== #

md_sd.Set('_PBC',				'xyz')
md_sd.Set('_CUTOFF',			 1.2)
md_sd.Set('_COULOMB',			'PME')
md_sd.Set('_NSTLIST',			'10')

md_sd.Set('_COMM_MODE',        'linear')
md_sd.Set('_COMM_GRPS',		' ')

md_sd.Set('_TCOUPL',			'no')
md_sd.Set('_TC_GRPS',			'System')
md_sd.Set('_TAU_T',			1.0)
md_sd.Set('_REF_T',			10) 

md_sd.Set('_PCOUPLING',		'no')	# !	
md_sd.Set('_PCOUPLTYPE' ,	 	'isotropic')    # !
md_sd.Set('_TAU_P'      , 		'5.0 5.0 5.0 0.0 0.0 0.0') # 1.0 1.0 1.0
md_sd.Set('_COMPRESSIBILITY' , '4.5e-5 4.5e-5 4.5e-5 0.0 0.0 0.0')
md_sd.Set('_REF_P'      , 		'1.0 1.0 1.0 0.0 0.0 0.0')
	       
md_sd.Set('_ANNEALING'  , 		'no')         
md_sd.Set('_ANNEAL_NPOINTS','')
md_sd.Set('_ANNEAL_TIME',	'')
md_sd.Set('_ANNEAL_TEMP', 	'')
	       
md_sd.Set('_GEN_VEL'    , 		'yes')        
md_sd.Set('_GEN_TEMP'    , 	10)
			       
md_sd.Set('_CONSTRAINTS', 		'none')
md_sd.Set('_ACC_GRPS', 		'')
md_sd.Set('_ACCELERATE', 		'')    
md_sd.Set('_ENERGYGRP_EXCL', 	'')   
md_sd.Set('_FREEZEDIM', 		    '')    
md_sd.Set('_FREEZEGRPS', 		'')

md_sd.Tag('SD')


