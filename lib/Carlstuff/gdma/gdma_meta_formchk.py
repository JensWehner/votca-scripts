from momo import osio, endl, flush

fs = [ 'nN', 'aA', 'cC' ]
mol = 'PEN'

for f in fs:
	osio.cd(f)
	osio >> '../gdma_formchk.sh {mol:s}_{f:s}'.format(mol=mol, f=f)
	osio.cd(-1)
