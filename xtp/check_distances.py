#!usr/bin/python

import numpy as np
import sqlite3
import argparse
import sys

parser=argparse.ArgumentParser(description="Checks pairs for dR diferrences")
parser.add_argument("-f","--file", default="system.sql",type=str,help="Statefile,default:system.sql")

args=parser.parse_args()

def readSqlall(sqlname):
	sqlstatement = "SELECT pairs.drX,pairs.drY, pairs.drZ, seg1.posX,seg1.posY,seg1.posZ, seg2.posX,seg2.posY,seg2.posZ FROM pairs JOIN segments seg1 ON seg1._id =pairs.seg1 JOIN segments seg2 ON seg2._id =pairs.seg2"
	con = sqlite3.connect(sqlname)
	with con:
		cur = con.cursor()
		cur.execute(sqlstatement)
		rows = cur.fetchall()
	sqlall=(np.array(rows))
	return sqlall

def getBox(sqlname):
	sqlstatement="SELECT box11,box12,box13,box21,box22,box23,box31,box32,box33 FROM frames"
	con = sqlite3.connect(sqlname)
	with con:
		cur = con.cursor()
		cur.execute(sqlstatement)
		rows = cur.fetchall()
	sqlall=(np.array(rows))
	return sqlall



sql=readSqlall(args.file)
box=getBox(args.file)
box=np.reshape(box,(3,3))
test=np.diag(np.diag(box))
print "Box has dimensions:"
print box
if not np.allclose(box,test):
	print "Box is not orthogonal. Exiting"
	sys.exit()
box=np.diag(box)
dr=sql[:,:3]
pos1=sql[:,3:6]
pos2=sql[:,6:]
drnew=pos2-pos1
factor=(drnew-dr)%box
pairid=0
isfine=True

for f,d,dn in zip(factor,dr,drnew):
	if not np.allclose(f,np.zeros(3)):
		print "For pair {} segment dR and pair dR differ".format(pairdid)," segmentdR=",dn," pairdR=",d
		isfine=False
	pairid+=1

if isfine:
	print "Statefile has only correct pairs"
else:
	print "Statefile has weird pairs. Something went wrong"



	




