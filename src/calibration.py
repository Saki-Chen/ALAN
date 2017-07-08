# -*- coding: utf-8 -*-

import cv2
import numpy as np
class fish_calibration(object):
    def __init__(self,frame):
        self.mtx=np.array([[374.67766648,               0.,    298.18696809],
                  [          0.,     374.41912695,    214.30454882],
                  [          0.,               0.,             1. ]])
        self.dist=np.array([[ -3.29607823e-01,   9.94071879e-02,   1.69540168e-03,  -1.61912063e-04,-2.33603492e-03]])
        h, w = frame.shape[:2]
        self.newcameramtx, self.roi = cv2.getOptimalNewCameraMatrix(self.mtx,self.dist,(w,h),1,(w,h)) 
    def cali(self,frame):       
        dst = cv2.undistort(frame,self.mtx,self.dist,None,self.newcameramtx)  
        x,y,w,h = self.roi  
        return dst[y:y+h,x:x+w]