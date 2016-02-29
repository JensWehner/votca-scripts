import sys
import os


# =============================================================================
# CONVENIENCE FUNCTIONS & CLASSES FOR SHELL EXECUTABLES
# =============================================================================

def okquit(what=''):
	if what != '': print what
	sys.exit(0)
def xxquit(what=''):
	if what != '':
		cprint.Error("ERROR: {what}".format(what=what))
	sys.exit(1)
def sysexe(cmd, silent=False, devfile='/dev/null'):
	if VERBOSE: print "{0}@{1}$ {2}".format(USER, HOST, cmd)
	if silent: cmd += ' >> {0} 2>> {0}'.format(devfile)
	cdx = os.system(cmd)
	#SYSCMDS.write('{cmd} = {cdx}\n'.format(cmd=cmd, cdx=cdx))
	return cdx

def nnprint(msg):
	print "{0:100s} {1}".format(msg, cprint.NN)
def okprint(msg):
	print "{0:100s} {1}".format(msg[0:97], cprint.OK)
def xxprint(msg):
	print "{0:100s} {1}".format(msg, cprint.XX)

def isfloat(item):
	try: float(item); return True
	except: return False
def xmlsplit(string, regex='<|>|/| '):
	return re.split(regex, string)

class CPrint(object):
	def __init__(self):
		self.HEADER = '\033[95m'
		self.OKBLUE = '\033[34m'
		self.LBLUE = '\033[1;34m'
		self.YELLOW = '\033[1;33m'
		self.GREEN = '\033[92m'
		self.WARNING = '\033[93m'
		self.ERROR = '\033[95m'
		self.MAGENTA = '\033[95m'
		self.RED = '\033[91m'
		self.ENDC = '\033[0;1m'
		self.OK = self.GREEN + 'OK' + self.ENDC
		self.XX = self.RED + 'XX' + self.ENDC
		self.NN = self.WARNING + ':/' + self.ENDC
	def Head(self, msg):
		print self.YELLOW+msg+self.ENDC
	def Error(self, msg):
		print self.ERROR+msg+self.ENDC
	def Green(self, msg):
		return self.GREEN+msg+self.ENDC
	def Red(self, msg):
		return self.ERROR+msg+self.ENDC
	def Headerlike(self, msg):
		return self.LBLUE+msg+self.ENDC
	def Yellow(self, msg):
		return self.YELLOW+msg+self.ENDC




