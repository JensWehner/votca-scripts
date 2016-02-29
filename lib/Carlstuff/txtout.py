import sys

class TxtOut(object):
	"""
	Class for dynamic printing. Methods include
	> this(_str): print in current line
	> next(_str): print in next line
	> tout(_str): same as built-in print '...'
	"""
	def __init__(self):
		return
	
	def this(self,_str = ''):
		sys.stdout.write('\r'+_str)
		sys.stdout.flush()
		
	def next(self, _str = ''):
		sys.stdout.write('\n'+_str)
		sys.stdout.flush()
		
	def tout(self, _str = ''):
		sys.stdout.write(_str+'\n')
		sys.stdout.flush()
		

