#!/bin/tcsh
#$ -pe PE_8 8
#$ -o run.log
#$ -e errors.log
#$ -cwd
#$ -j y
#$ -m eab
#$ -l h_rt=36:00:00
ulimit 129600
#$ -M kordt@mpip-mainz.mpg.de
#$ -N kmc

set workdir=`pwd`
echo "Workdir is $workdir"

source /people/thnfs/homes/kordt/votca/bin/VOTCARC.csh
source /sw/linux/intel/composerxe-2011.0.084/bin/compilervars.csh intel64

# create local scratch
if ( ! -d /usr/scratch/kordt ) then
    mkdir /usr/scratch/kordt
endif

set jno=0
while ( -d job_$jno ) 
    set jno = `expr $jno + 1`
end
set jobdir="/usr/scratch/kordt/job_$jno"
mkdir $jobdir
rm -rf $jobdir/'jobid #CURRENTJOB#'*
# mkdir $jobdir/temp

echo "Jobdir is $jobdir"

# copy stuff to local scratch
rsync -ar $workdir/'jobid #CURRENTJOB#'* $jobdir

cd $jobdir

setenv LD_LIBRARY_PATH /people/thnfs/homes/kordt/votca/lib
#LD_LIBRARY_PATH=/people/thnfs/homes/kordt/votca/lib
#COMMANDTOEXECUTE#

sleep 5

cd ..
#sync back
rsync -ar $jobdir/'jobid #CURRENTJOB#'* $workdir

#clean
rm -rf $jobdir/'jobid #CURRENTJOB#'*

