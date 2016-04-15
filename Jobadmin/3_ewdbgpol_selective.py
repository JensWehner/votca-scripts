#! /usr/bin/env python
from __pyosshell__ import *
from ctp__options__ import *
from ctp__cluster__ import *
from momo import osio

par = arg.ArgumentParser(description='CTP HELPER')
par.add_argument('--gen', dest='gen', action='store_const', const=1, default=0)    
par.add_argument('--exe', dest='exe', action='store_const', const=1, default=0)
par.add_argument('--cln', dest='cln', action='store_const', const=1, default=0)
par.add_argument('--loc', dest='loc', action='store_const', const=1, default=0)
par.add_argument('--sub', dest='sub', action='store_const', const=1, default=0)
par.add_argument('--chk', dest='chk', action='store_const', const=1, default=0)
opts = par.parse_args()

z_xx = get_dirs('./', '^\d*K_confout')
#z_xx = ['COR_DPBIC']
z_xx.sort()

queue = 'PE_16'
n_procs = 16
n_threads = 16
workground = 'EWDBGPOL'

root = osio.cwd()

pres = [ 'Q'+z[4:] for z in z_xx ]

for folder,pre in zip(z_xx, pres):	
	
	print "="*40, folder, "="*40
	os.chdir(folder)
	
	# CLEAN IF APPLICABLE
	if opts.cln:
		os.system('rm -rf %s' % workground)
		
	# SUPPLY FROM SOURCE
	if opts.gen:
		os.system('mkdir -p %s' % workground)
		os.chdir(workground)
		print "Copy files ..."
		os.system('cp -r ../MP_FILES .')
		os.system('cp ../system.xml ../mps.tab .')
		os.system('cp ../system.sql .')
		print "Generate options ..."
		write_ewdbgpol_options(
			filename='options.xml',
			multipoles='system.xml',
			mps_table='mps.tab',
			pdb_check=1,
			ewald_cutoff=6,
			shape='none',
			dipole_corr='false',
			induce=1,
			thole_cutoff=0,
			energy=1e-5,
			kfactor=100,
			rfactor=6)
		os.chdir('../')
	
	# GENERATE MPS TABLE
	if opts.exe:
		os.chdir(workground)
		if opts.loc:
			cmd = 'ctp_run -e ewdbgpol -o options.xml -f system.sql -t 4 -s 0'
			os.system(cmd)
		else:
			cmd = 'ctp_run -e ewdbgpol -o options.xml -f system.sql -t {th:d} -s 0 >& ctp.log'.format(th=n_threads)
			tag = pre.upper() + "_EWDBGPOL"
			batch = write_cluster_batch(cmd, tag, procs=n_procs, queue=queue,module=["gaussian/g03","votca/icc_cluster"],source=False)
			if opts.sub:
				os.system('qsub %s' % batch)	
		os.chdir('../')

	# READ & PROCESS PTOP-FILE
	if opts.chk:
		os.chdir(workground)
		os.system('mkdir -p READ_PTOP')
		os.chdir('READ_PTOP')
		if 'bgp_main.ptop' in os.listdir('./'):
			os.system('rm bgp_main.ptop')
		os.system('ln -s ../bgp_main.ptop .')
		write_ptopreader_options(ptop_file='bgp_main.ptop')
		cmd = 'ctp_tools -e ptopreader -o options.xml'
		outfile = 'bgp_main.ptop.tab'
		target = 'segs_{0}.tab'.format(folder.lower())
		os.system(cmd)
		os.system('cat {out} | grep sxyz > {tar}'.format(out=outfile, tar=target))
		collect_folder = os.path.join(root, 'ANALYSE_EWDBGPOL')
		os.system('cp {tar} {col}/.'.format(tar=target, col=collect_folder))	
		os.chdir('../')
		os.chdir('../')
		
	os.chdir('../')

sys.exit(0)
