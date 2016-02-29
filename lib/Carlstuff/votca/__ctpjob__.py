from __pyosshell__ import *
import xml.dom.minidom as xml


class XmlNodeValue(object):
	def __init__(self, path, value, attributes):
		self.path = path
		self.value = value
		self.attributes = attributes
	def As(self, typ):
		if typ == np.array:
			sps = self.value.split()
			return typ([ float(sp) for sp in sps ])
		else:
			return typ(self.value)


def GenerateNodeDict(node,path=''):
	path_value = {}
	if node.firstChild == None: return {}
	if node.firstChild.nodeValue.split() != []:
		value = XmlNodeValue(path, node.firstChild.nodeValue, node.attributes) 
		path_value[path] = value
		path_value['.%s' % node.nodeName] = value	
	for child in node.childNodes:
		if path == '': childPath = child.nodeName
		else: childPath = '%s.%s' % (path, child.nodeName)
		add_dict = GenerateNodeDict(child, childPath)
		for key in add_dict.keys():
			path_value[key] = add_dict[key]	
	return path_value


class Batch(object):
	def __init__(self, xmlfile = None):
		self.jobs = []
		if xmlfile != None:
			tree = xml.parse(xmlfile)
			for node in tree.getElementsByTagName('job'):
				self.jobs.append(Job(node=node))
		return
	def AddJob(self, jobTag, jobInput):
		jobId = len(self.jobs)+1
		newJob = Job(jobId,jobTag,jobInput)
		self.jobs.append(newJob)
		return
	def WriteToFile(self, outFile = 'jobs.xml'):
		if outFile in os.listdir('./'):
			print "Already exists:", os.getcwd(), outFile
			sys.exit(1)
		outt = open(outFile,'w')
		outt.write('<jobs>\n')
		for job in self.jobs:
			job.WriteToStream(outt)
		outt.write('</jobs>\n')
		outt.close()
		return


class Job(object):
	def __init__(self, id_ = None, tag_ = None, input_ = None, node = None):
		self.id_ 		= id_
		self.tag_ 		= tag_
		self.input_ 	= input_
		self.status_ 	= 'AVAILABLE'
		self.time_ 		= None
		self.host_ 		= None
		self.output_ 	= None
		self.error_ 	= None		
		self.node_      = node
		if node != None:
			self.LoadFromXmlNode(node)
		return	
	def LoadFromXmlNode(self, node):
		self.id_ = node.getElementsByTagName('id')[0].firstChild.nodeValue
		self.tag_ = node.getElementsByTagName('tag')[0].firstChild.nodeValue
		self.input_ = node.getElementsByTagName('input')[0].firstChild.nodeValue
		status = node.getElementsByTagName('status')
		if status == []: self.status_ = 'AVAILABLE'
		else: self.status_ = status[0].firstChild.nodeValue
		time = node.getElementsByTagName('time')
		if time == []: self.time_ = None
		else: self.time_ = time[0].firstChild.nodeValue
		host = node.getElementsByTagName('host')
		if host == []: self.host_ = None
		else: self.host_ = host[0].firstChild.nodeValue
		output = node.getElementsByTagName('output')
		if output == []: self.output_ = None
		else: self.output_ = output[0].firstChild.nodeValue
		error = node.getElementsByTagName('error')
		if error == []: self.error_ = None
		else: 
			if self.status_ == 'COMPLETE':				
				try:
					self.error_ = error[0].firstChild.nodeValue
					print "Has error", self.id_, self.tag_, self.input_, ":", self.error_
				except AttributeError:
					#print "Has error", self.id_, self.tag_, self.input_, ", yet complete."
					pass
		return
	def WriteToStream(self, ofs):
		# TODO Extend this function to incorporate output, timestamp, ...
		ofs.write('<job>\n')
		ofs.write('\t<id>%d</id>\n' % self.id_)
		ofs.write('\t<tag>%s</tag>\n' % self.tag_)
		ofs.write('\t<input>%s</input>\n' % self.input_)
		ofs.write('</job>\n')
		return

		
	
		
	
	












