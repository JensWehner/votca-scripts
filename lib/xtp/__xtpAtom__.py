import numpy as np
import numpy.linalg as lg

class atom:

    def __init__(self,name,pos):
        self.type=name
        self.pos=pos    
        self.rank=0
        self.q=0
        self.d=np.zeros(3)
        self.quad=np.zeros(5)
        self.pol=np.zeros([3,3])

    def setmultipoles(self,q,d,quad,pol):
        self.q=q        
        self.d=d
       
        self.quad=quad
        self.detrank()
        self.pol=pol

    def detrank(self):
        rank=0
        if any(self.d!=0):
            rank=1
        if any(self.quad!=0):
            rank=2
        self.rank=rank

    def shift(self,shift):
        #print self.pos
        #print shift
        self.pos+=shift
        #print self.pos


    def xyzline(self):
        return "{:<3s} {:.6f} {:.6f} {:.6f}\n".format(self.type,self.pos[0],self.pos[1],self.pos[2])



    def mpsentry(self):
        self.detrank
        entry="{:>3s} {:+.7f} {:+.7f} {:+.7f} Rank {:d}\n    {:+.7f}\n".format(self.type,self.pos[0],self.pos[1],self.pos[2],self.rank,self.q)
        pline="     P {:+.7f} {:+.7f} {:+.7f} {:+.7f} {:+.7f} {:+.7f}\n".format(self.pol[0,0],self.pol[0,1],self.pol[0,2],self.pol[1,1],self.pol[1,2],self.pol[2,2])
        if self.rank>0:
            entry+="    {:+.7f} {:+.7f} {:+.7f}\n".format(self.d[0],self.d[1],self.d[2])
        if self.rank>1:
            entry+="    {:+.7f} {:+.7f} {:+.7f} {:+.7f} {:+.7f}\n".format(self.quad[0],self.quad[1],self.quad[2],self.quad[3],self.quad[4])
        entry+=pline
        return entry
