from __pyosshell__ import *
from __molecules__ import *
from __qmshell__   import *
import xml.dom.minidom as xml


def WriteSystemXml(name,gro,xyz,xml = 'system.xml'):
	mol = SingleMoleculeFromGro(gro)[0]
	mol.fragment()
	mol.make_dict()
	mol.name = name
	es,xyz = e_xyz_from_xyz(xyz)
	# CHECK CONGRUENCY
	for atm, e, xyz in zip(mol.atoms,es,xyz):
		print atm.fragName, atm.name, "=>", e, xyz
		assert atm.name[0:1] == e or atm.name[0:2].lower() == e.lower()	
	outt = open(xml,'w')
	# MOLECULE HEADER
	outt.write('<topology>\n')
	outt.write('\t<molecules>\n')
	outt.write('\t<molecule>\n')
	outt.write('\t\t<name>%s</name>\n' % mol.name)
	outt.write('\t\t<mdname>%s</mdname>\n' % mol.name)
	outt.write('\t\t<segments>\n')
	# SEGMENT HEADER
	outt.write('\t\t<segment>\n')
	outt.write('\t\t\t<name>%s</name>\n' % mol.name)
	# XYZ FILE
	outt.write('\t\t\t<qmcoords>QC_FILES/%s.xyz</qmcoords>\n' % mol.name)
	# MPS FILES
	outt.write('\t\t\t<multipoles_n>MP_FILES/%s_n.mps</multipoles_n>\n' % (mol.name))
	outt.write('\t\t\t<multipoles_h>MP_FILES/%s_h.mps</multipoles_h>\n' % (mol.name))
	outt.write('\t\t\t<multipoles_e>MP_FILES/%s_e.mps</multipoles_e>\n' % (mol.name))
	outt.write('\t\t\t<map2md>0</map2md>\n')
	# FRAGMENTS
	outt.write('\t\t\t<fragments>\n')	
	for frag in mol.frags:
		# FRAGMENT HEADER
		fragName = '%s%d' % (frag.name,mol.frags.index(frag))
		outt.write('\t\t\t<fragment>\n')
		outt.write('\t\t\t\t<name>%s</name>\n' % fragName)
		# MD-ATOMS		
		mdatoms = ''
		for atom in frag.atoms:
			mdatoms += ' %-11s ' % ('%d:%s:%s' % (atom.fragId, atom.fragName, atom.name))
		outt.write('\t\t\t\t<mdatoms>%s</mdatoms>\n' % mdatoms)
		# QM-ATOMS, M-POLES, WEIGHTS
		qmatoms = ''
		weights = ''
		ms = { 'H' : 1, 'C' : 12, 'N' : 14, 'O' : 16, 'S' : 32, 'Zn' : 65 }
		for atom in frag.atoms:
			idx = mol.atoms.index(atom)
			typ = es[idx]
			qmatoms += ' %-11s ' % ('%d:%s' % (atom.Id,typ))
			weights += ' %-11s ' % ('%d' % ms[typ])
		outt.write('\t\t\t\t<qmatoms>%s</qmatoms>\n' % qmatoms)
		outt.write('\t\t\t\t<mpoles> %s</mpoles>\n' % qmatoms)
		outt.write('\t\t\t\t<weights>%s</weights>\n' % weights)
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
		outt.write('\t\t\t\t<localframe>%s</localframe>\n' % localframe)
		outt.write('\t\t\t</fragment>\n')
	# CLOSING TAGS
	outt.write('\t\t\t</fragments>\n')
	outt.write('\t\t</segment>\n')
	outt.write('\t\t</segments>\n')
	outt.write('\t</molecule>\n')
	outt.write('\t</molecules>\n')
	outt.write('</topology>\n')	
	outt.close()
	return


