# -*- coding: UTF-8 -*- 
import cv2
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

    return (theta,D)
    

def snap(src,p1,p2,k1=5,k2=1.2,adjustX=1.4,adjustY=1.1):
    x1,y1=p1
    x2,y2=p2
    R=array((x2-x1,y2-y1))
    L=linalg.norm(R)
    x3=x1+k2*R[1]
    y3=y1-k2*R[0]
    pts1=float32([[x1,y1],[x2,y2],[x3,y3]])
    pts2=float32([[0,k2*L],[L,k2*L],[0,0]])    
    M = cv2.getAffineTransform(pts1,pts2)
    dst = cv2.warpAffine(src,M,(int(k1*L),int(2*k2*L)))

    theta=None
    D=None

    if len(src.shape)==2:
        offsetX=int(L*adjustX)
        #offsetY=int(L*adjustY/2)
        avoid=cv2.resize(dst[:,offsetX:],(400-offsetX,200))
        cv2.imshow('avoid',avoid)
        #dst_0=cv2.resize(dst,(400,200))
        #cv2.imshow('snap_0',dst_0)
        #dst[int(k2*L)-offsetY:int(k2*L)+offsetY,:1]=0
        #dst[int(k2*L)-offsetY:int(k2*L)+offsetY,:offsetX]=0
        p3=get_centroid(dst[:,offsetX:])
        #p3=get_centroid(dst)
        if p3 is not None:
            p3=(p3[0]+offsetX,p3[1])
            theta,D =get_direction((0,int(k2*L)),(int(L),int(k2*L)),p3)
            D=int(128*(D-1)/(k1-1))
            #D=256*D/k1
    return (theta,D,dst)

def get_centroid(img_bin):
    _ ,contours, hierarchy = cv2.findContours(img_bin,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
    target=None
    area=160
    for cnt in contours:
        M= cv2.moments(cnt)
        if M['m00']>area:
            area=M['m00']
            target=(int(M['m10']/M['m00']),int(M['m01']/M['m00']))
    return target




if __name__=='__main__':
    print get_direction((0,0),(0.,3.),(4.,0.))