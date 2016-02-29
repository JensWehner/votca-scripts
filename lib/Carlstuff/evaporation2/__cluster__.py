from __pyosshell__ import *


QUEUE_OUT = 'out.info'
QUEUE_ERR = 'err.info'
QUEUE_MAIL = ['%s@mpip-mainz.mpg.de' % getpass.getuser(),'a'] # eab


VOTCARC = '/people/thnfs/homes/poelking/VOTCA_SUSE_12/bin/VOTCARC.csh'



def retrieve_qid(logfile=QUEUE_OUT):
	try:
		intt = open(logfile,'r')
		top = intt.readline()
		intt.close()
		qid = int(top.split('/')[-2].split('.')[0])
	except IOError:
		qid = '--qw--'
	return qid
	

def is_qid_active(qid): 
	is_active = not os.system('qstat | grep %d' % qid)
	return is_active


def are_jobs_waiting(username = getpass.getuser()):	
	sig = os.system('qstat -u %s | grep " qw " > /dev/null' % username)
	if sig == 0:
		return True
	else:
		return False


def write_qsub_sh_template(outfile = 'qsub.sh', username = getpass.getuser(), 
    queue = 'PE_8', procs = 8):
    
    # Placeholder '_USERNAME' (will be replaced by <username>)
	
	outt = open(outfile,'w')
	
	outt.write('#!/bin/tcsh\n')
	outt.write('#\n')
	outt.write('#$ -pe %s %d\n' % (queue,procs))	
	outt.write('#$ -o %s\n' % (QUEUE_OUT))
	outt.write('#$ -e %s\n' % (QUEUE_ERR))
	outt.write('#$ -cwd\n')
	outt.write('#$ -j y\n')
	outt.write('#$ -m %s\n' % (QUEUE_MAIL[1]))
	outt.write('#$ -M %s\n' % (QUEUE_MAIL[0]))
	outt.write('#$ -N _DESCRIPTION\n')
	
	
	outt.write('''
# USERNAME IS _USERNAME

source /sw/linux/intel/composerxe-2011.0.084/bin/compilervars.csh intel64
source /sw/linux/gromacs/4.5/shared/latest/bin/GMXRC

# WORKDIRECTORY
set workdir=`pwd`
echo "Workdir is $workdir"

# WORK SCRATCH
if ( ! -d /usr/scratch/_USERNAME ) then
    mkdir /usr/scratch/_USERNAME
endif

set jno=0
while ( -d job_$jno ) 
    set jno = `expr $jno + 1`
end
set jobdir="/usr/scratch/_USERNAME/job_$jno"
mkdir $jobdir
rm -rf $jobdir/*
mkdir $jobdir/temp

echo "Jobdir is $jobdir"

# COPY FOLDER
rsync -ar $workdir/* $jobdir

cd $jobdir

# EXECUTE HEAVY WORK
#_GROMPP_CMD
#_MDRUN_CMD

cd ..

# SYNCHRONIZE BACK & CLEAN
rsync -ar $jobdir/* $workdir
rm -rf $jobdir
''')

	outt.close()
	return


def WriteCtpBatch(command, tag, outfile = 'ctp_batch.sh', 
    username = getpass.getuser(), queue = 'PE_8', procs = 8):
	
	outt = open(outfile,'w')
	# QUEUE & BATCH INFO	
	outt.write('#!/bin/tcsh\n')
	outt.write('#\n')
	outt.write('#$ -pe %s %d\n' % (queue,procs))	
	outt.write('#$ -o %s\n' % (QUEUE_OUT))
	outt.write('#$ -e %s\n' % (QUEUE_ERR))
	outt.write('#$ -cwd\n')
	outt.write('#$ -j y\n')
	outt.write('#$ -m %s\n' % (QUEUE_MAIL[1]))
	outt.write('#$ -M %s\n' % (QUEUE_MAIL[0]))
	outt.write('#$ -N %s\n' % tag)
	outt.write('\n')
	# SOURCE VOTCA
	outt.write('source %s\n\n' % VOTCARC)
	# BASE DIRECTORY
	outt.write('# BASE DIRECTORY\n')
	outt.write('set basedir=`pwd`\n')
	outt.write('if ( ! -d /usr/scratch/%s ) then\n' % username)
	outt.write('    mkdir /usr/scratch/%s\n' % username)
	outt.write('endif\n\n')
	# JOB DIRECTORY
	outt.write('# JOB DIRECTORY\n')
	outt.write('set jno=0\n')
	outt.write('while ( -d job_$jno )\n')
	outt.write('    set jno = `expr $jno + 1`\n')
	outt.write('end\n')	
	outt.write('set jobdir="/usr/scratch/%s/job_$jno"\n' % username)
	outt.write('mkdir -p $jobdir\n')
	outt.write('rm -rf $jobdir/*\n')
	outt.write('rsync -ar $basedir/* $jobdir\n\n')
	# EXECUTE HEAVY STUFF
	outt.write('# EXECUTE HEAVY STUFF\n')	
	outt.write('cd $jobdir\n')
	outt.write('%s\n' % command)
	outt.write('cd ..\n\n')
	# SYNC BACK
	outt.write('# SYNC BACK\n')
	outt.write('rsync -ar $jobdir/* $basedir\n')
	outt.write('rm -rf $jobdir\n')
	outt.close()
	return