def WriteSystemXmlUsingPattern(name, gro, xyz, mpsfile, gropattern, xyzpattern, mpspattern, xml='system.xml', outt=None, map2md=False,
	segment_properties={}):
	assert len(gropattern) == len(xyzpattern)
	assert len(gropattern) == len(mpspattern)
	mol = SingleMoleculeFromGro(gro)[0]
	mol.fragment()
	mol.make_dict()
	mol.name = name
	es,xyz = e_xyz_from_xyz(xyz)
	mps = mps_from_mpsfile(mpsfile)
	if outt == None:
		outt = open(xml,'w')
		outt.write('<topology>\n')
		outt.write('\t<molecules>\n')
	# MOLECULE HEADER	
	outt.write('\t<molecule>\n')
	outt.write('\t\t<name>%s</name>\n' % mol.name)
	outt.write('\t\t<mdname>%s</mdname>\n' % mol.name)
	outt.write('\t\t<segments>\n')
	# SEGMENT HEADER
	outt.write('\t\t<segment>\n')
	outt.write('\t\t\t<name>%s</name>\n' % mol.name)
	# XYZ FILE
	outt.write('\t\t\t<qmcoords>QC_FILES/%s.xyz</qmcoords>\n' % mol.name)	
	# OPTIONAL PROPERTIES (WRITTEN IF SUPPLIED)
	orbital_keys = ['orbitals', 'basisset', 'torbital_h', 'torbital_e']
	energy_keys  = ['U_cC_nN_h', 'U_nC_nN_h', 'U_cN_cC_h', 'U_cC_nN_e', 'U_nC_nN_e', 'U_cN_cC_e']
	for key in orbital_keys:
		if segment_properties.has_key(key):
			outt.write('\t\t\t<{key:s}>{val:s}</{key:s}>\n'.format(key=key, val=str(segment_properties[key])))
	for key in energy_keys:
		if segment_properties.has_key(key):
			outt.write('\t\t\t<{key:s}>{val:s}</{key:s}>\n'.format(key=key, val=str(segment_properties[key])))
	# MPS FILES
	outt.write('\t\t\t<multipoles_n>MP_FILES/%s_n.mps</multipoles_n>\n' % (mol.name))
	outt.write('\t\t\t<multipoles_h>MP_FILES/%s_h.mps</multipoles_h>\n' % (mol.name))
	outt.write('\t\t\t<multipoles_e>MP_FILES/%s_e.mps</multipoles_e>\n' % (mol.name))
	outt.write('\t\t\t<map2md>%d</map2md>\n' % (0 if map2md == False else 1))
	# FRAGMENTS
	outt.write('\t\t\t<fragments>\n')
	ctp_frag_count = 0
	gro_atom_count = 0
	xyz_atom_count = 0
	mps_atom_count = 0
	for ctp_frag_size, xyz_frag_size, mps_frag_size in zip(gropattern, xyzpattern, mpspattern):
		ctp_frag_count += 1
		first_gro_atom_in_frag = mol.atoms[gro_atom_count]
		fragName = '%s%d' % (first_gro_atom_in_frag.fragName, ctp_frag_count)
		outt.write('\t\t\t<fragment>\n')
		outt.write('\t\t\t\t<name>%s</name>\n' % fragName)
		# MD-ATOMS, QM-ATOMS, M-POLES, WEIGHTS
		mdatoms = ''
		qmatoms = ''
		mpoles = ''
		weights = ''
		local_frame_str = ''
		local_frame_ids = []
		ms = { 'H' : 1, 'C' : 12, 'N' : 14, 'O' : 16, 'S' : 32, 'Zn' : 65 }
		for i in range(ctp_frag_size):
			gro_atom_count += 1
			atom = mol.atoms[gro_atom_count-1]
			mdatoms += ' %-11s ' % ('%d:%s:%s' % (atom.fragId, atom.fragName, atom.name))
			if i < xyz_frag_size:
				xyz_atom_count += 1
				id = xyz_atom_count
				typ = es[id-1]
				m = ms[typ]
				qmatoms += ' %-11s ' % ('%d:%s' % (id, typ))
				weights += ' %-11s ' % ('%d' % m)
				if len(local_frame_ids) < 3 and typ != 'H':
					local_frame_ids.append(id)
					local_frame_str += ' %d ' % id
			else:
				qmatoms += ' %-11s ' % ':'
				weights += ' %-11s ' % '0'
			if i < mps_frag_size:
				mps_atom_count += 1
				id = mps_atom_count
				typ = mps[id-1].e
				mpoles += ' %-11s ' % ('%d:%s' % (id, typ))
			else:
				pass
		outt.write('\t\t\t\t<mdatoms>%s</mdatoms>\n' % mdatoms)			
		outt.write('\t\t\t\t<qmatoms>%s</qmatoms>\n' % qmatoms)
		outt.write('\t\t\t\t<mpoles> %s</mpoles>\n' % mpoles)
		outt.write('\t\t\t\t<weights>%s</weights>\n' % weights)
		outt.write('\t\t\t\t<localframe>%s</localframe>\n' % local_frame_str)
		outt.write('\t\t\t</fragment>\n')
	# CLOSING TAGS
	outt.write('\t\t\t</fragments>\n')
	outt.write('\t\t</segment>\n')
	outt.write('\t\t</segments>\n')
	outt.write('\t</molecule>\n')
	if outt == None:
		outt.write('\t</molecules>\n')	
		outt.write('</topology>\n')
		outt.close()
	return


