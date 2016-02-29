#! /usr/bin/env python
import os
import sys

SCRIPTPATH = '/people/thnfs/homes/poelking/PYSCRIPT/gnuplot'

VERBOSE		= True
gp2eps 		= '%1s/gp2eps' 	% SCRIPTPATH
tex2eps		= '%1s/tex2eps' % SCRIPTPATH
fixbb		= '%1s/fixbb' 	% SCRIPTPATH
gnuplot 	= 'gnuplot'


# Sanity checks
if len(sys.argv) < 2:
	print "No input file specified. Return."
	sys.exit(1)
if not sys.argv[1] in os.listdir('./'):
	print "No such file: '%1s'. Return" % sys.argv[1]	
	sys.exit(1)
if len(sys.argv) > 2:
	print "Too many arguments. Return."
	sys.exit(1)
if sys.argv[1][-3:] != '.gp':
	print "First change extension to .gp, currently '%1s'. Return" % sys.argv[1][-3:]
	sys.exit(1)


# Arguments
gnufile = sys.argv[1]
stem    = sys.argv[1][:-3]


# Info policy
if VERBOSE: dev = ' '
else: dev = ' > /dev/null 2> /dev/null'


# Dependencies
os.system('%1s --deps %1s > %1s.d.tmp %1s' % (gp2eps, gnufile, stem, dev))
os.system("sed 's,\(.*/\)\(%1s\)\.eps[ :]*,\2.eps: ,g' < %1s.d.tmp > %1s.d;" % (stem, stem, stem))
os.system('rm -f %1s.d.tmp %1s' % (stem, dev))

# Gnuplot
os.system('%1s %1s %1s && ' 					% (gnuplot, gnufile, ' ') 	+ \
          '%1s %1s %1s && ' 					% (tex2eps, stem, dev) 		+ \
          'rm -f %1s-inc.eps %1s.tex %1s && ' 	% (stem, stem, dev) 		+ \
          '%1s %1s.eps %1s' 					% (fixbb, stem, dev) )

os.system('rm %1s.d' % stem)








