#!/bin/tcsh
#
#$ -pe PE_8 8
#$ -o out.info
#$ -e err.info
#$ -cwd
#$ -j y
#$ -m a
#$ -M wehnerj@mpip-mainz.mpg.de
#$ -N T0_evaporate_C60_347

# USERNAME IS wehnerj

source /sw/linux/intel/composerxe-2011.0.084/bin/compilervars.csh intel64
source /sw/linux/gromacs/4.5/shared/latest/bin/GMXRC

# WORKDIRECTORY
set workdir=`pwd`
echo "Workdir is $workdir"

# WORK SCRATCH
if ( ! -d /usr/scratch/wehnerj ) then
    mkdir /usr/scratch/wehnerj
endif

set jno=0
while ( -d job_$jno ) 
    set jno = `expr $jno + 1`
end
set jobdir="/usr/scratch/wehnerj/job_$jno"
mkdir $jobdir
rm -rf $jobdir/*
mkdir $jobdir/temp

echo "Jobdir is $jobdir"

# COPY FOLDER
rsync -ar $workdir/* $jobdir

cd $jobdir

# EXECUTE HEAVY WORK
#grompp -c system.gro -p system.top -f grompp.mdp -n system.ndx -o topol.tpr -maxwarn 4
mdrun  -s topol.tpr -o traj.trr -x traj.xtc -c confout.gro -cpo state.cpt -cpt 18 -maxh 36

cd ..

# SYNCHRONIZE BACK & CLEAN
rsync -ar $jobdir/* $workdir
rm -rf $jobdir
