#!/usr/bin/python

import lxml.etree as lxml
import argparse as ap
import os

parser=ap.ArgumentParser(description="Assign mpsfile to molecules for iexciotn jobs, mps.tab files and ewald jobs")
parser.add_argument("--path",type=str,required=True,help="Path to mps file folder")
parser.add_argument("--jobfile",type=str,required=True,help="file to rewrite")
parser.add_argument("--state",type=str,required=True,help="Defines the state e.g. n,n2s1,s1")
parser.add_argument("--suffix",type=str,help="Ending for mps files in folder, defaults to state if not specified")

args=parser.parse_args()

#if "s" in args.state:
#	args.state+args.state.replace("s","s1")

if args.suffix==None:
	args.suffix=args.state


filetype= os.path.splitext(args.jobfile)[1][1:]
if filetype=="jobs":
	parser=lxml.XMLParser(remove_comments=True)
	tree = lxml.parse(args.jobfile,parser)
	root = tree.getroot()
	for job in root.iter('job'): 
		inputs=job.find('input')
		for segment in inputs:
			segid=segment.get('id')
			segtype=segment.get('type')
			mpsfile=os.path.join(args.path,"{}_{}_{}.mps".format(segtype,args.suffix,segid))
			segment.set('mps_file',mpsfile)

	with open(args.jobfile, 'w') as f:
		f.write(lxml.tostring(root, pretty_print=True))

elif filetype=="xml":
	parser=lxml.XMLParser(remove_comments=True)
	tree = lxml.parse(args.jobfile,parser)
	root = tree.getroot()
	for job in root.iter('job'):
		inputs=job.find('input')
		tags=job.find("tag")
		tags=tags.text.split(":")
		segid=int(tags[0])
		name=tags[1]
		state=tags[2]
		if state==args.state:
			mpsfile=os.path.join(args.path,"{}_{}_{}.mps".format(name,args.suffix,segid))
			mpsfile="{}:{}:{}".format(segid,name,mpsfile)
			inputs.text=mpsfile

	with open(args.jobfile, 'w') as f:
		f.write(lxml.tostring(root, pretty_print=True))


elif filetype=="tab":
	content=[]
	with open(args.jobfile,"r") as f:
		for line in f.readlines():
			if line[0]=="#":
				content.append(line)
			else:
				entries=line.split()
				segid=int(entries[0])
				segtype=entries[1]
				line="{} {} {} {} {}\n".format(segid,segtype,os.path.join(args.path,"{}_{}_{}.mps".format(segtype,args.suffix,segid)),entries[3],entries[4])
				content.append(line)

	with open(args.jobfile,'w') as f:
		for line in content:
			f.write(line)


