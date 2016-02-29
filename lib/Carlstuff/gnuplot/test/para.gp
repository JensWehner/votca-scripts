reset
set terminal epslatex standalone color
set output "para.tex"


#################
# AXIS SPECS    #
#################
set size 1.0,1.0
set size square
set origin 0.0,0.0
set border lw 1

set multiplot
set key top left


set ylabel "$g$ [$\\%$]"    
set format y "%1.2f"   
set ytics 3.0,0.55,5.2    
set yrange [3.0:5.2]  
set mytics 1              

set y2label "$b$ [\\AA]"
set format y2 "%1.2f"
set y2range[4.5:5.3]
set y2tics 4.5,0.2,5.3






    
set xlabel "$T$ [K]"
set format x "%1.0f"


#set logscale y

#################
# LINE STYLES   #
#################
set style line 1 linecolor rgb "gray"    linewidth 2
set style line 2 linecolor rgb "black"   linewidth 2
set style line 3 linetype 1 linecolor rgb "blue"    ps 2 lw 3
set style line 4 linetype 2 linecolor rgbcolor "#483D8B"  ps 2 lw 3
set style line 5 linecolor rgb "yellow"  linewidth 2
set style line 6 linetype 3 linecolor rgb "red"     ps 2
set style line 7 linecolor rgb "green"   ps 2 lw 3
set style line 8 linetype 4 linecolor rgbcolor "#8B0000"  ps 2 lw 3
set style line 9 linecolor rgb "magenta" linewidth 2


g1(x) = G01 * 1 / (2*3.141592)**0.5 * 1/s1 * exp( - (x - u1)**2 / (2 * s1**2) )
G01 = 10
s1 = 0.047
u1 = 0.0
#fit g1(x) 'sites_rreg_II.dat' using ($1+0.41):2 via s1, G01

g2(x) = G02 * 1 / (2*3.141592)**0.5 * 1/s2 * exp( - (x - u2)**2 / (2 * s2**2) )
G02 = 10
s2 = 0.075
u2 = 0.0
#fit g2(x) 'sites_rrnd_II.dat' using ($1+0.40):2 via s2, G02

g3(x) = G03 * 1 / (2*3.141592)**0.5 * 1/s3 * exp( - (x - u3)**2 / (2 * s3**2) )
G03 = 10
s3 = 0.056
u3 = 0.0
#fit g3(x) 'sites_rreg_I.dat' using ($1+0.46):2 via s3, G03

g4(x) = G04 * 1 / (2*3.141592)**0.5 * 1/s4 * exp( - (x - u4)**2 / (2 * s4**2) )
G04 = 10
s4 = 0.075
u4 = 0.0
#fit g4(x) 'sites_rrnd_I.dat' using ($1+0.36):2 via s4, G04

set key bottom right

psc = 1.5

plot \
'paracrystallinity.dat' using 1:($2*0.333333333333333) axes x1y2 w lp   title "$b$" lc rgbcolor "blue" lw 3  ps psc, \
'paracrystallinity.dat' using 1:($3*100) axes x1y1 w lp   title "$g_m$" lc rgbcolor "red" lw 3  ps psc, \
'paracrystallinity.dat' using 1:($4*100) axes x1y1 w lp   title "$g_c$" lc rgbcolor "green" lw 3  ps psc
#'dyn_order_300.dat' using 1:3 w p   title  "300K" lc rgbcolor "purple" , \
#'dyn_order_350.dat' using 1:3 w p   title "350K" lc rgbcolor "blue", \
#'dyn_order_400.dat' using 1:3 w p   title "400K" lc rgbcolor "green", \
#'dyn_order_450.dat' using 1:3 w p   title "450K" lc rgbcolor "orange", \
#'dyn_order_500.dat' using 1:3 w p   title "500K" lc rgbcolor "red"



# +++++ #
# INSET #
# +++++ #

set size 0.3,0.4
set origin 0.17,0.5
set font "Helvetica, 12"
set border lw 4
unset xlabel 
unset key
set format x "%1.1f"
set xrange [-15:15]
set xtics ( "-15\260" -15, "0\260" 0, "+15\260" 15 ) font "Helvetica,18"
set xlabel "CAR-S-CBR-CAL" font "Helvetica,18"
unset ylabel
set yrange [0:400]
set ytics 0,100,400
set format y ""

#plot 'improper_rreg_digit.dat' using 1:2 ls 8 w p title "RREG 100 II", \
#     'improper_rrnd_digit.dat' using 1:2 ls 4 w p title "RREG   90 II", \
#     'improper_rreg_planar.dat' using 1:2 ls 6 w p title "RREG 100 I ", \
#     'improper_rrnd_planar.dat' using 1:2 ls 3 w p title "RREG   90 I "





reset
