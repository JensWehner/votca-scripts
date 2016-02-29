import sys
import argparse
from lxml import etree

class ExtendableNamespace(argparse.Namespace):
	def AddNamespace(self,  **kwargs):
		for name in kwargs:
			att = getattr(self, name, None)
			if att is None:
				setattr(self, name, kwargs[name])
			else:
				setattr(self, name, kwargs[name].As(type(att)))
		return
	def Add(self, name, value):
		att = getattr(self, name, None)
		if att is None:
			setattr(self, name, value)
		else:
			if type(att) != list:
				setattr(self, name, [att, value])
			else:
				att.append(value)
				setattr(self, name, att)
		return value

def GenerateTreeDict(tree, element, path='', paths_rel_to=None, verbose=False):
	if type(element) == etree._Comment: return [], {}
	# Update path
	if path == '':
		if element.tag != paths_rel_to:
			path += element.tag
	else:
		path += '/' + element.tag
	if verbose: print "Path =", path
	# Containers for lower levels
	tag_node = {}
	nodes = []
	# Construct Node
	xmlnode = XmlNode(element, path, tree) # tree.getpath(element))
	nodes.append(xmlnode)
	if len(element) == 0:
		tag_node[path] = xmlnode
	else:
		if verbose: print "len 0", xmlnode.path
		tag_node[path] = xmlnode
	# Iterate over children
	for child in element:
		if verbose: print "Child tag, ... =", child.tag, child.text, child.attrib
		child_elements, childtag_element = GenerateTreeDict(tree, child, path)
		nodes = nodes + child_elements
		for key in childtag_element.keys():
			if tag_node.has_key(key):
				if type(tag_node[key]) != list:
					tag_node[key] = [ tag_node[key], childtag_element[key] ]
				else:
					tag_node[key].append(childtag_element[key])
			else:
				tag_node[key] = childtag_element[key]
	return nodes, tag_node

def NamespaceFromDict(tree_dict):
	nspace = ExtendableNamespace()
	for key in tree_dict.keys():
		sections = key.split('/')
		values = [ None for s in sections ]
		values[-1] = tree_dict[key]
		add_to_nspace = nspace
		for s,v in zip(sections, values):
			if v == None:
				sub_nspace = ExtendableNamespace()
				add_to_nspace = add_to_nspace.Add(s, sub_nspace)
			else:
				add_to_nspace.Add(s, v)
	return nspace		

class XmlNode(object):
	# ACCESS LXML::ELEMENT MEMBERS VIA
		# self.node.tag		
		# self.node.text
		# self.node.attrib
	def __init__(self, element, path, tree):		
		self.path = path
		self.node = element		
		self.tag_child = {}
		for child in self.node:
			if not self.tag_child.has_key(child.tag):
				self.tag_child[child.tag] = []
			self.tag_child[child.tag].append(XmlNode(child, path+'/'+child.tag, tree))
		return
	# OPERATOR OVERLOADING (), []
	def __call__(self, to_type=str, split=None):
		if split:
			return [ to_type(s) for s in self.node.text.split(split) ]
		else:
			return to_type(self.node.text)
	def __getitem__(self, key):
		return self.GetUnique(key)
	def keys(self):
		return self.tag_child.keys()
	# GET METHODS
	def GetAll(self, tag):
		return self.tag_child[tag]
	def GetUnique(self, tag):
		if not self.tag_child.has_key(tag):
			raise ValueError("Invalid <XmlNode::Get> request, no such path: '%s'" % tag)
		elif len(self.tag_child[tag]) > 1:
			raise RuntimeError("Ambiguous <XmlNode::Get> request, path: '%s'" % tag)
		else: 
			return self.tag_child[tag][0]
	def GetValue(self, tag, to_type=str):
		node = self.GetUnique(tag)
		return to_type(node.node.text)

class XmlTree(XmlNode):
	def __init__(self, xmlfile=None):
		self.xmlfile = xmlfile
		self.xtree = etree.parse(xmlfile)
		self.xroot = self.xtree.getroot()
		XmlNode.__init__(self, self.xroot, '', self.xtree)

if __name__ == "__main__":
	xmlfile = sys.argv[1]
	
	tree = XmlTree(xmlfile)	
	jobs = tree.GetAll('job')
	
	for job in jobs:
		print job['status']()
		print job['id'](int)
		print job['tag'](str, ':')
		
	root = etree.Element('root')
	for job in jobs:
		if job['status']() == 'AVAILABLE':
			root.append(job.node)
	print etree.tostring(root, pretty_print=True)
	
	



