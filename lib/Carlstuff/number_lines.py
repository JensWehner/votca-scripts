# Writes line numbers in front of lines, overwrites file

inttstr = raw_input('Enter file name: ')
intt = open(inttstr,'r')
write = []
lnno = 1
for ln in intt.readlines():
	ln = str(lnno) + '   ' + ln
	write.append(ln)
	lnno += 1
intt.close()

outt = open(inttstr,'w')
for ln in write:
	outt.write(ln)
outt.close()
