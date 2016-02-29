#! /usr/bin/env python
#
#$ -pe openmpi 8
#$ -o out.info
#$ -e err.info
#$ -cwd
#$ -j y
#$ -m eab
#$ -M poelking@mpip-mainz.mpg.de
#$ -N JOB_DESCRIPTION

import os		as os
import shutil	as shutil

USER = 'poelking' # Also remember to change e-mail address in header
JOB  = 0

def exec_this():
	
	print os.listdir('./')

	outt = open('success','w')
	outt.write('Success.\n')
	outt.close()
	
	return True

# ============================================================ #
# PREPARATIONS                                                 #
# ============================================================ #

print "Preparing directories:"

# Working directory
work_dir = os.getcwd()
print "... Working directory = %1s." % work_dir

# Scratch directory
try:
	scratch_dir = '/usr/scratch/%1s/' % USER
	os.mkdir(scratch_dir)
	print "... Scratch directory = %1s created." % scratch_dir
except OSError:
	print "... Scratch directory = %1s exists." % scratch_dir

# Job directory
job_dir = scratch_dir + ('job_%1d' % JOB)
try:
	os.mkdir(job_dir)
	print "... Job exe directory = %1s created." % scratch_dir
except OSError:
	print "... Job exe directory = %1s exists." % job_dir

os.system('rm -rf %1s/*' %job_dir)
os.system('rsync -ar %1s/* %1s' % (work_dir, job_dir))
os.chdir(job_dir)


# ============================================================ #
# EXECUTION                                                    #
# ============================================================ #

print "Executing batch job:"

return_bool = exec_this()

if return_bool:
	print "... Success."
else:
	print "... Returned False."

# ============================================================ #
# SYNCHRONISE                                                  #
# ============================================================ #

print "Synchronise data:"

os.chdir('../')
os.system('rsync -ar %1s/* %1s' % (job_dir, work_dir))
os.system('rm -r %1s' % job_dir)

print "... Success."


	
