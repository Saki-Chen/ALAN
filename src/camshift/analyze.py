# -*- coding: UTF-8 -*- 
#由p1指向p2的矢量为小车定位矢量，由p1指向p3的矢量为目标定位矢量
#数据格式为 \xAA\xBB\x55\x01\x04\x00\x11\角度位\距离位\校验位
#角度格式为左正右赋值,取值-128~127
#距离为相对距离，即目标定位矢量与小车定位矢量的长度之比，取值0~255，超过255取255

from numpy import linalg
from numpy import *

def get_direction(point1,point2,point3):
    #p=(x,y)  p1,p2为车上点  p3为灯
    R1=(array(point2)-array(point1))
    R2=(array(point3)-array(point1))
    L1=linalg.norm(R1)
    L2=linalg.norm(R2)
    theta=arccos(inner(R1,R2)/(L1*L2))

    ou=outer(R1,R2)
    if ou[0][1]-ou[1][0]<0:
       theta=theta-pi
    theta=theta/2./pi*256

    D=L2/L1
    if D>255:
        D=255

    return (int(theta),int(D))
    

#if __name__=='__main__':
#    print get_direction((0,0),(0.,3.),(4.,0.))