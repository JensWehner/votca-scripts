from __molecules__ import *

class FrameStack(object):
	
	def __init__(self, trj = 'traj.xtc',  tpr = 'topol.tpr', 
	                   top = 'system.top', t_0 = 0, t_1 = 0, 
	                   dt = 1, opt = '-pbc mol -ur tric',
	                   dev = '> /dev/null 2> /dev/null', grp = "0"):
		
		self.trj = trj
		self.tpr = tpr
		self.top = top
		self.t_0 = t_0
		self.t_1 = t_1
		self.opt = opt
		self.dev = dev
		self.grp = grp
		
		self.t   = t_0
		self.dt  = dt
		self.pop = None
	
	def NextFrame(self, fragment = True, make_dict = True):
		
		if not self.HasMoreFrames():
			return None
		
		if 'stack.gro' in os.listdir('./'):
			os.system('rm stack.gro')
		sig = os.system('echo %1s | trjconv -f %1s -s %1s -o stack.gro %1s -b %1d -e %1d %1s' \
		                    % (self.grp,self.trj, self.tpr, self.opt, self.t, self.t,self.dev))
		if sig:
			print "Error in trjconv - early return"
			self.t = t_1 + d_t
			return
			
		del self.pop
		self.pop = Population('stack.gro',self.top,False)
		self.t += self.dt
		
		if fragment:
			self.pop.fragment()
		if make_dict:
			self.pop.make_dict()
			
		return self.pop
	
	def ImportSingle(self, grofile = 'system.gro', topfile = 'system.top', fragment = True, make_dict = True):
		
		del self.pop
		self.pop = Population(grofile,topfile)
		
		if fragment:
			self.pop.fragment()
		if make_dict:
			self.pop.make_dict()
			
		return self.pop		
	
	def HasMoreFrames(self):
		if self.t > self.t_1:
			return False
		else:
			return True
	
	def PrintInfo(self):
		print "Population at t = %1d: %1d molecules, %1d atoms" \
		        % (self.pop.t, self.pop.mol_count(), self.pop.atom_count())


