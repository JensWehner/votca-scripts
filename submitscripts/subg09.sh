#!/bin/tcsh
#
#$ -pe PE_8 8   
#$ -o job.out
#$ -e job.err
#$ -cwd
#$ -j y
#$ -m a  
#$ -M wehnerj@mpip-mainz.mpg.de
#$ -N job_8PNP4s_n

set workdir=`pwd`
echo "Workdir is $workdir"

source /etc/profile.d/modules.csh
setenv MODULEPATH "/sw/linux/modules/modulefiles/"
module use -a '/people/thnfs/homes/wehnerj/privatemodules'
module load gaussian/g09

# create local scratch
if ( ! -d /usr/scratch/wehnerj ) then
    mkdir /usr/scratch/wehnerj
endif

set jno=0
while ( -d /usr/scratch/wehnerj/job_$jno ) 
    set jno = `expr $jno + 1`
end
set jobdir="/usr/scratch/wehnerj/job_$jno"
mkdir $jobdir
rm -rf $jobdir/*
mkdir $jobdir/temp

echo "Jobdir is $jobdir"

# copy stuff to local scratch
rsync -ar $workdir/* $jobdir

cd $jobdir

g09 8PNP4s_n.com

cd ..
#sync back
rsync -ar $jobdir/* $workdir --exclude "temp"

#clean
rm -rf $jobdir

