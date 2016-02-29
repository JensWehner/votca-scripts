set terminal epslatex standalone color
set output "test.tex"


# ========================================================
#                       LAYOUT
# ========================================================

lsc = 1.0 # Line scale
psc = 1.0 # Point scale
bsc = 3.0 # Border scale

set multiplot
set size 1.0,1.0 	# W, H
set size square
set border lw bsc 
set origin 0.0,0.0 	# W, H


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
#                   PLOT VARIABLES
# ========================================================


d(x) = 0*x
e(x) = 1*x
f(x) = 2*x
g(x) = 3*x
h(x) = 4*x
i(x) = 5*x
j(x) = 6*x
k(x) = 7*x
l(x) = 8*x
m(x) = 9*x
n(x) = 10*x
o(x) = 11*x
p(x) = 12*x
q(x) = 13*x
r(x) = 14*x
s(x) = 15*x



# ========================================================
#                        PLOT 1
# ========================================================

unset key

set origin 0.0,0.0
set size   1.0,1.0

set xlabel "x"
set ylabel "y"

plot \
-d(x) axes x1y1 w lp  lt 0  pt pt0 lw lsc ps psc lc rgbcolor bb title "$0$", \
-e(x) axes x1y1 w lp  lt 1  pt pt1 lw lsc ps psc lc rgbcolor db title "$1$", \
-f(x) axes x1y1 w lp  lt 2  pt pt2 lw lsc ps psc lc rgbcolor mb title "$2$", \
-g(x) axes x1y1 w lp  lt 3  pt po3 lw lsc ps psc lc rgbcolor lb title "$3$", \
-h(x) axes x1y1 w lp  lt 4  pt po1 lw lsc ps psc lc rgbcolor dr title "$4$", \
-i(x) axes x1y1 w lp  lt 5  pt po2 lw lsc ps psc lc rgbcolor mr title "$5$", \
-j(x) axes x1y1 w lp  lt 6  pt po3 lw lsc ps psc lc rgbcolor lr title "$6$", \
-k(x) axes x1y1 w lp  lt 7  pt po4 lw lsc ps psc lc rgbcolor dg title "$7$", \
-l(x) axes x1y1 w lp  lt 8  pt po5 lw lsc ps psc lc rgbcolor mg title "$8$", \
-m(x) axes x1y1 w lp  lt 9  pt po6 lw lsc ps psc lc rgbcolor lg title "$9$", \
-n(x) axes x1y1 w lp  lt 10 pt pc1 lw lsc ps psc lc rgbcolor dy title "$10$", \
-o(x) axes x1y1 w lp  lt 11 pt pc2 lw lsc ps psc lc rgbcolor my title "$11$", \
-p(x) axes x1y1 w lp  lt 12 pt pc3 lw lsc ps psc lc rgbcolor ly title "$12$", \
-q(x) axes x1y1 w lp  lt 13 pt pc4 lw lsc ps psc lc rgbcolor dw title "$13$", \
-r(x) axes x1y1 w lp  lt 14 pt pc5 lw lsc ps psc lc rgbcolor mw title "$14$", \
-s(x) axes x1y1 w lp  lt 15 pt pc6 lw lsc ps psc lc rgbcolor lw title "$15$"



# ========================================================
#                        PLOT 2
# ========================================================

set origin 1.0,0.0
set size   1.0,1.0

set xlabel "x"
set ylabel "y"

plot \
d(x) axes x1y1 w lp  lt 0  pt pt0 lw lsc ps psc lc rgbcolor bb title "$0$", \
e(x) axes x1y1 w lp  lt 1  pt pt1 lw lsc ps psc lc rgbcolor db title "$1$", \
f(x) axes x1y1 w lp  lt 2  pt pt2 lw lsc ps psc lc rgbcolor mb title "$2$", \
g(x) axes x1y1 w lp  lt 3  pt po3 lw lsc ps psc lc rgbcolor lb title "$3$", \
h(x) axes x1y1 w lp  lt 4  pt po1 lw lsc ps psc lc rgbcolor dr title "$4$", \
i(x) axes x1y1 w lp  lt 5  pt po2 lw lsc ps psc lc rgbcolor mr title "$5$", \
j(x) axes x1y1 w lp  lt 6  pt po3 lw lsc ps psc lc rgbcolor lr title "$6$", \
k(x) axes x1y1 w lp  lt 7  pt po4 lw lsc ps psc lc rgbcolor dg title "$7$", \
l(x) axes x1y1 w lp  lt 8  pt po5 lw lsc ps psc lc rgbcolor mg title "$8$", \
m(x) axes x1y1 w lp  lt 9  pt po6 lw lsc ps psc lc rgbcolor lg title "$9$", \
n(x) axes x1y1 w lp  lt 10 pt pc1 lw lsc ps psc lc rgbcolor dy title "$10$", \
o(x) axes x1y1 w lp  lt 11 pt pc2 lw lsc ps psc lc rgbcolor my title "$11$", \
p(x) axes x1y1 w lp  lt 12 pt pc3 lw lsc ps psc lc rgbcolor ly title "$12$", \
q(x) axes x1y1 w lp  lt 13 pt pc4 lw lsc ps psc lc rgbcolor dw title "$13$", \
r(x) axes x1y1 w lp  lt 14 pt pc5 lw lsc ps psc lc rgbcolor mw title "$14$", \
s(x) axes x1y1 w lp  lt 15 pt pc6 lw lsc ps psc lc rgbcolor lw title "$15$"





