reset
set terminal postscript enhanced color
set term png enhanced size 1000,1000 font "Helvetica,24"

#################
# AXIS SPECS    #
#################
                                set output "DOS_Compared_dE.jpg"
                                set title "Site Energy Distributions DCV4T C60"
                                set size 1.0,1.0
                                set origin 0.0,0.0
                                set border lw 8

                           #   |
                           #   |
set ylabel "Frequency"     #   |
set format y "%1.0f"       #   |
#set ytics -180,60,180     #   |
#set yrange [0:27]     #   |
                           #   |
                           #   |
                           #   |
                           #   |
                           #   |_______________________________________

                                   set xlabel "Site Energy [eV]"
                                   set format x "%1.1f"
                                   #set xtics -1.2,0.2,0.1
                                   set xrange [-1.5:2.5]


#################
# LINE STYLES   #
#################
set style line 1 linecolor rgb "gray" linewidth 3
set style line 2 linecolor rgb "black" linewidth 3
set style line 3 linecolor rgb "blue" linewidth 3
set style line 4 linecolor rgb "violet" linewidth 3
set style line 5 linecolor rgb "yellow" linewidth 3
set style line 6 linecolor rgb "red" linewidth 3
set style line 7 linecolor rgb "green" linewidth 3

plot 'dE_SiteEnergies_IND0_DCV.dat' using 1:2 ls 1 with steps      title "DCV4T Static", \
	 'dE_SiteEnergies_IND0_C60.dat' using 1:2 ls 2 with steps      title "C60 Static ", \
	 'dE_SiteEnergies_IND1_DCV.dat' using 1:2 ls 6 with histeps    title "DCV4T Dynamic", \
	 'dE_SiteEnergies_IND1_C60.dat' using 1:2 ls 3 with histeps    title "C60 Dynamic"

reset
