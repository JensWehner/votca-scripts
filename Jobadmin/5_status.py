#! /usr/bin/env python
from __pyosshell__ import *
from ctp__options__ import *
from ctp__cluster__ import *
from ctp__jobfile__ import *
from momo import osio, endl

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
	height, width = os.popen('stty size', 'r').read().split()
	width = int(width)
	leftright = int((width - len(title)-2)/2)
	print "="*leftright, title, "="*leftright
	return


par = arg.ArgumentParser(description='CTP LITTLE HELPER')
par.add_argument('--gen', dest='gen', action='store_const', const=1, default=0)    
par.add_argument('--exe', dest='exe', action='store_const', const=1, default=0)
par.add_argument('--cln', dest='cln', action='store_const', const=1, default=0)
par.add_argument('--sub', dest='sub', action='store_const', const=1, default=0)
opts = par.parse_args()
z_xx = get_dirs('./', '^\d*K_confout')
z_xx.sort()
bases = ['PEWALD3D']

for sysfolder in z_xx:
	os.chdir(sysfolder)	
	for base in bases:
		os.chdir(base)		
		jobfile = 'jobs.xml'
		jobfile_back = 'jobs.xml.back'
		osio >> 'cp %s %s' % (jobfile, jobfile_back)
		nt, nav, nas, nfl, ncp = jobfile_info(jobfile_back)

		colour = osio.mg if nt == ncp else osio.my
		osio << colour << "Status: {sys:20s} {ncp:3d} / {nt:3d}    ({nav:3d}, {nas:3d}, {nfl:3d}, {ncp:3d})".format(sys=sysfolder, nt=nt, nav=nav, nas=nas, nfl=nfl, ncp=ncp) << endl
		os.chdir('../')
	os.chdir('../')

sys.exit(0)
