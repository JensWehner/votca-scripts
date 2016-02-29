reset
set terminal postscript enhanced color
set term png enhanced font "Helvetica,10"

#################
# AXIS SPECS    #
#################
                                set output "gdma_h.jpg"
                                set title "Static Site Energy Distribution DCV2T E(C) - E(N)"
                                set size 0.8,1.0
                                set origin 0.0,0.0

                           #   |
                           #   |
set ylabel "Frequency"     #   |
set format y "%1.1f"       #   |
#set ytics -180,60,180     #   |
set yrange [-1.17:1.17]     #   |
                           #   |
                           #   |
                           #   |
                           #   |
                           #   |_______________________________________

                                   set xlabel "Site Energy [eV]"
                                   set format x "%1.1f"
                                   #set xtics -180,60,180
                                   set xrange [-1.17:1.17]


#################
# LINE STYLES   #
#################
set style line 1 linecolor rgb "gray" linewidth 2
set style line 2 linecolor rgb "black" linewidth 1.5
set style line 3 linecolor rgb "blue" linewidth 1.5
set style line 4 linecolor rgb "violet" linewidth 1.5
set style line 5 linecolor rgb "yellow" linewidth 1.5
set style line 6 linecolor rgb "red" linewidth 1.5
set style line 7 linecolor rgb "green" linewidth 1.5

plot 'tamed_DCV_1_esf.dat' using 1:2:($4/20):($5/20) with vector title "ESF DCV (N) GDMA k = 2"


reset