def TopItpFromXyzGro(xyzfile, grofile, molname):
	mols = SingleMoleculeFromGro(grofile)
	atoms = mols[0].atoms
	if xyzfile != None:
		elem,xyz = e_xyz_from_xyz(xyzfile)
	else:
		elem = [ atom.name[0:1] for atom in atoms ]
		xyz = [ np.array([0,0,0]) for i in range(len(atoms)) ]
	# Sanity checks
	assert len(atoms) == len(elem) == len(xyz)
	for atm,e in zip(atoms,elem):
		if atm.name[0:1] != e[0:1]:
			print "WARNING: Possible mismatch", atm.name, "<>", e
	
	os.system('mkdir -p FORCEFIELD')
	os.chdir('FORCEFIELD')
	# WRITE TOPOLOGY FILE HEADER
	ofs = open('%s.itp' % molname, 'w')
	ofs.write('[ moleculetype ]\n')
	ofs.write('; Name            nrexcl\n')
	ofs.write('%s    3\n' % molname)
	ofs.write('\n')
	ofs.write('[ atoms ]\n')
	ofs.write(';   nr       type  rsdnr rsd      atom   cgnr     charge\n')
	# List of atoms in molecule
	for atm,e in zip(atoms,elem):
		ofs.write('{nr:5d} {typ:3s}   {rsdnr:5d} {rsd:3s}   {atom:3s} {cgnr:5d}   {chrg:1.3f}\n'.format(\
		    nr=atm.Id, typ=e, rsdnr=atm.fragId, rsd=atm.fragName, atom=atm.name, cgnr=atm.fragId+1, chrg=0.0))
	ofs.write('\n')
	# Potentials
	ofs.write('[ bonds ]\n')
	ofs.write(';  ai    aj           funct  c0 c1 c2 c3\n')
	ofs.write('\n')
	ofs.write('[ pairs ]\n')
	ofs.write(';  ai    aj           funct  c0 c1 c2 c3\n')
	ofs.write('\n')
	## System
	#ofs.write('[ system ]\n')
	#ofs.write('%1s\n' % molname)
	
	# WRITE ITP HEADER
	# Collect types
	atps = []
	for e in elem:
		if not PTABLE[e] in atps:
			atps.append(PTABLE[e])
	ofs = open('%s_forcefield.itp' % molname, 'w')
	# Atom types
	ofs.write('[ atomtypes ]\n')
	ofs.write('; name mass      charge      ptype   sigma     eps\n')
	for atp in atps:
		ofs.write('   {name:2s}   {mass:1.5f}   +0.00      A       0.325     0.293\n'.format(\
			name=atp, mass=PTABLE[e].mass))
	ofs.close()
	
	# DEFAULT ITP
	ofs = open('default.itp', 'w')
	# Defaults
	ofs.write('[ defaults ]\n')
	ofs.write('; nbfunc	comb-rule	gen-pairs	fudgeLJ	fudgeQQ\n')
	ofs.write('  1		    3		    yes		    0.5	    0.5\n')
	ofs.write('\n')
	ofs.close()
	
	os.chdir('../')
	# SYSTEM TOP
	ofs = open('system.top', 'w')
	ofs.write('; FORCEFIELD\n')
	ofs.write('#include "./FORCEFIELD/default.itp"\n')
	ofs.write('#include "./FORCEFIELD/%s_forcefield.itp"\n' % molname)
	ofs.write('\n')
	ofs.write('; MOLECULES\n')
	ofs.write('#include "./FORCEFIELD/%s.itp"\n' % molname)
	ofs.write('\n')
	ofs.write('[ system ]\n')
	ofs.write('%s\n' % molname)
	ofs.write('\n')
	ofs.write('[ molecules ]\n')
	ofs.write('%s 1\n' % molname)
	ofs.write('\n')
	ofs.close()	
	
	return


