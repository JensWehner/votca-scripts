from __future__		import division
from __evp_system__ import *

# ============================================================= #
#              SIMULATION META PARAMETERS, VARIABLES            #
# ============================================================= #

ARGS				= None

RESTART_WITH_ITER	= None
RESTART_FROM_TIME	= None

RUN_TIME_ITER		= None	
MAX_MOLS_ITER		= None	
MAX_ITER			= None	
KEEP_EVERY_NTH_ITER = None			

RESTART_FROM_MOLS	= None	
MOLS_TARGET			= None
BULK_TARGET         = None


ON_CLUSTER			= None	
RUN					= None	

GRO					= None	
TOP					= None	
NDX					= None	
CTR					= None	
HST					= None	

SYSTEM_DIR			= None	

REQUIRED_DIRS		= None	


# ============================================================= #

SIM_TIME			= None	
MOL_COUNT			= None
BULK_SIZE           = None
SIM_ITER			= None	
EVO_STEP			= None	

EVO_STEP_CMDS		= None

def set_globals(arg1,  arg2,  arg3,  arg4,  arg5,
                arg6,  arg7,  arg8,  arg9,  arg10,
                arg11, arg12, arg13, arg14, arg15,
                arg16, arg17, arg18, arg19, arg20,
                arg21, arg22, arg23, arg24):
	
	global ARGS
	
	global RESTART_WITH_ITER
	global RESTART_FROM_TIME
	
	global RUN_TIME_ITER
	global MAX_MOLS_ITER
	global MAX_ITER
	global KEEP_EVERY_NTH_ITER
	
	global RESTART_FROM_MOLS
	global MOLS_TARGET
	global BULK_TARGET
	
	global ON_CLUSTER
	global RUN
	
	global GRO
	global TOP
	global NDX
	global CTR
	global HST
	
	global SYSTEM_DIR
	global REQUIRED_DIRS
	
	global SIM_TIME
	global MOL_COUNT
	global BULK_SIZE
	global SIM_ITER
	global EVO_STEP
	
	global EVO_STEP_CMDS
	
	ARGS				= arg23
	
	RESTART_WITH_ITER 	= arg1
	RESTART_FROM_TIME 	= arg2
	
	RUN_TIME_ITER 		= arg3
	MAX_MOLS_ITER 		= arg4
	MAX_ITER 			= arg5
	KEEP_EVERY_NTH_ITER = arg22
	
	RESTART_FROM_MOLS 	= arg6
	MOLS_TARGET 		= arg7
	BULK_TARGET         = arg24
	
	ON_CLUSTER 			= arg8
	RUN				 	= arg9
	
	GRO 				= arg10
	TOP 				= arg11
	NDX 				= arg12
	CTR 				= arg13
	HST 				= arg14
	
	SYSTEM_DIR 			= arg15
	REQUIRED_DIRS 		= arg16
	
	SIM_TIME			= arg17
	MOL_COUNT			= arg18
	BULK_SIZE           = 0
	SIM_ITER			= arg19
	EVO_STEP			= arg20
	
	EVO_STEP_CMDS		= arg21
	
	
	
def clean_if_applicable(prefix='ITER_'):
	
	global EVO_STEP
	global KEEP_EVERY_NTH_ITER
	
	if EVO_STEP % KEEP_EVERY_NTH_ITER == 0 or True:	 # Override
		folders = [ f for f in os.listdir('./') if prefix in f ]
		
		for folder in folders:			
			sim_iter = int(folder[5:])
			
			if sim_iter % KEEP_EVERY_NTH_ITER == 0:
				pass
			elif EVO_STEP - sim_iter <= 5:
				pass
			else:
				exe("rm -r ./%1s" % folder)
	return True


