from   __future__ import division
import sys        as sys
import os		  as os
import numpy      as np


segments     = 512
fractions    = 50
cp_from_path = 'CP_QRUN'
cp_qctp      = 'CP_QRUN/qctp.sh'
cp_options   = 'CP_QRUN/options.xml'
tag          = 'dcv4t_35A_'


os.mkdir('RUN_DIR_SINGLES')

os.chdir('RUN_DIR_SINGLES')
for f in range(fractions):	
	os.mkdir('Q'+str(f))	
	

q_segs = int(segments / fractions)
remains = segments - q_segs * fractions
	
for f in range(fractions):

	first = f * q_segs + 1
	last = (f+1) * q_segs

	os.chdir('Q'+str(f))
	os.system('cp -r ../../'+cp_from_path+'/*'+' .')
	os.system('cat ../../'+cp_qctp + '  | sed "s/DESCRIPTION/'+tag+str(f) + '/" > ./qctp.sh')
	os.system('cat ../../'+cp_options + '  | sed "s/FIRST/'+str(first) + '/" | sed "s/LAST/'+str(last) + '/" > ./options.xml')
	os.chdir('../')
	
	
os.chdir('../')




	








