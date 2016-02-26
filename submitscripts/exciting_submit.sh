#!/bin/tcsh
#$ -pe PE_8 8
#$ -o out.info
#$ -e err.info
#$ -cwd
#$ -j y
#$ -m a
#$ -M wehnerj@mpip-mainz.mpg.de
#$ -N exciting

# USERNAME IS wehnerj

echo "Starting"

source /etc/profile.d/modules.csh
setenv MODULEPATH "/sw/linux/modules/modulefiles/"

module load intel/13.0
# export OMP_NUM_THREADS=8

# WORKDIRECTORY
set workdir=`pwd`
echo "Workdir is $workdir"

# WORK SCRATCH
if ( ! -d /usr/scratch/wehnerj ) then
    mkdir /usr/scratch/wehnerj
endif

set jno=0
while ( -d /usr/scratch/wehnerj/job_$jno ) 
    set jno=`expr $jno + 1`
end
set jobdir="/usr/scratch/wehnerj/job_$jno"
mkdir $jobdir
rm -rf $jobdir/*
mkdir $jobdir/temp

echo "Jobdir is $jobdir"

# COPY FOLDER
rsync -ar $workdir/* $jobdir --exclude "*.info"

cd $jobdir

# EXECUTE HEAVY WORK
#grompp -c system.gro -p system.top -f grompp.mdp -n system.ndx -o topol.tpr -maxwarn 4
/people/thnfs/homes/wehnerj/exciting_cluster/bin/excitingser input.xml > log.txt
cd ..

# SYNCHRONIZE BACK & CLEAN
rsync -ar $jobdir/* $workdir --exclude "*.info"
#rm -rf $jobdir