def obtain_status(gro, top, ndx, ctr, hst, iter_prefix='ITER_'):
	
	global ARGS
	
	next_iter, mols_target, mols_current, iter_time = \
	    autorestart_find_next_iter(gro, top, ndx, ctr, hst, iter_prefix,
	        verbose=False)
	
	latest_iter = next_iter-1
	
	logfile = None
	rootfiles = [ item for item in os.listdir('./') if not os.path.isdir(item) ]
	for rootfile in rootfiles:
		if 'log' in rootfile:
			logfile = rootfile			
			break
	
	pid = -1
	root = os.getcwd().split('/')[-1]
	tag = "___"
	
	if logfile != None:
		# Retrieve PID
		pid = convert_os_cmd(cmd = 'cat %s | grep PID | tail -n 1' % logfile, colidx=-1, typ=int)
		is_active = not os.system('ps caux | grep %d > /dev/null' % pid)
		if not is_active: pid = '-----'
		# Retrieve tag
		tag = convert_os_cmd(cmd = 'cat %s | grep "ID tag" | tail -n 1' % logfile, colidx=-1, typ=str)
	
	# Calculate progress (# evaporated / # targeted)
	count_current_total = 0
	count_target_total = 0
	for current,target in zip(mols_current,mols_target):
		sp1 = current.split(':')
		sp2 = target.split(':')
		molname = sp1[0]
		assert sp1[0] == sp2[0]
		count_current = int(sp1[1])
		count_target = int(sp2[1])
		count_current_total += count_current
		count_target_total += count_target
	prog = 100*float(count_current_total)/count_target_total		
	
	# Bulk size
	os.chdir('%s%d' % (iter_prefix, latest_iter))
	system = System(gro, top, ndx, ctr, hst, ARGS, verbose=False)
	z0,z1 = system.estimate_bulk_z()
	dz = z1-z0
	os.chdir('../')
	
	# Queue ID
	try:
		os.chdir('%s%d' % (iter_prefix, latest_iter+1))
		qid = retrieve_qid()
		os.chdir('../')
	except OSError:
		qid = '------'
	
	print "ROOT= %-20s TAG= %-20s PID= %-5s QID= %s TIME= %-5d ITER= %-4d PROG= %3.0f%% EVAP= %4d BULK= %2.1fnm" % \
	    (root, tag[:-1], pid, qid, iter_time, next_iter, prog, count_current_total, dz)
	
	if False: # TODO verbose
		for current,target in zip(mols_current,mols_target):
			sp1 = current.split(':')
			sp2 = target.split(':')
			molname = sp1[0]
			assert sp1[0] == sp2[0]
			count_current = int(sp1[1])
			count_target = int(sp2[1])
			if count_target == 0: 
				print "\t%-15s %4d/%-4d" % \
					(molname, count_current, count_target)
			else:
				print "\t%-15s %4d/%-4d -> %2.0f%% complete" % \
				    (molname, count_current, count_target, 
				    100*float(count_current)/count_target)	
	sys.exit(0)
	assert False
	return
	

