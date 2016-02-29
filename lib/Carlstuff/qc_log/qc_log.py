import re
import os
import ui

# Where to read from
currdir = raw_input("\nYour dir: ")
print "Search for .log in", currdir

# FIND LOG FILES 
files = os.listdir(currdir)
logs  = []

for fi in files:
    if fi[-3:] == 'log':
        logs.append(fi)
    else:
        pass

# Where to write to
adddir  = raw_input("\nqc_ log dir:")

# CROPT INFO FROM LOG FILES, ONE AT A TIME
for lo in logs:
    print lo
    # in- / output filenames
    loid = lo[:-4]
    lostr   = currdir+"/"+lo
    xyzstr  = currdir+"/"+adddir+"/"+loid+"_XYZ.dat"
    chrgstr = currdir+"/"+adddir+"/"+loid+"_CHRG.dat"
    enerstr = currdir+"/"+adddir+"/"+loid+"_ENER.dat"
    xyzfi   = open(xyzstr,'w')
    chrgfi = open(chrgstr,'w')
    enerfi = open(enerstr,'w')
    
    #####################
    # Check termination #
    #####################    
    tmp,tmp1 = ui.croptt(tt=lostr,startstr = 'Normal termination', this = True)
    if tmp != []:
        print tmp1
    else:
        print "! .log probably not complete !"   
    #################
    # CROP XYZ DATA #
    #################
    atm,tmp = ui.croptt(tt=lostr,startstr = 'Charge',
                        finishstr = 'NAtoms',colstr='1')
    xyz,tmp = ui.croptt(tt=lostr,startstr = 'Standard orientation:',
                        startatknock = -1, finishstr = 'Rotational',
                        skipstr = '-----')
    if xyz == []:
        xyz, tmp = ui.croptt(tt=lostr,startstr = 'Z-Matrix orientation:',
                             startatknock = -1, finishstr = 'Rotational',
                             skipstr = '------')
    if xyz != []:
        axyz = []
        nxyz = []

        for line in xyz:
            try:
                ind = int(line[0])
                nxyz.append(line)
            except ValueError:
                pass
        for i in range(len(atm)):
            new = atm[i][0] + ' ' + nxyz[i][3] + ' ' + nxyz[i][4] + ' ' + nxyz[i][5]
            axyz.append(new)
        for item in axyz:
            xyzfi.write(item+' \n')
        xyzfi.close()
        print "XYZ",
    ####################
    # CROP CHARGE DATA #
    ####################

    tmp,chrg = ui.croptt(tt=lostr,startstr = 'Fitting point charges',
                         finishstr = '-------', skipstr = 'Charge',
                          startatknock = -1)
    
    if chrg == '':
        # Only one charge entry
        print "! Recommended to check charges !"
        tmp,chrg = ui.croptt(tt=lostr, startstr = 'Fitting pont charges',
                             finishstr = '------', skipstr = 'Charge')

    if chrg != '':
        chrgfi.writelines(chrg)
        chrgfi.close()
        print "CHARGE",
    ####################
    # CROP ENERGY DATA #
    ####################
    ener,tmp = ui.croptt(tt=lostr, startstr = 'E(', this = True,
                          startatknock = -1, colstr = '5 6')
    if ener == []:
        # Only one energy entry => chagne startatknock
        print "! Recommended to check energies !"
        ener, tmp = ui.croptt(tt=lostr, startstr = 'E(', this = True,
                              colstr = '5 6')

    
    if ener != []:
        ener_AU = float(ener[0][0])
        ener_eV    = ener_AU*27.211396132
        ener_kJmol = ener_AU*2625.49962
        enerfi.write(str(ener_AU)+' A.U. \n')
        enerfi.write(str(ener_eV)+' eV \n')
        enerfi.write(str(ener_kJmol) + ' kJ/mol \n')
        enerfi.close()
        print "ENER\n"



