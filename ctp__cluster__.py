import os
import getpass

QUEUE_MAIL = ['%s@mpip-mainz.mpg.de' % getpass.getuser(),'a'] # eab

def write_cluster_batch(
    command, 
    tag, 
    outfile = 'ctp_batch.sh', 
    username = getpass.getuser(), 
    queue = 'PE_8', 
    procs = 8,
    outlog = 'out.log',
    errlog = 'err.log',
    votcarc = None,
    source = None,
    module= None,
    rsync=None):

   
    if tag[0:1] in '0123456789':
		tag = 'Q'+tag
	
    if votcarc == None and module==None:
        votcarc = os.path.join(os.environ['VOTCASHARE'],'../../bin/VOTCARC.csh')
	
    ofs = open(outfile,'w')
    # QUEUE & BATCH INFO	
    ofs.write('#!/bin/tcsh\n')
    ofs.write('#\n')
    ofs.write('#$ -pe %s %d\n' % (queue,procs))	
    ofs.write('#$ -o %s\n' % (outlog))
    ofs.write('#$ -e %s\n' % (errlog))
    ofs.write('#$ -cwd\n')
    ofs.write('#$ -j y\n')
    ofs.write('#$ -m %s\n' % (QUEUE_MAIL[1]))
    ofs.write('#$ -M %s\n' % (QUEUE_MAIL[0]))
    ofs.write('#$ -N %s\n' % tag)
    ofs.write('\n')
    # SOURCE LOCATIONS
    if source != None and module==None:
        if type(source) == str:
			ofs.write('source %s\n' % source)
        elif source!=False:
		    for s in source:
		        ofs.write('source %s\n' % s)
    if module !=None:
        ofs.write('source /etc/profile.d/modules.csh\n')
        ofs.write('setenv MODULEPATH "/sw/linux/modules/modulefiles/"\n')
        ofs.write('module use -a "/people/thnfs/homes/wehnerj/privatemodules"\n')
        if type(module) == str:
			ofs.write('module load %s\n' % module)
        else:
            for s in module:
                ofs.write('module load %s\n' % s)
	# SOURCE VOTCA
    if source!=False:
        ofs.write('source %s\n\n' % votcarc)
	# BASE DIRECTORY
    ofs.write('# BASE DIRECTORY\n')
    ofs.write('set basedir=`pwd`\n')
    ofs.write('if ( ! -d /usr/scratch/%s ) then\n' % username)
    ofs.write('    mkdir /usr/scratch/%s\n' % username)
    ofs.write('endif\n\n')
    # JOB DIRECTORY
    ofs.write('# JOB DIRECTORY\n')
    ofs.write('set jno=0\n')
    ofs.write('while ( -d /usr/scratch/%s/job_$jno )\n' % username  )
    ofs.write('    set jno = `expr $jno + 1`\n')
    ofs.write('end\n')	
    ofs.write('set jobdir="/usr/scratch/%s/job_$jno"\n' % username)
    ofs.write('mkdir -p $jobdir\n')
    ofs.write('rm -rf $jobdir/*\n')
    if rsync==None:
        ofs.write('rsync -ar $basedir/* $jobdir\n\n')
    else:
        ofs.write('rsync -ar $basedir/{} $jobdir\n\n'.format(rsync))
    # EXECUTE HEAVY STUFF
    ofs.write('# EXECUTE HEAVY STUFF\n')	
    ofs.write('cd $jobdir\n')
    if type(command) == str:
        ofs.write('%s\n' % command)
    else:
        for c in command:
            ofs.write('%s\n' % c)
    ofs.write('cd ..\n\n')
    # SYNC BACK
    ofs.write('# SYNC BACK\n')
    ofs.write('rsync -au $jobdir/* $basedir\n')
    ofs.write('rm -rf $jobdir\n')
    ofs.close()
    return outfile


def multi_write_cluster_batch(
    n, 
    command, 
    tag = 'VOTCA_CTP_{ID:02d}', 
    outfile = 'ctp_batch_{ID:02d}.sh', 
    username = getpass.getuser(), 
    queue = 'PE_8', 
    procs = 8,
    votcarc = None,
    resubmit = False,
    source = None,
    module = None,rsync=None):
    """
    Writes <n> cluster batch scripts, using string placeholder {ID} in <command>, <tag>, <outfile> 
    Returns a list of the batch files that were written
    """
    offset_id = 1
    
    while resubmit and outfile.format(ID=offset_id) in os.listdir('./'):
        offset_id += 1
    if resubmit:
        print "Resubmit %d jobs (previously submitted: %d)" % (n, offset_id-1)

    list_sh = []
    for batch_id in range(offset_id,n+offset_id):
        cmd_i = command.format(ID=batch_id)
        tag_i = tag.format(ID=batch_id)
        outfile_i = outfile.format(ID=batch_id)
        outlog_i = tag_i.lower()+".std"
        errlog_i = tag_i.lower()+".err"
        print "CTP batch script '{batch}'\n  o cmd='{cmd}'\n  o tag='{tag}'".format(batch=outfile_i, cmd=cmd_i, tag=tag_i)
        write_cluster_batch(cmd_i, tag_i, outfile_i, username, queue, procs, outlog_i, errlog_i, votcarc=votcarc, source=source,module=module,rsync=rsync)
        list_sh.append(outfile_i)
    return list_sh

    	

