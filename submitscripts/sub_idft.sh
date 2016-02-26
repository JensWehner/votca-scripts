#!/bin/tcsh
#
#$ -pe PE_8 8
#$ -o idft.out
#$ -e idft.err
#$ -cwd
#$ -j n
#$ -m eab
#$ -M wehnerj@mpip-mainz.mpg.de
#$ -N idftjens
#$ -l hostname="thinc*"

set workdir=`pwd`
echo "Workdir is $workdir"

mkdir -p /usr/scratch/wehnerj/idft

setenv g09root /sw/linux/gaussian
setenv GAUSS_SCRDIR /usr/scratch/wehnerj
source $g09root/g09/bsd/g09.login
source ~/tm_init
source /data/isilon/wehnerj/votca/bin/VOTCARC.csh

#echo $LD_LIBRARY_PATH

ctp_parallel -e "idft" -o /people/thnfs/homes/wehnerj/Medos/supercellEL086new/options.xml -f /people/thnfs/homes/wehnerj/Medos/supercellEL086new/system.sql -t 8 -c 32 -r "stat(AVAILABLE)" -s 0 
