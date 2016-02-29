from __pyosshell__ import *
from __molecules__ import *
from __qmshell__   import *


def ctp_map_auto(sql='state.sql', xml='system.xml', md_files='MD_FILES'):
	abort = False
	ext_dict = dict_by_ext(md_files)	
	# MD COORDINATE + TOPOLOGY FILE
	try:
		tpr = ext_dict['tpr']
	except KeyError:
		tpr = '?'
		print "ERROR No topology (.tpr) file in %s/%s" % (os.getcwd(), md_files)
		abort = True
	try:
		gro = ext_dict['gro']
	except KeyError:
		try:
			gro = ext_dict['pdb']
		except KeyError:
			gro = '?'
			print "ERROR No coordinate file in %s/%s" % (os.getcwd(), md_files)
			abort = True
	# DATABASE + MAPPING FILE
	if sql in os.listdir('./'):
		print "ERROR SQL-file '%s' already exists, will abort." % sql
		abort = True
	if not xml in os.listdir('./'):
		print "ERROR XML-file '%s' missing, will abort." % xml
		abort = True	
	# EXECUTE	
	opts = '-c %s -t %s -s %s -f %s' % (gro, tpr, xml, sql)
	print 'ctp_map %s' % (opts)	
	if abort: sys.exit(1)
	os.system('ctp_map %s' % opts)
	return



def WriteSystemXml(name, gro, xyz, xml = 'system.xml'):
	mol = SingleMoleculeFromGro(gro)[0]
	mol.fragment()
	mol.make_dict()
	mol.name = name
	es,xyz = e_xyz_from_xyz(xyz)
	# CHECK CONGRUENCY
	for atm, e, xyz in zip(mol.atoms,es,xyz):
		print atm.fragName, atm.name, "=>", e, xyz
		assert atm.name[0:1] == e or atm.name[0:2].lower() == e.lower()	
	ofs = open(xml,'w')
	# MOLECULE HEADER
	ofs.write('<topology>\n')
	ofs.write('\t<molecules>\n')
	ofs.write('\t<molecule>\n')
	ofs.write('\t\t<name>%s</name>\n' % mol.name)
	ofs.write('\t\t<mdname>%s</mdname>\n' % mol.name)
	ofs.write('\t\t<segments>\n')
	# SEGMENT HEADER
	ofs.write('\t\t<segment>\n')
	ofs.write('\t\t\t<name>%s</name>\n' % mol.name)
	# XYZ FILE
	ofs.write('\t\t\t<qmcoords>QC_FILES/%s.xyz</qmcoords>\n' % mol.name)
	# MPS FILES
	ofs.write('\t\t\t<multipoles_n>MP_FILES/%s_n.mps</multipoles_n>\n' % (mol.name))
	ofs.write('\t\t\t<multipoles_h>MP_FILES/%s_h.mps</multipoles_h>\n' % (mol.name))
	ofs.write('\t\t\t<multipoles_e>MP_FILES/%s_e.mps</multipoles_e>\n' % (mol.name))
	ofs.write('\t\t\t<map2md>0</map2md>\n')
	# FRAGMENTS
	ofs.write('\t\t\t<fragments>\n')	
	for frag in mol.frags:
		# FRAGMENT HEADER
		fragName = '%s%d' % (frag.name,mol.frags.index(frag))
		ofs.write('\t\t\t<fragment>\n')
		ofs.write('\t\t\t\t<name>%s</name>\n' % fragName)
		# MD-ATOMS		
		mdatoms = ''
		for atom in frag.atoms:
			mdatoms += ' %d:%s:%s ' % (atom.fragId, atom.fragName, atom.name)
		ofs.write('\t\t\t\t<mdatoms>%s</mdatoms>\n' % mdatoms)
		# QM-ATOMS, M-POLES, WEIGHTS
		qmatoms = ''
		weights = ''
		ms = { 'H' : 1, 'C' : 12, 'N' : 14, 'O' : 16, 'S' : 35 }
		for atom in frag.atoms:
			idx = mol.atoms.index(atom)
			typ = es[idx]
			qmatoms += ' %d:%s       ' % (atom.Id,typ)
			weights += ' %d         ' % ms[typ]
		ofs.write('\t\t\t\t<qmatoms>%s</qmatoms>\n' % qmatoms)
		ofs.write('\t\t\t\t<mpoles> %s</mpoles>\n' % qmatoms)
		ofs.write('\t\t\t\t<weights>%s</weights>\n' % weights)
		# LOCAL FRAME
		localframe = ''
		count_atoms = 0
		for atom in frag.atoms:
			if count_atoms == 3: break
			
			idx = mol.atoms.index(atom)
			typ = es[idx]
			if typ != 'H':
				count_atoms += 1
				localframe += ' %d ' % atom.Id
		ofs.write('\t\t\t\t<localframe>%s</localframe>\n' % localframe)
		ofs.write('\t\t\t</fragment>\n')
	# CLOSING TAGS
	ofs.write('\t\t\t</fragments>\n')
	ofs.write('\t\t</segment>\n')
	ofs.write('\t\t</segments>\n')
	ofs.write('\t</molecule>\n')
	ofs.write('\t</molecules>\n')
	ofs.write('</topology>\n')	
	ofs.close()
	return