def autorestart_find_next_iter(gro, top, ndx, ctr, hst,
        iter_prefix='ITER_', verbose=True):
	
	if verbose: print "Auto-restart from root =", os.getcwd()
	iters = get_dirs(regex=iter_prefix)

	if iters == []:
		return None,None,None,None

	iter_ids = []
	for iteration in iters:
		iter_ids.append(int(iteration.split('_')[-1]))
	iter_ids.sort()
	
	if verbose: print "Snapshots available for restart: # = %d" % len(iter_ids)
	
	iter_slot = -1
	latest_iter = iter_ids[iter_slot]
	mols = []
	mols_current = []
	iter_time = 0
	
	while latest_iter > 0:
		latest_iter = iter_ids[iter_slot]
		latest_dir = '%s%d' % (iter_prefix,latest_iter)
		os.chdir(latest_dir)
		
		files = os.listdir('./')
		try:
			assert gro in files
			assert top in files
			assert ndx in files
			assert ctr in files
			assert hst in files
			
			# Check for completeness of gro-file
			intt = open(gro,'r')
			lns = intt.readlines()
			lenlns = len(lns)
			intt.close()
			if lenlns < 3:
				if verbose: print "%s in %s is broken" % (gro,latest_iter)
				assert False
			
			# Check for completeness in log file
			intt = open(hst, 'r')
			iter_found = False
			for ln in intt.readlines():
				ln = ln.replace(',',' ')
				sp = ln.split()
				if sp == []:
					continue
				elif sp[0] == 'Log':
					iter_nr = int(sp[-1])
					iter_time = float(sp[3])
					if iter_found:
						break
					if iter_nr == latest_iter:
						iter_found = True
						if verbose: print "Found log entry for iteration %d in %s" % (latest_iter,hst)
					else: pass
				elif sp[0] != 'Log' and iter_found:
					mol_name = sp[0]
					mol_target = int(sp[-1])
					mol_current = int(sp[-3])
					mols.append('%s:%d' % (mol_name,mol_target))
					mols_current.append('%s:%d' % (mol_name,mol_current))
				elif sp[0] != 'Log':				
					pass			
				else: print 1/0 # Error in hist-file
					
			if not iter_found:
				assert False # Iteration not found in log-file (*.hist)				
			break
		except AssertionError:
			if verbose: print "Candidate %s not complete. Continue backwards ..." % latest_dir
			iter_slot = iter_slot - 1
		
		os.chdir('../')		
	os.chdir('../')
	if verbose: print "Latest iteration = %d in directory '%s'" % (latest_iter,latest_dir)

	return latest_iter+1, mols, mols_current, iter_time


def originate(in_dir):

	global GRO; global TOP; global NDX; global CTR; global HST;	

	global RESTART_WITH_ITER			
	global SYSTEM_DIR
	global REQUIRED_DIRS
	
	global EVO_STEP
	
	global SIM_TIME
	global MOL_COUNT
	global MOLS_TARGET
	
		
	if RESTART_WITH_ITER == 1:
		assemble_dir = './%1s0' % in_dir
		os.chdir(SYSTEM_DIR)

		print "="*80
		print "Originating system, step = %1d:" % EVO_STEP
		for key in MOL_COUNT.keys():
			print "... %-5s %5d/%1d" % (key, MOL_COUNT[key], MOLS_TARGET[key])
		print "="*80

		system = System(GRO,TOP,NDX,CTR,HST,ARGS)
		
		#system.group_system()
		#system.xy_density()
		system.assemble_here('../'+assemble_dir)

		del system
		os.chdir('../')
	
		for DIR in REQUIRED_DIRS:
			exe('cp -r %1s %1s' % (DIR, assemble_dir))	
	else:
		restart_dir = './%s%d' % (in_dir, RESTART_WITH_ITER-1)
		print "Restarting from iteration %d using %s" % (RESTART_WITH_ITER, restart_dir)
		os.chdir(restart_dir)
		
		# Retrieve restart configuration from hist-file (HST)
		# ... Set SIM_TIME, MOL_COUNT
		intt = open(HST, 'r')
		iter_found = False	
		for ln in intt.readlines():
			ln = ln.replace(',',' ')
			sp = ln.split()
			if sp == []:
				continue
			elif sp[0] == 'Log':
				iter_nr = int(sp[-1])
				if iter_found: break			
				elif iter_nr == RESTART_WITH_ITER-1:
					iter_found = True
					print "Found log entry for iteration %d in %s" % (RESTART_WITH_ITER-1,HST)
					SIM_TIME = float(sp[3])
					print "... Restart from time t =", SIM_TIME
				else: pass			
			elif sp[0] != 'Log':				
				if iter_found:
					mol_name = sp[0]
					mol_nr = int(sp[1])
					RESTART_FROM_MOLS[mol_name] = mol_nr
					MOL_COUNT[mol_name] = mol_nr
					print "... Restart from # %s = %d" % (mol_name, mol_nr)
				else: pass			
			else: assert False
					
		if not iter_found:
			assert False # Iteration not found in log-file (*.hist)				
		
		os.chdir('../')
		
	return		


