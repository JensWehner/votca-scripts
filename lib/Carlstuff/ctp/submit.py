from   __future__ import division
import sys        as sys
import os		  as os
import numpy      as np


os.chdir('RUN_DIR_SINGLES')

for i in range(51):
	
	os.chdir('Q'+str(i))
	os.system('qsub qctp.sh')	
	os.chdir('../')

os.chdir('../')
