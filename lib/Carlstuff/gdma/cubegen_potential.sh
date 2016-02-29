#! /bin/tcsh
# $3 = -2,-3,-4 => coarse, medium, fine
source ~/g03_init
cubegen 0 potential=scf $1.fchk $2.cube $3 h

