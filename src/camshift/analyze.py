# -*- coding: UTF-8 -*- 

from numpy import linalg
from numpy import *

def get_direction(point1,point2,point3):
    #p=(x,y)
    R1=(array(point2)-array(point1))
    R2=(array(point3)-array(point1))
    L1=linalg.norm(R1)
    L2=linalg.norm(R2)
    theta=arccos(inner(R1,R2)/(L1*L2))

    ou=outer(R1,R2)
    if ou[0][1]-ou[1][0]>0:
       theta=-theta
    theta=theta/2./pi*256

    D=L2/L1
    if D>255:
        D=255

    return (int(theta),int(D))
    

if __name__=='__main__':
    print get_direction((0,0),(0.,3.),(4.,0.))