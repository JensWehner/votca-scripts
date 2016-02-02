reset

set terminal postscript eps size 4,3 enhanced color font 'Times,14'
set output 'energycut.eps'

set dgrid3d 40,40,1
set pm3d at b
set isosample 200,200

splot 'energycut.txt' with lines t '' 
