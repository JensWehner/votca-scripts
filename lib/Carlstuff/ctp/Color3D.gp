reset
set term png enhanced size 1000,1000 font "Helvetica,24"
set output "Thiophene_ESP.jpg"
set title "Thiophene ESP"

set border lw 6
set size square
set xlabel 'x [A]'
set ylabel 'y [A]'
set xrange[-10:10]
set yrange[-10:10]
set zrange[-15:15]
set isosample 500
set pm3d map
#set palette defined (0 "white", 0.005 "blue", 0.01 "green", 0.02 "yellow", 0.04 "red")
set palette defined (0 "blue", 0.5 "white", 1 "red")
splot 'ISO_esp_0.xyz' notitle

reset
