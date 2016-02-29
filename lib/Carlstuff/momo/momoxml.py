import sys
import argparse
from lxml import etree		

class XmlNode(object):
	# ACCESS LXML::ELEMENT MEMBERS VIA
		# self.node.tag		
		# self.node.text
		# self.node.attrib
	def __init__(self, element, path, tree):		
		self.path = path
		self.node = element		
		self.tag_child = {}
		self.childs = []
		for child in self.node:
			if type(child.tag) != str: continue
			if not self.tag_child.has_key(child.tag):
				self.tag_child[child.tag] = []
			xmlnode = XmlNode(child, path+'/'+child.tag, tree)
			self.tag_child[child.tag].append(xmlnode)
			self.childs.append(xmlnode)
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
		if self.tag_child.has_key(tag):
			return self.tag_child[tag]
		else:
			return []
	def GetAllWhere(self, tag, key, value):
		candidates = []
		for child in self.tag_child[tag]:
			if key(child) == value:
				candidates.append(child)
		return candidates
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
	def DiveForAll(self, obj, boxed=[]):
		boxed = boxed + self.GetAll(obj)
		for child in self.childs:
			boxed = child.DiveForAll(obj, boxed)
		return boxed

class XmlTree(XmlNode):
	def __init__(self, xmlfile=None):
		self.xmlfile = xmlfile
		self.xtree = etree.parse(xmlfile)
		self.xroot = self.xtree.getroot()
		XmlNode.__init__(self, self.xroot, '', self.xtree)
	def GetRoot(self):
		return self.xroot

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
	
	



