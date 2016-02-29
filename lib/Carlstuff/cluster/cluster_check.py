import commands as cmds
import os

def write_header(title):
    try:
        height, width = os.popen('stty size', 'r').read().split()
        width = int(width)
        leftright = int((width - len(title)-2)/2)
    except ValueError:
        leftright = 40
    print "="*leftright, title, "="*leftright
    return


class Job(object):
	def __init__(self, qstat_line):
		self.qstat = qstat_line.split()
		self.user = self.qstat[3]
		self.tag = self.qstat[2]
		self.status = self.qstat[4]
		self.machine = self.qstat[7].split('@')[1].split('.')[0]
	def __str__(self):
		return "%-20s %-10s" % (self.tag, self.machine)
	def Check(self, cmd=''):
		if 'rm' in cmd: assert False
		home = os.path.abspath(os.getcwd())
		work = '/scratch/{mach:s}/{user:s}/job_0/'.format(mach=self.machine, user=self.user)
		os.chdir(work)
		if cmd != '': out = os.popen(cmd).readlines() # out = cmds.getoutput(cmd)
		print out
		os.chdir(home)
	def ChecksAndBalances(self, do_fct):
		home = os.path.abspath(os.getcwd())
		work = '/scratch/{mach:s}/{user:s}/job_0/'.format(mach=self.machine, user=self.user)
		os.chdir(work)
		do_fct()	
		os.chdir(home)


class Do(object):
	def __init__(self, **kwargs):
		self.args = kwargs
	def __call__(self):
		files = os.listdir('./')
		"""
		for f in files:
			if 'ctp_' in f and '.log' in f:	
				print f
				time_lns = []
				ifs = open(f, 'r')
				for ln in ifs.readlines():
					if 'Timing' in ln:
						#print ln[:-1]
						time_lns.append(ln)
				print "=>", len(time_lns)
				ifs.close()
		"""
		
		if 'ctp.log' in files:
			os.system('cat ctp.log | grep started')
		return
		



# EXECUTE QSTAT & GENERATE JOBS
qstat = cmds.getoutput('qstat')
qstat = qstat.split('\n')
# Pop header
for i in range(2): qstat.pop(0)
# Load job data
jobs = []
for q in qstat:
	job = Job(q)
	jobs.append(job)

# CHECKS AND BALANCES
for job in jobs:
	write_header(str(job))
	do = Do()
	job.ChecksAndBalances(do)





