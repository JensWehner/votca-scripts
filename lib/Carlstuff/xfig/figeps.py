#! /usr/bin/env python
import os
import sys

SCRIPTPATH = '/people/thnfs/homes/poelking/PYSCRIPT/xfig'

VERBOSE		= False
figdeps		= '%1s/figdeps.sh' 	% SCRIPTPATH
figtex2eps	= '%1s/figtex2eps' 	% SCRIPTPATH



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
if sys.argv[1][-4:] != '.fig':
	print "First change extension to .fig, currently '%1s'. Return" % sys.argv[1][-3:]
	sys.exit(1)


# Arguments
figfile = sys.argv[1]
stem    = sys.argv[1][:-3]


os.system('%1s %1s' % (figdeps, figfile))
os.system('%1s %1s' % (figtex2eps, figfile))
os.system('rm figtex2eps-preamble.tex')