def ConvertToGhost(mol):
	# Atom name conversion rule
	#     name = 'C' + name[0:1] + counter
	# Molecule name
	#     name = 'G' + name
	# Fragment name
	#     name = 'G' + name[0:2]
	series = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
	if mol.frags == []:
		mol.fragment()
		mol.make_dict()
	for frag in mol.frags:
		assert len(frag.atoms) <= len(series)
	for frag in mol.frags:
		counter = 0
		frag.name = 'C' + frag.name[0:2]
		for atom in frag.atoms:
			atom.name = 'C%s%s' % (atom.name[0:1], series[counter])
			atom.fragName = 'G' + atom.fragName[0:2]
			counter += 1
	mol.name = 'G' + mol.name
	return mol


def GhostTopItpFromXyzGro(xyzfile, grofile, molname):
	mols = SingleMoleculeFromGro(grofile)
	atoms = mols[0].atoms
	elem,xyz = e_xyz_from_xyz(xyzfile)
	# Sanity checks
	assert len(atoms) == len(elem) == len(xyz)
	for atm,e in zip(atoms,elem):
		if atm.name[0:1] != e[0:1]:
			print "WARNING: Possible mismatch", atm.name, "<>", e

	# Convert to ghost
	mol = ConvertToGhost(mols[0])
	atoms = mol.atoms
	elem = [ 'C' for i in range(len(atoms)) ]
	mol.write_gro(molname+'.gro')
	
	# Write ghost xyz
	e_xyz_to_xyz(elem, xyz, molname + '.xyz')
	
	os.system('mkdir -p FORCEFIELD')
	os.chdir('FORCEFIELD')
	# WRITE TOPOLOGY FILE HEADER
	ofs = open('%s.itp' % molname, 'w')
	ofs.write('[ moleculetype ]\n')
	ofs.write('; Name            nrexcl\n')
	ofs.write('%s    3\n' % molname)
	ofs.write('\n')
	ofs.write('[ atoms ]\n')
	ofs.write(';   nr       type  rsdnr rsd      atom   cgnr     charge\n')
	# List of atoms in molecule
	for atm,e in zip(atoms,elem):
		ofs.write('{nr:5d} {typ:3s}   {rsdnr:5d} {rsd:3s}   {atom:3s} {cgnr:5d}   {chrg:1.3f}\n'.format(\
		    nr=atm.Id, typ=e, rsdnr=atm.fragId, rsd=atm.fragName, atom=atm.name, cgnr=atm.fragId+1, chrg=0.0))
	ofs.write('\n')
	# Potentials
	ofs.write('[ bonds ]\n')
	ofs.write(';  ai    aj           funct  c0 c1 c2 c3\n')
	ofs.write('\n')
	ofs.write('[ pairs ]\n')
	ofs.write(';  ai    aj           funct  c0 c1 c2 c3\n')
	ofs.write('\n')
	## System
	#ofs.write('[ system ]\n')
	#ofs.write('%1s\n' % molname)
	
	# WRITE ITP HEADER
	# Collect types
	atps = []
	for e in elem:
		if not PTABLE[e] in atps:
			atps.append(PTABLE[e])
	ofs = open('%s_forcefield.itp' % molname, 'w')
	# Atom types
	ofs.write('[ atomtypes ]\n')
	ofs.write('; name mass      charge      ptype   sigma     eps\n')
	for atp in atps:
		ofs.write('   {name:2s}   {mass:1.5f}   +0.00      A       0.325     0.293\n'.format(\
			name=atp, mass=PTABLE[e].mass))
	ofs.close()
	
	# DEFAULT ITP
	ofs = open('default.itp', 'w')
	# Defaults
	ofs.write('[ defaults ]\n')
	ofs.write('; nbfunc	comb-rule	gen-pairs	fudgeLJ	fudgeQQ\n')
	ofs.write('  1		    3		    yes		    0.5	    0.5\n')
	ofs.write('\n')
	ofs.close()
	
	os.chdir('../')
	# SYSTEM TOP
	ofs = open('system.top', 'w')
	ofs.write('; FORCEFIELD\n')
	ofs.write('#include "./FORCEFIELD/default.itp"\n')
	ofs.write('#include "./FORCEFIELD/%s_forcefield.itp"\n' % molname)
	ofs.write('\n')
	ofs.write('; MOLECULES\n')
	ofs.write('#include "./FORCEFIELD/%s.itp"\n' % molname)
	ofs.write('\n')
	ofs.write('[ system ]\n')
	ofs.write('%s\n' % molname)
	ofs.write('\n')
	ofs.write('[ molecules ]\n')
	ofs.write('%s 1\n' % molname)
	ofs.write('\n')
	ofs.close()	
	
	return
	


