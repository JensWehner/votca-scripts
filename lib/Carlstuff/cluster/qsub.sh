#!/bin/tcsh
#
#$ -pe openmpi 8
#$ -o outinf
#$ -e errinf
#$ -cwd
#$ -j y
#$ -m eab
#$ -M poelking@mpip-mainz.mpg.de
#$ -N C60_fcc_npt

source /sw/linux/intel/composerxe-2011.0.084/bin/compilervars.csh intel64
source /sw/linux/gromacs/4.5/shared/latest/bin/GMXRC

################
# PREPARATIONS #
################

# WORKDIRECTORY
set workdir=`pwd`
echo "Workdir is $workdir"

# WORK SCRATCH
if ( ! -d /usr/scratch/poelking ) then
    mkdir /usr/scratch/poelking
endif

set jno=0
while ( -d job_$jno ) 
    set jno = `expr $jno + 1`
end
set jobdir="/usr/scratch/poelking/job_$jno"
mkdir $jobdir
rm -rf $jobdir/*
mkdir $jobdir/temp

echo "Jobdir is $jobdir"

# COPY FOLDER
rsync -ar $workdir/* $jobdir

cd $jobdir

#############
# EXECUTION #
#############

#grompp -c fcc.gro -p include.top -f grompp.mdp -o topol.tpr -maxwarn 0
#mdrun_d -s topol.tpr -o traj.trr -x traj.xtc -c confout.gro -cpo state.cpt -cpt 18 -maxh 36

echo "Nothing to do here" > "new.file"

#################
# SYNCHRONISING #
#################

cd ..
#sync back
rsync -ar $jobdir/* $workdir

#clean
rm -rf $jobdir