def which_mol_to_evap():
	
	global MOL_COUNT
	global MOLS_TARGET
	
	ratio 	= {}
	ratios 	= []
	for key in MOLS_TARGET.keys():
		if MOLS_TARGET[key] == 0:
			ratio[key] = 1.0
		else:
			ratio[key] = MOL_COUNT[key] / MOLS_TARGET[key]
		
		ratios.append(ratio[key])
			
	min_ratio = min(ratios)
	for key in MOLS_TARGET.keys():
		if ratio[key] == min_ratio:
			print "Decided to evaporate %1s next." % key
			return key
		else:
			pass
	
	print "Could not decide which molecule to evaporate next."
	return None
		

def enough_mols():
	
	global MOL_COUNT
	global BULK_SIZE
	global MOLS_TARGET
	global BULK_TARGET
	
	if BULK_SIZE > BULK_TARGET:
		return True
	
	for key in MOLS_TARGET.keys():
		if MOL_COUNT[key] < MOLS_TARGET[key]:
			return False
		else:
			pass
			
	return True		


def enough_iters():
	
	global SIM_ITER
	global MAX_ITER
	
	return SIM_ITER >= MAX_ITER


def evolve(from_dir,to_dir, nr_evaps, t_in, t_run):
	
	global GRO; global TOP; global NDX; global CTR; global HST;
	
	global REQUIRED_DIRS
	global MOL_COUNT
	global BULK_SIZE
	global MOLS_TARGET
	global BULK_TARGET
	global MAX_MOLS_ITER
	
	global RUN_TIME_ITER
	global SIM_TIME
	global EVO_STEP	
	global EVO_STEP_CMDS
	
	EVO_STEP += 1	
	
	if nr_evaps == None:
		nr_evaps = MAX_MOLS_ITER
	if t_in == None:
		t_in = SIM_TIME
	if t_run == None:
		t_run = RUN_TIME_ITER
	
	from_dir = from_dir + '%1d' % (EVO_STEP-1)
	to_dir	 = to_dir   + '%1d' % (EVO_STEP)
	
	print "="*80
	print "Evolving system, step = %1d:" % EVO_STEP
	for key in MOL_COUNT.keys():
		print "... %-15s %5d/%1d" % (key, MOL_COUNT[key], MOLS_TARGET[key])
	print "="*80
	
	os.chdir('./%1s' % from_dir)
	
	for FREQ_CMD in EVO_STEP_CMDS:
		freq = FREQ_CMD[0]
		cmd  = FREQ_CMD[1]
		if EVO_STEP % freq == 0:
			print "STEP %1d EXE %1s" % (EVO_STEP, cmd)
			exe(cmd)
		else:
			pass
	
	if 'topol.tpr' in os.listdir('./'):
		print "Placing all atoms inside the periodic box to evaluate height profile."
		exe('echo "0" | trjconv -f %1s -o %1s -pbc atom -ur tric > /dev/null 2> /dev/null' % (GRO,GRO))
	else:
		print "NOTE: No topol.tpr in directory. Make sure %1s is wrapped." % GRO
	
	system = System(GRO,TOP,NDX,CTR,HST,ARGS)
	system.set_time(t_in,t_run)
	system.xy_density() # evaporate_mol() also does this automatically
	
	for n in range(nr_evaps):
	
		evap_mol = which_mol_to_evap()
		if evap_mol == None:			
			assert False # No mol. name given
	
		os.chdir('./EVAPORATOR_%1s' % evap_mol)
		exe('python evaporate.py')
		os.chdir('../')
		if system.evaporate_mol(evap_mol):
			MOL_COUNT[evap_mol] += 1
			if enough_mols():
				break
		else:
			break
	
	system.auto_box()
	system.group_system()
	system.assemble_here('../%1s' % to_dir)
	
	z0,z1 = system.estimate_bulk_z()
	BULK_SIZE = z1-z0
	if BULK_SIZE > BULK_TARGET:
		print "Bulk size %1.3f exceeds %1.3f -> Enough molecules" % (BULK_SIZE,BULK_TARGET)
	else:
		print "Bulk size %1.3f <= %1.3f -> More molecules" % (BULK_SIZE,BULK_TARGET)
	
	del system
	
	os.chdir('../')
	
	for DIR in REQUIRED_DIRS:
		exe('cp -r %1s ./%1s' % (DIR, to_dir))
	
	return True
		