def ctp_map_auto(sql='state.sql', xml='system.xml', md_files='MD_FILES'):
	abort = False
	ext_dict = dict_by_ext(md_files)	
	# MD COORDINATE + TOPOLOGY FILE
	tpr = ext_dict['tpr']
	try:
		gro = ext_dict['gro']
	except KeyError:
		gro = ext_dict['pdb']
	except KeyError:
		print "No coordinate file in", os.getcwd(), md_files
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


def ctp_run_auto(exe, xml='options.xml', sql='state.sql', save=0, threads=1):
	abort = False
	# RUN THROUGH CHECKLIST
	if not xml in os.listdir('./'):
		print "ERROR Options file '%s' missing, will abort." % xml
		abort = True
	if not sql in os.listdir('./'):
		print "ERROR Sql file '%s' missing, will abort." % sql
		abort = True
	# EXECUTE
	opts = '-e "%s" -o %s -f %s -s %d -t %d' % (exe,xml,sql,save,threads)
	print 'ctp_run %s' % (opts)
	if abort: sys.exit(1)
	os.system('ctp_run %s' % opts)
	return
	
	
def write_xqmp_options(jobfile):
	ofs = open('options.xml','w')
	ofs.write('''<options>
	<xqmultipole>
		<multipoles>system.xml</multipoles> <!-- XML allocation polar sites -> fragment -->
		<control>
''')
	ofs.write('			<job_file>%s</job_file>\n' % jobfile)
	ofs.write('''			<emp_file>mps.tab</emp_file>	<!-- Allocation of .mps files to segs; for template, run 'stateserver' with key = 'emp' -->
			<pdb_check>0</pdb_check>        <!-- Output - Check mapping of polar sites -->
			<!--write_chk></write_chk-->    <!-- Write x y z charge file with dipoles split onto point charges spaced 1fm apart -->
			<format_chk>xyz</format_chk>   	<!-- 'gaussian' or 'xyz' -->
			<split_dpl>1</split_dpl>        <!-- '0' do not split dipoles onto point charges, '1' do split -->
			<dpl_spacing>1e-4</dpl_spacing>	<!-- Spacing a [nm] to be used when splitting dipole onto point charges: d = q * a -->
		</control>
		<coulombmethod>
			<method>cut-off</method>
			<cutoff1>3.0</cutoff1>
			<cutoff2>6.0</cutoff2>
		</coulombmethod>
		<tholemodel>
			<induce>1</induce>
			<induce_intra_pair>1</induce_intra_pair>
			<exp_damp>0.39</exp_damp>
			<scaling>0.25 0.50 0.75</scaling>
		</tholemodel>
		<convergence>
			<wSOR_N>0.30</wSOR_N>
			<wSOR_C>0.30</wSOR_C>
			<max_iter>512</max_iter>
			<tolerance>0.001</tolerance>
		</convergence>
	</xqmultipole>
</options>
''')
	ofs.close()
	return


