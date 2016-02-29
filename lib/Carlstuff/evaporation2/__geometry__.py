from __future__ import division
import numpy as np


class Box(object):
    """An axis aligned box defined by an minimum and extend points (array/list like values)."""
    
    def __init__(self, origin=(0,0,0), extent=(1,1,1)):
        self.origin = np.array(origin)
        self.extent = np.array(extent)
        self.points = [origin, extent]
    
    def intersection(self, rpos, rdir):
        '''
        Amy Williams, Steve Barrus, R. Keith Morley, and
        Peter Shirley, "An Efficient and Robust Ray-Box Intersection Algorithm" Journal of
        graphics tools, 10(1):49-54, 2005
        Implementation from PVTRACE
        '''
        pts = [np.array(self.points[0]), np.array(self.points[1])]
        
        rinvd = [1.0/rdir[0], 1.0/rdir[1], 1.0/rdir[2]]
        rsgn = [1.0/rinvd[0] < 0.0, 1.0/rinvd[1] < 0.0, 1.0/rinvd[2] < 0.0]
        tmin = (pts[rsgn[0]][0] - rpos[0]) * rinvd[0]
        tmax = (pts[1-rsgn[0]][0] - rpos[0]) * rinvd[0]
        tymin = (pts[rsgn[1]][1] - rpos[1]) * rinvd[1]
        tymax = (pts[1-rsgn[1]][1] - rpos[1]) * rinvd[1]
        
        if (tmin > tymax) or (tymin > tmax):
            return None
            
        if tymin > tmin:
            tmin = tymin
            
        if tymax < tmax:
            tmax = tymax
            
        tzmin = (pts[rsgn[2]][2] - rpos[2]) * rinvd[2]
        tzmax = (pts[1-rsgn[2]][2] - rpos[2]) * rinvd[2]
        
        if (tmin > tzmax) or (tzmin > tmax):
            return None            
        if tzmin > tmin:
            tmin = tzmin            
        if tzmax < tmax:
            tmax = tzmax
        
        hit_coordinates = []
        pt1 = rpos + tmin * rdir
        pt2 = rpos + tmax * rdir
        
        if tmin >= 0.0:
            hit_coordinates.append(pt1)        
        if tmax >= 0.0:
            hit_coordinates.append(pt2)
        if len(hit_coordinates) == 0:
            return None
        
        return hit_coordinates










