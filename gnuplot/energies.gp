set terminal cairolatex  color colortext standalone font 'phv,12' header "\\usepackage[helvet]{sfmath}\n\\definecolor{t}{rgb}{0,0,0}" dashed dl 1.5 #size 5.5in,6in
set out "energies.tex"

load "~/.gnuplot_styles_tex"

set tics nomirror
set notitle
set macro
# x- and ytics for each row resp. column
NOXTICS = "set xtics ('' 0.0, '' 5.0,'' 10.0,'' 15.0,'' 20.0, '' 25.0, '' 30.0, '' 35.0, ''40.0); \
          unset xlabel"
XTICS = "set format x '%3.1f';set xtics (0.0,'5.0' 5.0,'10.0' 10.0,'15.0' 15.0,'20.0' 20.0, 25, 30,35,40);\
          set xlabel 'x'"
NOYTICS = "set format y ''; unset ylabel"
YTICS = "set format y '%3.2f'; set ylabel 'y'"

# Margins for each row resp. column
TMARGIN = "set tmargin at screen 0.90; set bmargin at screen 0.55"
BMARGIN = "set tmargin at screen 0.55; set bmargin at screen 0.20"
#LMARGIN = "set lmargin at screen 0.15; set rmargin at screen 0.55"
LMARGIN = "set lmargin at screen 0.15; set rmargin at screen 0.95"
RMARGIN = "set lmargin at screen 0.55; set rmargin at screen 0.95"

set multiplot layout 2,1
set xrange[0:40]
## energies
@NOXTICS; @YTICS
@TMARGIN; @LMARGIN
set yrange[1.95:2.45]
set ytics autofreq 2.0,0.1
set ylabel "Energies (eV)"
#set logscale y
#unset key
plot "energies.dat" u (2.0*$1):2 t "FE",\
     "" u (2.0*$1):3 t "CT1",\
     "" u (2.0*$1):4 t "CT2",\
     "" u (2.0*$1):5 t "CT3"

### Charge transfer
@XTICS; @YTICS
@BMARGIN; @LMARGIN
set ylabel "CT (e)"
unset key
set ytics autofreq 0.0,0.2
set xlabel "Cluster size (nm)"
set yrange[0:1.05]
plot "energies.dat" u (2.0*$1):6 t "FE",\
     "" u (2.0*$1):7 t "CT1",\
     "" u (2.0*$1):8 t "CT2",\
     "" u (2.0*$1):9 t "CT3"


unset multiplot

set out
