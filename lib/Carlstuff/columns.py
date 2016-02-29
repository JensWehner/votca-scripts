intt = raw_input('Input: ')
intt = open(intt,'r')
outt = raw_input('Output: ')
outt = open(outt,'w')

cols = raw_input('Columns: ')
cols = [ int(i) for i in cols.split() ]
print cols

for ln in intt.readlines():
	lnsp = ln.split()
	outln = ''
	outsp = []
	if lnsp == []:
		pass
	else:
		if len(lnsp) >= len(cols):
			try:
				outsp = [ lnsp[i] for i in cols ]
				for sp in outsp:
					outln += str(sp) + ' '
				outln += ' \n'
				outt.write(outln)
			except IndexError:
				pass
				
			
		else:
			pass
			
intt.close()
outt.close()
		
		
			
			
	

