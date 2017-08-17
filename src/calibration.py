# -*- coding: utf-8 -*-
import pickle
import cv2
import numpy as np
class fish_calibration(object):
    def __init__(self,img_size):
        data=pickle.load(open('cam_calibration.p','rb'))
        #data=pickle.load(open("C:\\Users\\nuc\\Desktop\\src\\cam_calibration.p",'rb'))
        mtx=data['mtx']
        dist=data['dist']
        dist=np.array([dist[0][0], dist[0][1], dist[0][2], dist[0][3], dist[0][4]/1.45])
        #640x480为标定用图像分辨率
        newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(640,480),0.2,img_size)
        self.mapx,self.mapy = cv2.initUndistortRectifyMap(mtx,dist,None,newcameramtx,img_size,5)

    def cali(self,frame):       
        return cv2.remap(frame,self.mapx,self.mapy,cv2.INTER_LINEAR)