from __vmd_assist__ import *


ofs = open('config.tcl', 'w')
vmd = SystemVMD()
vmd.AddMol('confout.gro')
vmd.AddRep(modselect='fragment 0', modstyle='cpk')
vmd.ToTCL(ofs)
ofs.close()






