#! /usr/bin/env python
from __pyosshell__ import *


SIZE_X 		= 2
SIZE_Y 		= 2
SIZE2_X 	= 1.75
SIZE2_Y 	= 1.75
BORDER_LW 	= 2
LSC 		= 4

if len(sys.argv) < 2 or sys.argv[1][-3:] != '.gp':
	print "No call. Exit."
	sys.exit(1)

gpfile = sys.argv[1]
outfile = 'ppt_%1s' % gpfile

intt = open(gpfile,'r')
outt = open(outfile, 'w')
for ln in intt.readlines():
	sp = ln.split()
	if 'set term' in ln:
		ln = 'set terminal epslatex standalone color size %1.1f,%1.1f\n' % (SIZE_X, SIZE_Y)
	if 'set output' in ln:
		ln = 'set output "%1s.tex"' % (outfile[:-3])
	elif 'set size' in ln and not 'square' in ln:
		ln = 'set size %1.2f,%1.2f\n' % (SIZE2_X, SIZE2_Y)
	elif 'set border lw' in ln:
		ln = 'set border lw %1.2f\n' % (BORDER_LW)
	elif 'lsc =' in ln:
		ln = 'lsc = %1.2f\n' % (LSC)
	else:
		pass
	
	outt.write(ln)
outt.close()
intt.close()

os.system('/people/thnfs/homes/poelking/PYSCRIPT/gnuplot/gnu2eps.py %1s' % outfile)

