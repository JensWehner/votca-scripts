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

    def CartesianQuadrupoles(self):
        cartesian=np.zeros([3,3])
        sqrt3=np.sqrt(3)
        cartesian[0][0] = 0.5 * (sqrt3 * self.quad[3] - self.quad[0])
        cartesian[1][1] = -0.5 * (sqrt3 * self.quad[3] + self.quad[0]);
        cartesian[2][2] = self.quad[0];

        cartesian[0][1] = 0.5 * sqrt3 * self.quad[4];
        cartesian[1][0] = cartesian[0][1];

        cartesian[0][2] = 0.5 * sqrt3 * self.quad[1];
        cartesian[2][0] = cartesian[0][2];

        cartesian[1][2] = 0.5 * sqrt3 * self.quad[2];
        cartesian[2][1] = cartesian[1][2];

        return cartesian

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


    def splitup(self,spacing=0.01):
        multipolelist=[]
        m=atom(self.type,self.pos)
        m.setmultipoles(self.q,np.zeros(3),np.zeros(5),self.pol)
        multipolelist.append(m)

        if self.rank>0 and any(self.d!=0):
            cartesian=np.array([self.d[1],self.d[2],self.d[0]])
            norm=cartesian/np.linalg.norm(self.d)
            posA=self.pos+0.5*spacing*norm
            posB=self.pos-0.5*spacing*norm
            qA=np.linalg.norm(self.d)/spacing
            if np.absolute(qA) >1.e-9:
                qB=-qA
                d1=atom("D",posA);
                d1.setmultipoles(qA,np.zeros(3),np.zeros(5),np.zeros([3,3]))
                d2 = atom("D", posB);
                d2.setmultipoles(qB, np.zeros(3), np.zeros(5), np.zeros([3, 3]))
                multipolelist.append(d1)
                multipolelist.append(d2)
        if self.rank>1:
            cartesian=self.CartesianQuadrupoles()
            eigenval,eigenvec=np.linalg.eigh(cartesian)
            fullcharge=0
            for val,vec in zip(eigenval,eigenvec.T):
                q=1/3.0*val/(spacing**2)
                if np.absolute(q)<1.e-9:
                    continue
                vecA=self.pos+spacing*vec
                vecB = self.pos-spacing * vec
                q1 = atom("Q", vecA);
                q1.setmultipoles(q, np.zeros(3), np.zeros(5), np.zeros([3, 3]))
                q2 = atom("Q", vecB);
                q2.setmultipoles(q, np.zeros(3), np.zeros(5), np.zeros([3, 3]))
                multipolelist.append(q1)
                multipolelist.append(q2)
            quad=np.zeros([3,3])
            total=0
            for m in multipolelist:
                total+=m.q
                quad+=m.q*(1.5*np.outer(m.pos-self.pos,m.pos-self.pos)-0.5*np.identity(3)*(np.sum((m.pos-self.pos)**2)))
            print cartesian/quad
        return multipolelist




    def mpsentry(self):
        bohr2A=0.52917721092
        self.detrank()
        entry="{:>3s} {:+.7f} {:+.7f} {:+.7f} Rank {:d}\n    {:+.7f}\n".format(self.type,self.pos[0],self.pos[1],self.pos[2],self.rank,self.q)
        pline="     P {:+.7f} {:+.7f} {:+.7f} {:+.7f} {:+.7f} {:+.7f}\n".format(self.pol[0,0],self.pol[0,1],self.pol[0,2],self.pol[1,1],self.pol[1,2],self.pol[2,2])
        if self.rank>0:
            d=self.d/bohr2A
            entry+="    {:+.7f} {:+.7f} {:+.7f}\n".format(d[0],d[1],d[2])
        if self.rank>1:
            quad=self.quad/(bohr2A**2)
            entry+="    {:+.7f} {:+.7f} {:+.7f} {:+.7f} {:+.7f}\n".format(quad[0],quad[1],quad[2],quad[3],quad[4])
        entry+=pline
        return entry
