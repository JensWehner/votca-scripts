set terminal epslatex standalone color
set output "raw.tex"

# ========================================================
#                       LAYOUT
# ========================================================

lsc = 1.0 # Line scale
psc = 1.0 # Point scale
bsc = 1.0 # Border scale

set multiplot
set size   square
set size   1.0,1.0 	# W, H
set origin 0.0,0.0 	# W, H
set border lw bsc 



# ========================================================
#                       STYLES
# ========================================================

db = "#000080"; mb = "#0000FF"; lb = "#87CEFA"; # blue
dr = "#8B0000"; mr = "#FF0000"; lr = "#CD5C5C"; # red
dg = "#006400"; mg = "#32CD32"; lg = "#ADFF2F"; # green
dy = "#FFA500"; my = "#DAA520"; ly = "#FFD700"; # yellow
dw = "#A9A9A9"; mw = "#7F7F7F"; lw = "#DCDCDC"; # gray
bb = "#000000"                                  # black

pt0 = 0;    				# no point
pt1 = 1;  pt2 = 2; pt3 = 3 	# crosses
po1 = 4;  pc1 = 5  			# square
po2 = 6;  pc2 = 7  			# circle
po3 = 8;  pc3 = 9  			# triangle up
po4 = 10; pc4 = 11 			# triangle down
po5 = 12; pc5 = 13 			# diamond
po6 = 14; pc6 = 15 			# pentagon



# ========================================================
#                        PLOT 1 
# ========================================================

set origin 0.0, 0.0
set size   1.0, 1.0

set xlabel "x"
set ylabel "y"

plot \
"paracrystallinity.dat" using ($1*1.000):($2*0.333) axes x1y1 w lp lt 1 pt pt1 lw lsc ps psc lc rgbcolor mb title "$1$" , \
"paracrystallinity.dat" using ($1*1.000):($3*100.000) axes x1y1 w lp lt 2 pt pt2 lw lsc ps psc lc rgbcolor mr title "$2$" , \
"paracrystallinity.dat" using ($1*1.000):($4*100.000) axes x1y1 w lp lt 3 pt pt3 lw lsc ps psc lc rgbcolor mg title "$3$" 