def simulate(in_dir):

	global RUN
	global ON_CLUSTER	
	
	global SIM_TIME
	global EVO_STEP
	global RUN_TIME_ITER
	
	in_dir = in_dir + '%1d' % EVO_STEP
	
	os.chdir('./%1s' % in_dir)
	
	# ... Exe grompp
	exe('chmod +x mdp.sh')
	exe_safe('./mdp.sh > /dev/null 2> grompp.out')
	print "Grompp summary ..."
	s1 = os.system("pcregrep -M 'NOTE(.)*\n(.)*\n' grompp.out")
	s2 = os.system("pcregrep -M 'WARNING(.)*\n(.)*\n' grompp.out")
	s3 = os.system("pcregrep -M 'ERROR(.)*\n(.)*\n' grompp.out")
	print "Grompp complete",
	if not s1: print "(see notes)",
	if not s2: print "(see warnings)",
	if not s3: print "(errors!)",
	print "."
	os.system("rm grompp.out")	
	
	if not 'topol.tpr' in os.listdir('./'):
		print "Missing topol.tpr. Error in grompp? Abort."
		return False

	# ... Exe mdrun
	if RUN:	
		if ON_CLUSTER:
			# ... Check queue if specified
			if ARGS.nicejob:
				print "This is a nice job: Checking queue ..."
				jobs_waiting = are_jobs_waiting(ARGS.username)
				if jobs_waiting:
					print "Job waits for queue to be cleared."
				while jobs_waiting:
					print "Sleep ..."
					time.sleep(10)
					jobs_waiting = are_jobs_waiting(ARGS.username)
				print "No jobs waiting. Submit ..."
			# ... Submit job
			exe('qsub qmd.sh')
			# ... Wait for mdrun
			exists = monitor_dir_for_file('confout.gro', verbose = True, t_h = 144)
			if not exists: 
				print "File confout.gro did not pop up in time.";
				return False
		else:
			exe('chmod +x run.sh')
			exe('./run.sh')
		
		
		
	else:
		exe('cp %1s confout.gro' % (GRO))	
	
	if not 'confout.gro' in os.listdir('./'):
		print "Did GROMACS terminate correctly? Missing confout.gro. Abort."
		sys.exit(1)
		
	SIM_TIME += RUN_TIME_ITER
	
	# ... Rename files
	exe('mv %1s %1s_initial.gro' % (GRO,GRO[:-4]))
	exe('mv confout.gro %1s'     % (GRO))	
	
	os.chdir('../')	
	return True


def log_iter(in_dir):
	
	global HST
	global SIM_TIME
	global EVO_STEP
	global MOL_COUNT
	
	global SIM_ITER
	
	in_dir = in_dir + '%1d' % EVO_STEP
	
	SIM_ITER += 1
	
	os.chdir('./%1s' % in_dir)
	
	outt = open(HST,'a')
	outt.write('Log t = %5d, iter (since restart) = %4d, iter (since start) = %4d\n' % (SIM_TIME,SIM_ITER,EVO_STEP))
	for key in MOLS_TARGET.keys():
		outt.write('    %-5s %5d / %-5d\n' % (key, MOL_COUNT[key], MOLS_TARGET[key]))
	
	os.chdir('../')
	return True
	
	


