#! /usr/bin/env python
from __pyosshell__ import *
from __lxml__ import *
from ctp__options__ import *
from ctp__cluster__ import *
from ctp__jobfile__ import *
from momo import osio, endl, flush

def safe_remove(path):
	cdx = raw_input("Remove '%s' ? (yes/no)" % path)
	if cdx == 'yes':
		os.system('rm -rf %s' % path)
	else:
		print "Nothing happened"
	return
	
def safe_mkdir(path):
	if not os.path.exists(path):
		os.mkdir(path)
	return

def write_header(title):
	try:
		height, width = os.popen('stty size', 'r').read().split()
		width = int(width)
		leftright = int((width - len(title)-2)/2)
	except ValueError:
		leftright = 40
	print "="*leftright, title, "="*leftright
	return
	
def countdown(t_sec):
	osio.os_print_config(tl='')
	colours = [osio.ww, osio.mb, osio.mg, osio.my, osio.mr]
	N = int(t_sec+0.5)
	n = N*10
	osio << "|" << flush
	for i in range(n):
		t = i*0.1		
		colour = colours[int(t/t_sec*(len(colours)))]
		if i % 10 == 0:
			osio << colour << " %1.0fs  " % t << flush
		else:
			osio << colour << "\b=>" << flush
		time.sleep(0.1)
	osio << colours[-1] << " %1.0fs |" % t_sec << endl
	osio.os_print_reset()

par = arg.ArgumentParser(description='CTP LITTLE HELPER')
par.add_argument('--gen', dest='gen', action='store_const', const=1, default=0)
par.add_argument('--cpy', dest='cpy', action='store_const', const=1, default=0)  
par.add_argument('--exe', dest='exe', action='store_const', const=1, default=0)
par.add_argument('--cln', dest='cln', action='store_const', const=1, default=0)
par.add_argument('--sub', dest='sub', action='store_const', const=1, default=0)
opts = par.parse_args()




RELATIVE_BASE 		= 'APE_ISO'
RELATIVE_WORKGROUND = 'WORKGROUND'
EWDBGPOL_FOLDER 	= 'EWDBGPOL'
MP_FILES			= 'MP_FILES'
JOBFILE				= 'jobs.ewald.xml'
PARTITION_JOBFILE	= True
ACCESS_LOC_JOBFILE	= True

n_threads 			= 16
n_procs				= n_threads
queue 				= 'PE_16'
t_job  				= 30.0/60.	# hours
T_wall 				= 36		# hours
t_comm 				= 1			# hours

votcarc 			= '/people/thnfs/homes/poelking/VOTCA_SUSE_12/bin/VOTCARC.csh'

#z_xx =  ['TEST']
#z_xx =  ['C60_ZNPC_S']
#z_xx = get_dirs('./', '^L..G_2D$')
z_xx = get_dirs('./', '^\d*K_confout')
z_xx = sorted(z_xx)
exclude = []

pres = [ z[:] for z in z_xx ]
n_jobs_total = 0
n_nodes_total = 0

