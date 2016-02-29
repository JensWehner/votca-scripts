from __future__ import division
import numpy as np


infile1 = 'segment_3.pdb'
infile2 = 'DCV2T.punch'
outfile = 'Seg4_' + infile2

ANGSTROM2BOHR = 1 / 0.529189379

class Atom(object):
	def __init__(self, rsdno, rsdname, atmno, atmname, pos):
		self.pos = pos
		self.atmname = atmname
		
		
class PSite(object):
	def __init__(self, name, pos, rank, Qs):
		self.name = name
		self.pos = pos
		self.rank = rank
		self.Qs = Qs
		
	def write_to_file(self, outt):
		outt.write(self.name + ' ' + str(self.pos[0]) + ' ' + str(self.pos[1]) + ' ' * str(self.pos[2]) + ' ')
		outt.write('Rank   ' + str(self.rank))
		outt.write('\n')
		
		outt.write(Qs[0] + ' \n')
		outt.write(Qs[1] + ' ' + Qs[2] + ' ' + Qs[3] + ' \n')
		outt.write(Qs[4] + ' ' + Qs[5] + ' ' + Qs[6] + ' ' + Qs[7] + ' ' + Qs[8] + ' \n')
		

def read_pdb_ln(ln):

	if ln[0:4] != 'ATOM' and ln[0:6] != 'HETATM':
		# print ".",
		return None, None, None, None, None
	
	try:
		atmname    = ln[13:16]
		atmname = atmname.strip()
		atmno      = int(ln[6:11])
		rsdname    = ln[17:20]
		rsdname = rsdname.strip()
		rsdno      = int( ln[22:26] )
		x   = float( ln[30:38] )
		y   = float( ln[38:46] )
		z   = float( ln[46:54] )
		return rsdno, rsdname, atmno, atmname, np.array( [x,y,z] )
		
	except ValueError:
		print 'PDB PARSING ERROR'
		print ln
		assert False
		

# Load atoms and correct for CoM
intt = open(infile1, 'r')

atoms = []
for ln in intt.readlines():
	
	rsdno, rsdname, atmno, atmname, pos = read_pdb_ln(ln)
	
	atmname = atmname[0:1]
	pos = pos * ANGSTROM2BOHR
	atoms.append(Atom(rsdno, rsdname, atmno, atmname, pos))


com = np.array([0,0,0])
N = 0
for atom in atoms:
	com = com + atom.pos
	N = N + 1

com = com / N
for atom in atoms:
	atom.pos = atom.pos - com
	
intt.close()	



# Load polar sites from GDMA file
intt = open(infile2, 'r')

psites = []
for ln in intt.readlines():
	
	ln = ln.split()
	
	if ln == []:
		continue
	
	if ln[0] == '!' or ln[0][0] == '!':
		continue
	
	if ln[4] == 'Rank':
		psites.append(PSite(ln[0], None, int(ln[5]), []))
	
	else:
		for i in range(len(ln)):
			psites[-1].Qs.append(ln[i])
			
intt.close()


assert len(atoms) == len(psites)

# Copy positions from atoms to polar sites
for i in range(len(atoms)):
	psites[i].pos = atoms[i].pos





# Write polar sites to file

outt = open(outfile, 'w')

outt.write('! ' + infile1 + '+' + infile2 + '=>' + outfile + ' \n')
outt.write('Units bohr \n')

for psite in psites:
	psite.write_to_file(outt)

outt.close()
 
	





		
	
	




	
	
	
		
	 


