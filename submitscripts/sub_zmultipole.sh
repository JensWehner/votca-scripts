#!/bin/tcsh
#
#$ -pe PE_8 8
#$ -o zmulti.out
#$ -e zmulti.err
#$ -cwd
#$ -j n
#$ -m eab
#$ -M kordt@mpip-mainz.mpg.de
#$ -N zmul
#$ -l hostname=thinc*

set workdir=`pwd`
echo "Workdir is $workdir"

mkdir -p /usr/scratch/kordt

setenv g09root /sw/linux/gaussian
setenv GAUSS_SCRDIR /usr/scratch/kordt
source $g09root/g09/bsd/g09.login
source ~/votca/bin/VOTCARC.csh
source ~/tm_init

#echo $LD_LIBRARY_PATH

ctp_run -e "zmultipole" -o options.xml -f /people/thnfs/homes/kordt/Projects/DPBIC/calculations/MerzKollmann/4000_molecules/cutoffradius//fullbox/zmultipole_3nm/cutoff_3/state.sql -t 8 -s 0 > zmulti_out.txt