def write_ewald_options(jobfile):
	ofs = open('options.xml','w')
	ofs.write('''<options>
	<ewald>
		<multipoles>system.xml</multipoles> <!-- XML allocation polar sites -> fragment -->
		<control>
''')
	ofs.write('			<job_file>%s</job_file>\n' % jobfile)
	ofs.write('''			<mps_table>mps.tab</mps_table>	<!-- Allocation of .mps files to segs; for template, run 'stateserver' with key = 'emp' -->
			<pdb_check>0</pdb_check>        <!-- Output - Check mapping of polar sites -->
		</control>
		<coulombmethod>
			<method>ewald</method>
			<cutoff>12.0</cutoff>
			<shape>xyslab</shape>
		</coulombmethod>
		<polarmethod>
            <method>thole</method>
            <induce>1</induce>
            <cutoff>3.0</cutoff>
        </polarmethod>
		<convergence>
            <energy>1e-5</energy>
            <kfactor>100</kfactor>
            <rfactor>6.0</rfactor>
            <kmetric>1 1 1</kmetric>
		</convergence>
	</ewald>
</options>
''')
	ofs.close()
	return



class Batch(object):
	def __init__(self, xmlfile = None):
		self.jobs = []
		if xmlfile != None:
			tree = xml.parse(xmlfile)
			for node in tree.getElementsByTagName('job'):
				self.jobs.append(Job(node=node))
		return
	def AddJob(self, jobTag, jobInput):
		jobId = len(self.jobs)+1
		newJob = Job(jobId,jobTag,jobInput)
		self.jobs.append(newJob)
		return
	def WriteToFile(self, outFile = 'jobs.xml'):
		if outFile in os.listdir('./'):
			print "Already exists:", os.getcwd(), outFile
			sys.exit(1)
		outt = open(outFile,'w')
		outt.write('<jobs>\n')
		for job in self.jobs:
			job.WriteToStream(outt)
		outt.write('</jobs>\n')
		outt.close()
		return
	def ProcessAsEwaldSiteJobs(self, states=['n','e','h']):
		segID_state_dict = {}
		for job in self.jobs:
			jobID = int(job.id_)
			tag = job.tag_.split(':')
			out = job.output_.split()
			stat = job.status_		
			segID = int(tag[0])
			segName = tag[1]
			state = tag[2]			
			#x = float(out[35])
			#y = float(out[36])
			#z = float(out[37])
			pos = np.array([0,0,0])
			pp = float(out[3])
			if state not in states: continue		
			jobResult = JobResultXqm(jobID, segID, segName, state, pos, 0, pp, 0)			
			try:
				segID_state_dict[segID][state] = jobResult
			except KeyError:
				segID_state_dict[segID] = {}
				segID_state_dict[segID][state] = jobResult		
		# SUBTRACT ENERGIES TO OBTAIN IP, EA
		assert 'n' in states
		chrgStates = states[:]
		chrgStates.remove('n')		
		ips_eas = { 'e' : [], 'h' : [] }
		keyIDs = segID_state_dict.keys()
		keyIDs.sort()
		for ID in keyIDs:			
			for state in chrgStates:
				n = segID_state_dict[ID]['n']
				c = segID_state_dict[ID][state]
				cn = n.SubtractFrom(c)				
				ips_eas[state].append(cn)				
				#n.PrintInfo()
				#c.PrintInfo()
				#cn.PrintInfo()
		return ips_eas
	def ProcessAsXqmSiteJobs(self, states=['n','e','h']):
		# OUTPUT STRUCTURE
		# 0 1          2   3         4   5         6   7            
		# 1 1:C60:n    TT +0.0000000 PP +0.0000000 PU +0.0000000 
		#
		# 8   9         10   11        12   13        14   15    
		# UU +0.0000000 F00 +0.0000000 F01 +0.0000000 F02 +0.0000000   
		#
		# 16   17        18   19        20  21        22  23       
		# F11 +0.0000000 F12 +0.0000000 M0 +0.0000000 M1 +0.0000000
		#
		# 24  25         26    27  28    29  30    31 32 33
		# M2 +0.0000000 |QM0|   1 |MM1|  30 |MM2|  90 IT  0
		#
		# 34   35          36        37
		# XYZ +4.5579834 +1.0736500 +0.3511333	
		#
		# ASSEMBLE INTO DICTIONARY	
		segID_state_dict = {}
		for job in self.jobs:
			jobID = int(job.id_)
			tag = job.tag_.split(':')
			out = job.output_.split()
			stat = job.status_		
			segID = int(tag[0])
			segName = tag[1]
			state = tag[2]			
			x = float(out[35])
			y = float(out[36])
			z = float(out[37])
			pos = np.array([x,y,z])			
			tt = float(out[3])
			pp = float(out[5])
			pu = float(out[7])
			if state not in states: continue		
			jobResult = JobResultXqm(jobID, segID, segName, state, pos, tt, pp, pu)
			
			try:
				segID_state_dict[segID][state] = jobResult
			except KeyError:
				segID_state_dict[segID] = {}
				segID_state_dict[segID][state] = jobResult		
		# SUBTRACT ENERGIES TO OBTAIN IP, EA
		assert 'n' in states
		chrgStates = states[:]
		chrgStates.remove('n')		
		ips_eas = { 'e' : [], 'h' : [] }
		keyIDs = segID_state_dict.keys()
		keyIDs.sort()
		for ID in keyIDs:			
			for state in chrgStates:
				n = segID_state_dict[ID]['n']
				c = segID_state_dict[ID][state]
				cn = n.SubtractFrom(c)				
				ips_eas[state].append(cn)				
				#n.PrintInfo()
				#c.PrintInfo()
				#cn.PrintInfo()
		return ips_eas


