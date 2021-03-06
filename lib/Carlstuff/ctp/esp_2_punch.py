from __future__ import division
import numpy as np

infiles = []
xyzfiles = []
outfiles = []
scales = []

xyzfiles.append('dcv5t.xyz')
infiles.append('dcv5t_n.esp')
outfiles.append('dcv5t_n.mps')
scales.append(2)

xyzfiles.append('dcv5t.xyz')
infiles.append('dcv5t_h.esp')
outfiles.append('dcv5t_h.mps')
scales.append(2.7)

xyzfiles.append('dcv5t.xyz')
infiles.append('dcv5t_e.esp')
outfiles.append('dcv5t_e.mps')
scales.append(2.7)

"""
xyzfiles.append('C60.xyz')
infiles.append('C60_neutr.esp')
outfiles.append('C60_N.punch')
scales.append(2)

xyzfiles.append('C60.xyz')
infiles.append('C60_catio.esp')
outfiles.append('C60_C.punch')
scales.append(2.7)

xyzfiles.append('C60.xyz')
infiles.append('C60_anion.esp')
outfiles.append('C60_A.punch')
scales.append(2.7)
"""


P1 = {}
P1['H'] = 0.496
P1['C'] = 1.334
P1['N'] = 1.073
P1['O'] = 0.837
P1['S'] = 2.926

class PolarSite(object):
	def __init__(self, name, pos = np.array([0,0,0]), chrg = None, scale = 1):
		self.name = name
		self.pos = pos
		self.chrg = chrg
		self.pol = self.find_polarity(scale)
		
	def find_polarity(self, scale):
	
		global P1
		
		if self.name == 'H':
			pol = P1['H']
		else:
			pol = P1[self.name] * scale
			
		return pol
		
		
		

def sites_from_esp_xyz(espfile, xyzfile, scale):
	intt = open(espfile, 'r')
	
	poles = []
	for ln in intt.readlines():
		
		ln = ln.split()
		if ln == []:
			continue
		
		
		name = ln[1]
		chrg = float(ln[2])
		
		poles.append(PolarSite(name, np.array([0,0,0]), chrg, scale))
		
	intt.close()
	
	
	intt = open(xyzfile, 'r')
	count = -1
	for ln in intt.readlines():
		
		ln = ln.split()
		if ln == []:
			continue
		
		if len(ln) < 4:
			continue
		
		count += 1
		
		x = float(ln[1])
		y = float(ln[2])
		z = float(ln[3])
		
		assert ln[0] == poles[count].name
		
		poles[count].pos = np.array([x,y,z])
		
	
	intt.close()
	
	return poles
	
	
	
def poles_to_punch(outfile, poles):
	outt = open(outfile, 'w')
	
	outt.write('! PUNCHFILE GENERATED BY ESP_2_PUNCH.PY \n')
	outt.write('! INPUT FOR VOTCA::CTP::EMULTIPOLE \n')
	outt.write('Units angstrom \n')
	
	for pole in poles:
		outt.write('%3s %4.7f %4.7f %4.7f Rank 0 \n' % (pole.name, pole.pos[0], pole.pos[1], pole.pos[2]))
		outt.write('    %1.7f \n' % (pole.chrg))
		outt.write('    P %1.7f \n' % (pole.pol))
	
	outt.close()
	


for i in range(len(infiles)):
	poles = sites_from_esp_xyz(infiles[i], xyzfiles[i], scales[i])
	poles_to_punch(outfiles[i], poles)



	

		
		
