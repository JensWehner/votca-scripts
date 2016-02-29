from __proptions__ import *
from __molecules__ import *



GROFILE = 'planar.gro'
TOPFILE = 'DCV5T_ME3.itp'





mol,box = SingleMoleculeFromGro(GROFILE)
bonds = sect_from_bracket_file(TOPFILE,'bonds')
pairs = sect_from_bracket_file(TOPFILE,'pairs')
angles = sect_from_bracket_file(TOPFILE,'angles')
impropers = sect_from_bracket_file(TOPFILE,'dihedrals')
propers = sect_from_bracket_file(TOPFILE,'dihedrals_imp')


outt = open('potentials.xyz','w')

for bond in bonds:
	break
	idx1 = int(bond[0])
	idx2 = int(bond[1])
	
	atm1 = mol.atoms[idx1-1]
	atm2 = mol.atoms[idx2-1]
	atm3 = atm1
	atm4 = atm2
	
	outt.write('4\n')
	outt.write('Bond\n')
	outt.write('R %4.7f %4.7f %4.7f\n' % (atm1.pos[0]*10,atm1.pos[1]*10,atm1.pos[2]*10))
	outt.write('R %4.7f %4.7f %4.7f\n' % (atm2.pos[0]*10,atm2.pos[1]*10,atm2.pos[2]*10))
	outt.write('R %4.7f %4.7f %4.7f\n' % (atm3.pos[0]*10,atm3.pos[1]*10,atm3.pos[2]*10))
	outt.write('R %4.7f %4.7f %4.7f\n' % (atm4.pos[0]*10,atm4.pos[1]*10,atm4.pos[2]*10))


for pair in pairs:
	break
	idx1 = int(pair[0])
	idx2 = int(pair[1])
	
	atm1 = mol.atoms[idx1-1]
	atm2 = mol.atoms[idx2-1]
	atm3 = atm1
	atm4 = atm2
	
	outt.write('4\n')
	outt.write('Bond\n')
	outt.write('R %4.7f %4.7f %4.7f\n' % (atm1.pos[0]*10,atm1.pos[1]*10,atm1.pos[2]*10))
	outt.write('R %4.7f %4.7f %4.7f\n' % (atm2.pos[0]*10,atm2.pos[1]*10,atm2.pos[2]*10))
	outt.write('R %4.7f %4.7f %4.7f\n' % (atm3.pos[0]*10,atm3.pos[1]*10,atm3.pos[2]*10))
	outt.write('R %4.7f %4.7f %4.7f\n' % (atm4.pos[0]*10,atm4.pos[1]*10,atm4.pos[2]*10))

for angle in angles:
	break
	idx1 = int(angle[0])
	idx2 = int(angle[1])
	idx3 = int(angle[2])
	
	atm1 = mol.atoms[idx1-1]
	atm2 = mol.atoms[idx2-1]
	atm3 = mol.atoms[idx3-1]
	atm4 = atm1
	
	outt.write('4\n')
	outt.write('Bond\n')
	outt.write('R %4.7f %4.7f %4.7f\n' % (atm1.pos[0]*10,atm1.pos[1]*10,atm1.pos[2]*10))
	outt.write('R %4.7f %4.7f %4.7f\n' % (atm2.pos[0]*10,atm2.pos[1]*10,atm2.pos[2]*10))
	outt.write('R %4.7f %4.7f %4.7f\n' % (atm3.pos[0]*10,atm3.pos[1]*10,atm3.pos[2]*10))
	outt.write('R %4.7f %4.7f %4.7f\n' % (atm4.pos[0]*10,atm4.pos[1]*10,atm4.pos[2]*10))

for dih in impropers:

	idx1 = int(dih[0])
	idx2 = int(dih[1])
	idx3 = int(dih[2])
	idx4 = int(dih[3])
	
	atm1 = mol.atoms[idx1-1]
	atm2 = mol.atoms[idx2-1]
	atm3 = mol.atoms[idx3-1]
	atm4 = mol.atoms[idx4-1]
	
	outt.write('4\n')
	outt.write('Bond\n')
	outt.write('R %4.7f %4.7f %4.7f\n' % (atm1.pos[0]*10,atm1.pos[1]*10,atm1.pos[2]*10))
	outt.write('R %4.7f %4.7f %4.7f\n' % (atm2.pos[0]*10,atm2.pos[1]*10,atm2.pos[2]*10))
	outt.write('R %4.7f %4.7f %4.7f\n' % (atm3.pos[0]*10,atm3.pos[1]*10,atm3.pos[2]*10))
	outt.write('R %4.7f %4.7f %4.7f\n' % (atm4.pos[0]*10,atm4.pos[1]*10,atm4.pos[2]*10))
	
for dih in propers:
	break
	idx1 = int(dih[0])
	idx2 = int(dih[1])
	idx3 = int(dih[2])
	idx4 = int(dih[3])
	
	atm1 = mol.atoms[idx1-1]
	atm2 = mol.atoms[idx2-1]
	atm3 = mol.atoms[idx3-1]
	atm4 = mol.atoms[idx4-1]
	
	outt.write('4\n')
	outt.write('Bond\n')
	outt.write('R %4.7f %4.7f %4.7f\n' % (atm1.pos[0]*10,atm1.pos[1]*10,atm1.pos[2]*10))
	outt.write('R %4.7f %4.7f %4.7f\n' % (atm2.pos[0]*10,atm2.pos[1]*10,atm2.pos[2]*10))
	outt.write('R %4.7f %4.7f %4.7f\n' % (atm3.pos[0]*10,atm3.pos[1]*10,atm3.pos[2]*10))
	outt.write('R %4.7f %4.7f %4.7f\n' % (atm4.pos[0]*10,atm4.pos[1]*10,atm4.pos[2]*10))


outt.close()





outt = open('vis.tcl','w')

outt.write('mol new conf.gro\n')
outt.write('mol new potentials.xyz\n')

outt.close()
	
	






