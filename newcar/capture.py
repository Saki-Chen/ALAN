# -*- coding: utf-8 -*-
"""
Created on Fri May 19 17:30:02 2017

@author: ASUS
"""

import numpy as np
import cv2
import glob

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((6*7,3), np.float32)
objp[:,:2] = np.mgrid[0:7,0:6].T.reshape(-1,2)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

images = glob.glob('D://biaoding//*.jpg')

for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    size = gray.shape[::-1]  

    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, (7,6),None)
    print ret

    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp)

        corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
        imgpoints.append(corners2)

        # Draw and display the corners
        img = cv2.drawChessboardCorners(img, (7,6), corners2,ret)
        cv2.imshow('img',img)
        cv2.waitKey(500)

cv2.destroyAllWindows()
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints,size, None, None)  
  
print "ret:",ret  
print type(ret)
print "mtx:\n",mtx        # 内参数矩阵  
print type(mtx)
print "dist:\n",dist      # 畸变系数   distortion cofficients = (k_1,k_2,p_1,p_2,k_3)  
print type(dist)
print "rvecs:\n",rvecs    # 旋转向量  # 外参数  
print type(rvecs)
print "tvecs:\n",tvecs    # 平移向量  # 外参数  
print type(tvecs)
  
print("-----------------------------------------------------")  
# 畸变校正  
img = cv2.imread("D://biaoding/img0010.jpg")  
h, w = img.shape[:2]  
newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))  
print newcameramtx  
print("------------------使用undistort函数-------------------")  
dst = cv2.undistort(img,mtx,dist,None,newcameramtx)  
x,y,w,h = roi  
dst1 = dst[y:y+h,x:x+w]  
cv2.imwrite('D://calibresult11.jpg', dst1)  
print "方法一:dst的大小为:", dst1.shape  