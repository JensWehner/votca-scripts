import xml.dom.minidom as xmld
import numpy as np

# =============================================================================
# XML.DOM.MINIDOM WRAPPERS
# =============================================================================

def GenerateNodeDict(node, path='', abbreviate=False):
	path_value = {}
	if node.firstChild == None and '#text' in path: return {}
	elif node.firstChild == None: return { path : XmlNodeValue(path, '', node.attributes, node) }
	if node.firstChild.nodeValue.split() != []:
		value = XmlNodeValue(path, node.firstChild.nodeValue, node.attributes, node) 
		path_value[path] = value
		if abbreviate: path_value['.%s' % node.nodeName] = value	
	for child in node.childNodes:
		if path == '': childPath = child.nodeName
		else: childPath = '%s.%s' % (path, child.nodeName)
		add_dict = GenerateNodeDict(child, childPath, abbreviate)
		for key in add_dict.keys():
			path_value[key] = add_dict[key]	
	return path_value

def CleanXmlTree(node, level='', verbose=False):
	rm = []
	if verbose: print level + node.nodeName
	for child in node.childNodes:		
		CleanXmlTree(child, level=level+'    ', verbose=verbose)		
		if 'text' in child.nodeName:
			if verbose: print level + "Remove", child.nodeName
			rm.append(child)
		else:
			if verbose: print level + "Keep", node.firstChild.nodeName
	for child in rm:
		node.removeChild(child)
	return node

class XmlNode(object):
	def __init__(self, node):
		self.node = node
		self.path_value = GenerateNodeDict(self.node, abbreviate=True)
	def __getitem__(self, key):
		return self.path_value[key]
	def keys(self):
		return self.path_value.keys()

class XmlNodeCollection(list):
	def __init__(self, *args, **kwargs):
		"""
		>>> # Use like this
		>>> XmlNodeCollection([xmlnode1, xmlnode2])
		>>> XmlNodeCollection(tree=xmldom, key='job')
		"""
		if len(kwargs) == 2:
			nodes = [ XmlNode(node) for node in kwargs['tree'].getElementsByTagName(kwargs['key']) ]
			for node in nodes: self.append(node)
		elif len(args) == 1:
			for node in args[0]: self.append(node)
		else:
			assert False
	def Nodes(self):
		return Nodes
	def SelectNodesWhere(self, path, value, typ=str, convert=lambda v : v):
		selection = []
		for node in self:
			if convert(node[path].As(typ)) == value:
				selection.append(node)
			else:
				pass
		return XmlNodeCollection(selection)

class XmlNodeValue(object):
	def __init__(self, path, value, attributes, node=None):
		self.node = node
		self.path = path
		self.value = value
		self.attributes = attributes
	def As(self, typ):
		if typ == np.array:
			sps = self.value.split()
			return typ([ float(sp) for sp in sps ])
		else:
			return typ(self.value)
	def AsArray(self, typ, sep=' ', rep='\t\n'):
		for r in rep:
			self.value = self.value.replace(r, sep)
		sp = self.value.split(sep)
		return [ typ(s) for s in sp if str(s) != '' ]
	def SetNodeValue(self, new_value):
		self.value = new_value
		if self.node != None:
			self.node.firstChild.nodeValue = new_value
		return

class XmlDocument(object):
	def __init__(self, root, filename=None, verbose=False):
		# Document
		self.doc = xmld.Document()
		self.root = root
		self.filename = filename if filename != None else root+'.xml'
		# Path tracker
		self.has_paths = {}
		self.path_docelement = {}
		self.verbose = verbose
		# Add root
		self.has_paths[self.root] = True
		self.rootelement = self.doc.createElement(self.root)
		self.path_docelement[self.root] = self.rootelement
		self.doc.appendChild(self.rootelement)
		return
	def Add(self, parent, child='', value=None, attributes=''):
		# Assemble path
		path = parent+'.'+child if child != '' else parent
		if self.verbose: print "Add {0:40s} = {1:20s}".format(path,str(value))
		sp = path.split('.')
		# Keep track of full path, parent path, and tip
		parent_path = self.root
		cum_path = self.root
		for i in range(len(sp)):
			tip = sp[i]
			cum_path += '.'+sp[i]
			# Check whether path exists, if not, add element
			try:
				assert self.has_paths[cum_path]
			except KeyError:
				#print "... {0:20s} full={1:40s} base={2:40s}".format(tip,cum_path,parent_path)
				self.has_paths[cum_path] = True
				new_element = self.doc.createElement(tip)
				# Only add value if this is the head node
				if value != None and i == len(sp)-1:
					new_element.appendChild(self.doc.createTextNode(str(value)))
				self.path_docelement[cum_path] = new_element
				self.path_docelement[parent_path].appendChild(new_element)
			parent_path = cum_path
		return
	def Print(self, filename=None):
		filename = filename if filename != None else self.filename
		ofs = open(filename,'w')
		ofs.write(self.doc.toprettyxml(indent='\t'))
		ofs.close()
		return