class JobResultXqm(object):
	def __init__(self, jobID, segID, segName, state, pos, tt, pp, pu):
		self.jobID = jobID
		self.segID = segID
		self.segName = segName
		self.state = state
		self.pos = pos
		self.tt = tt
		self.pp = pp
		self.pu = pu
		return
	def PrintInfo(self):
		print "ID %5d %5d %-10s %-2s XYZ %+1.7e %+1.7e %+1.7e TT %+1.7e PP %+1.7e PU %+1.7e" % \
		    (self.jobID, self.segID, self.segName, self.state, 
		    self.pos[0], self.pos[1], self.pos[2], self.tt, self.pp, self.pu)
		return
	def SubtractFrom(self, other):
		assert other.segID == self.segID
		assert other.segName == self.segName
		if self.state == 'n': assert other.state in ['e','h']
		elif self.state in ['e','h']: assert self.state == 'n'
		else: assert False # State combination other than 'n' <> ['e','h']? Error.
		dtt = other.tt - self.tt
		dpp = other.pp - self.pp
		dpu = other.pu - self.pu
		dstate = '%s%s' % (other.state,self.state)
		return JobResultXqm(0, self.segID, self.segName, dstate, self.pos, dtt, dpp, dpu)


class JobResultEwald(object):
	def __init__(self, jobID, segID, segName, state, pos, pp):
		self.jobID = jobID
		self.segID = segID
		self.segName = segName
		self.state = state
		self.pos = pos
		self.pp = pp

