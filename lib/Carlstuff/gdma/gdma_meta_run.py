from momo import osio, endl, flush
import os

def write_gdma_infile(fchkfile):
	assert fchkfile[-5:] == '.fchk'
	tag = fchkfile[:-5]
	osio << "File 'gdma.in' in" << osio.cwd() << ":" << fchkfile << endl
	ofs = open('gdma.in', 'w')
	ofs.write('''\
Title "{tag:s}"
File {fchk:s}

Multipoles
  Limit 2
  Limit 1 H
  Radius H 0.35
  Punch {tag:s}.mps
Start

Finish
'''.format(fchk=fchkfile, tag=tag))
	ofs.close()

GDMA	= '/people/thnfs/homes/poelking/GDMA/gdma-2.2.06/bin/gdma'
dirs 	= [ 'nN', 'aA', 'cC' ]
mol 	= 'PEN'

for dir in dirs:
	osio.cd(dir)
	osio << "Directory: '%s'" % dir << endl
	write_gdma_infile('{mol:s}_{dir:s}.fchk'.format(mol=mol, dir=dir))
	osio >> '{gdma:s} < gdma.in > gdma.out &'.format(gdma=GDMA)
	osio.cd(-1)
