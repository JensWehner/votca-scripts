import os

def sect_from_bracket_file(infile, get_section = 'atoms', skip = ';'):	

	intt = open(infile,'r')	
	table = []
	section = 'GLOBAL'
	
	for ln in intt.readlines():
		
		ln = ln.replace('\t',' ')
		sp = ln.split()		
		
		if sp == [] or skip in sp[0] or skip in sp[0][0]:
			continue
		
		if '[' and ']' in ln:
			section = ln.replace('[',' ').replace(']',' ').strip()
		
		elif section != get_section:
			continue
		
		else:
			table.append(ln.split())
			
	intt.close()
	return table
		

def dict_from_bracket_file(infile, skip = '#'):
	
	intt = open(infile,'r')	
	options = {}
	section = 'GLOBAL'
	
	for ln in intt.readlines():
		
		ln = ln.replace('\t',' ')
		sp = ln.split()
		if sp == [] or skip in sp[0] or skip in sp[0][0]:
			continue
		
		if '[' and ']' in ln:
			section = ln.replace('[',' ').replace(']',' ').strip()
			options[section] = {}
		
		else:
			ln = ln.split('=')
			key = ln[0].strip()
			
			tmpstr = ln[1].strip()
			
			if tmpstr[0:1] == '"' and tmpstr[-1:] == '"':
				# One single string
				arg = [tmpstr.replace('"','')]		
			else:
				tmp = ln[1].strip().split()
				arg = []
			
				for t in tmp:
					if skip in t:
						break
					else:
						try:
							arg.append(float(t))
						except ValueError:
							arg.append(t)
			
			options[section][key] = arg
			
	
	intt.close()
	return options
	

def struct_from_topfile(infile):
	
	system = sect_from_bracket_file(infile, get_section = 'molecules')
	name   = sect_from_bracket_file(infile, get_section = 'system')
	include = sect_from_bracket_file(infile, get_section = 'GLOBAL')
	
	mol_nrAtoms = {}
	
	for item in include:
		name = item[1].replace('"','')
		try:
			molecule = sect_from_bracket_file(name, 'moleculetype')[0][0]
		except IndexError:
			continue
		nr_atoms = len(sect_from_bracket_file(name))		
		mol_nrAtoms[molecule] = nr_atoms
		
	mol_nrMol_nrAtoms = []
	for item in system:
		mol_nrMol_nrAtoms.append( [item[0], int(item[1]), mol_nrAtoms[item[0]]] )
	
	return mol_nrMol_nrAtoms

	
