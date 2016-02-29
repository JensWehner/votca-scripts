from __pyosshell__ import *



conv = 'dcv4t.com'

table = file_to_table('dcv4t.com')
exyz  = []


prev = np.array([0,0,0])

for tab in table:
	
	if tab[0] == '%' or  len(tab) < 4:
		continue
		
	
	if tab[0] in 'CHNS':
		
		x = float(tab[1])
		y = float(tab[2])
		z = float(tab[3])
	
		elem = tab[0]
	
	else:		
		
		x = float(tab[0])
		y = float(tab[1])
		z = float(tab[2])
		
		this = np.array([x,y,z])
		
		if magnitude(this-prev) > 0.2:
			elem = 'X'
		else:
			elem = 'A'
		
		prev = this
	
	exyz.append([elem,x,y,z])

xyz_file = conv[:-4]+'_converted.xyz'

outt = open(xyz_file,'w')
outt.write('%5d\n\n' % len(exyz))
outt.close()

table_to_file_safe(conv[:-4]+'_converted.xyz',exyz,mode = 'a')
			
	
	
	
	