class Job(object):
	def __init__(self, id_ = None, tag_ = None, input_ = None, node = None):
		self.id_ 		= id_
		self.tag_ 		= tag_
		self.input_ 	= input_
		self.status_ 	= 'AVAILABLE'
		self.time_ 		= None
		self.host_ 		= None
		self.output_ 	= None
		self.error_ 	= None		
		self.node_      = node
		if node != None:
			self.LoadFromXmlNode(node)
		return	
	def LoadFromXmlNode(self, node):
		self.id_ = node.getElementsByTagName('id')[0].firstChild.nodeValue
		self.tag_ = node.getElementsByTagName('tag')[0].firstChild.nodeValue
		self.input_ = node.getElementsByTagName('input')[0].firstChild.nodeValue
		status = node.getElementsByTagName('status')
		if status == []: self.status_ = 'AVAILABLE'
		else: self.status_ = status[0].firstChild.nodeValue
		time = node.getElementsByTagName('time')
		if time == []: self.time_ = None
		else: self.time_ = time[0].firstChild.nodeValue
		host = node.getElementsByTagName('host')
		if host == []: self.host_ = None
		else: self.host_ = host[0].firstChild.nodeValue
		output = node.getElementsByTagName('output')
		if output == []: self.output_ = None
		else: self.output_ = output[0].firstChild.nodeValue
		error = node.getElementsByTagName('error')
		if error == []: self.error_ = None
		else: 
			if self.status_ == 'COMPLETE':				
				try:
					self.error_ = error[0].firstChild.nodeValue
					print "Has error", self.id_, self.tag_, self.input_, ":", self.error_
				except AttributeError:
					#print "Has error", self.id_, self.tag_, self.input_, ", yet complete."
					pass
		return
	def WriteToStream(self, ofs):
		# TODO Extend this function to incorporate output, timestamp, ...
		ofs.write('<job>\n')
		ofs.write('\t<id>%d</id>\n' % self.id_)
		ofs.write('\t<tag>%s</tag>\n' % self.tag_)
		ofs.write('\t<input>%s</input>\n' % self.input_)
		
		ofs.write('</job>\n')
		return


def jobs_from_pop(pop, includeList = None, states = ['n','e','h']):
	# INCLUDE LIST
	checkInclude = True
	
	# GENERATE BATCH
	batch = Batch()
	if includeList == None:
		checkInclude = False
		for mol in pop.mols:
			if checkInclude and mol.Id not in includeList:
				continue
			for state in states:
				jobTag = '%d:%s:%s' % (mol.Id,mol.name,state)
				jobInput = '%d:%s:MP_FILES/%s_%s.mps' % (mol.Id,mol.name,mol.name,state)
				batch.AddJob(jobTag,jobInput)
	else:
		for idx in includeList:
			mol = pop.mols[idx-1]
			assert idx == mol.Id
			for state in states:
				jobTag = '%d:%s:%s' % (mol.Id,mol.name,state)
				jobInput = '%d:%s:MP_FILES/%s_%s.mps' % (mol.Id,mol.name,mol.name,state)
				batch.AddJob(jobTag,jobInput)
	return batch
		
	
		
	
	












