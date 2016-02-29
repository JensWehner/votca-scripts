import ui

tt = raw_input(' -> ')

ctsp, ctcp = ui.croptt(tt = tt,  startstr = "H ", startatknock = -1)

to = open('connectivity.dat','w')
to.writelines(ctcp)
to.close()



