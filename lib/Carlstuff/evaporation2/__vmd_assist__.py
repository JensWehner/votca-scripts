

class SystemVMD(object):
	def __init__(self):
		self.reps = []
	def AddRep(self,
			   modselect = "all", 
	           modcolor = "name", 
	           modstyle = "lines",
	           modmaterial = "Opaque"):
		if len(self.reps): addrep = True
		else: addrep = False # Use default rep
		ID = len(self.reps)
		self.reps.append(RepVMD(ID, 
		                        modselect, 
		                        modcolor, 
		                        modstyle,
		                        modmaterial, 
		                        addrep))
		return
	def ToTCL(self,outt):
		for rep in self.reps:
			rep.ToTCL(outt)
		return

class RepVMD(object):
	def __init__(self, ID = 0, modselect = "all", 
	                           modcolor = "name", 
	                           modstyle = "lines", 
	                           modmaterial = "Opaque",
	                           addrep = True):
		self.ID				= ID
		self.modselect		= modselect
		self.modcolor		= modcolor
		self.modstyle		= modstyle
		self.modmaterial 	= modmaterial
		self.add			= addrep
	def ToTCL(self, outt):
		if self.add:
			outt.write('mol addrep top\n')
		outt.write('mol modselect %d top %s\n' % (self.ID, self.modselect))
		outt.write('mol modcolor %d top %s\n' % (self.ID, self.modcolor))
		outt.write('mol modstyle %d top %s\n' % (self.ID, self.modstyle))
		outt.write('mol modmaterial %d top %s\n' % (self.ID, self.modmaterial))
		return