for folder, pre in zip(z_xx, pres):	
	if folder in exclude: continue
	
	write_header(folder)
	os.chdir(folder)
	
	ROOT = os.path.abspath(os.getcwd())
	BASE = os.path.join(ROOT, RELATIVE_BASE)
	WORKGROUND = os.path.join(BASE, RELATIVE_WORKGROUND)
	
	print "Root = ", ROOT
	print "Base = ", BASE
	print "Work = ", WORKGROUND	
	
	
	# CLEAN IF APPLICABLE
	if opts.cln:
		safe_remove(BASE)
		
	# SUPPLY FROM SOURCE
	if opts.gen:
		
		# Base directory (local)
		safe_mkdir(BASE)
		os.chdir(BASE)
		print "Copy files to base directory"
		sql = os.path.join(ROOT, 'system.sql')
		job = os.path.join(ROOT, JOBFILE)
		os.system('cp %s .' % sql)
		os.system('cp %s jobs.xml' % job)
		
		# Work directory (local)
		safe_mkdir(WORKGROUND)
		os.chdir(WORKGROUND)
		print "Copy files to workground"
		sysxml = os.path.join(ROOT, 'system.xml')
		mpstable = os.path.join(ROOT, 'mps.tab')
		mpfiles = os.path.join(ROOT, MP_FILES)
		ptop = os.path.join(ROOT, '%s/bgp_main.ptop' % EWDBGPOL_FOLDER)
		
		os.system('cp %s .' % sysxml)
		os.system('cp %s .' % mpstable)
		os.system('cp -r %s MP_FILES' % mpfiles)
		if os.path.exists(ptop):
			os.system('cp %s .' % ptop)
			polar_bg = 'bgp_main.ptop'
		else:
			print "No background polarization available, set ptop = ''"
			polar_bg = ''
		
		# Absolute paths to input files
		abs_jobxml = os.path.join(BASE, 'jobs.xml')
		abs_sql = os.path.join(BASE, 'system.sql')
		
		abs_jobxml_shared_nonloc = abs_jobxml
		abs_sql_shared_nonloc = abs_sql
		
		# Calcatulate number of jobs / node and number of nodes
		n_jobs = count_jobs(abs_jobxml)
		n_jobs_total += n_jobs
		
		jobs_per_thread  = int(T_wall/t_job)
		jobs_per_machine = int(n_procs*T_wall/t_job)
		
		n_nodes = int(n_jobs / jobs_per_machine) + (1 if n_jobs % jobs_per_machine > 0 else 0)
		n_nodes_total += n_nodes
		
		# Distribute overhang equally
		jobs_per_machine = int(n_jobs/n_nodes)+1
		jobs_cache = int(n_procs*t_comm/t_job)
		
		
		# PARTITION JOBFILES IF APPLICABLE
		jobfiles = []		
		if PARTITION_JOBFILE:
			tree = XmlTree(abs_jobxml)
			jobs = tree.GetAll('job')
			job_idx = -1
			for i in range(n_nodes):
				jobfile = 'jobs.%d.xml' % (i+1)
				root = etree.Element('jobs')
				for j in range(jobs_per_machine):
					job_idx += 1
					if job_idx == len(jobs):
						break
					root.append(jobs[job_idx].node)					
				ofs = open(jobfile, 'w')
				ofs.write(etree.tostring(root, pretty_print=True))
				ofs.close()
				
				if ACCESS_LOC_JOBFILE:
					pass
				else:
					jobfile = os.path.abspath(jobfile)
				jobfiles.append(jobfile)
		else:
			jobfiles = [ abs_jobxml for i in range(n_nodes) ]		
			
		# Options
		print "Generate options"
		
		for i in range(n_nodes):
			write_pewald3d_options(
				filename='options.%d.xml' % (i+1),
				job_file=jobfiles[i],
				mapping='system.xml',
				mps_table='mps.tab',
				polar_bg=polar_bg,
				pdb_check=0,
				ewald_cutoff=8,
				shape='none',
				save_nblist='false',
				induce=1,
				thole_cutoff=3,
				thole_tolerance=0.001,
				calculate_fields='true',
				polarize_fg='true',
				evaluate_energy='true',
				cg_background='false',
				cg_foreground='false',
				cg_radius=3,
				cg_anisotropic='true',
				energy=1e-5,
				kfactor=100,
				rfactor=6)
			if i == 0:
				options_writer_toggle_verbose()	
				print "... options.?.xml ..."
		options_writer_toggle_verbose()	
			
		# Generate commmand
		print "Generate command"
		
		cmd_dict = {\
			'exe'   : 'ctp_parallel',
			'calc'  : 'pewald3d',
			'sql' 	: abs_sql_shared_nonloc,
			'job'   : abs_jobxml_shared_nonloc,
			'map'   : 'system.xml',
			'opt'   : 'options.{ID:d}.xml',
			'n_thd' : n_threads,
			'cache' : jobs_cache,
			'max'   : jobs_per_machine,
			'log' 	: 'ctp_{ID:02d}.log'}
		cmd = '{exe} -e {calc} -o {opt} -f {sql} -s 0 -t {n_thd} -c {cache} -m {max} >& {log}'.format(**cmd_dict)		
		
		# Generate batch files
		tag = pre.upper()+'_{ID:02d}_PEWD3D'
		print "Tag", tag
		print "Cmd", cmd
		print "{0} jobs => {1} nodes @ {2} jobs per node, cache {3}, max {4}".format(n_jobs, n_nodes, jobs_per_machine, jobs_cache, jobs_per_machine)
		batch_files = multi_write_cluster_batch(n=n_nodes, command=cmd, tag=tag, queue=queue, source=False,module=['gaussian/g03','votca/icc_cluster'], procs=n_procs)
		
		if opts.sub:	
			for batch in batch_files:
				os.system('qsub %s' % batch)
				if PARTITION_JOBFILE:
					time.sleep(1)
					continue
				elif batch == batch_files[-1]:
					pass
				else:
					time.sleep(60)
		os.chdir(ROOT)
	
	os.chdir('../')

print "N(jobs,total)  =", n_jobs_total
print "N(nodes,total) =", n_nodes_total

sys.exit(0)
