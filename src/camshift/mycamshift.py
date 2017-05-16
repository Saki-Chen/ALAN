# -*- coding: UTF-8 -*-  
import cv2
import numpy as np


class mycamshift(object):
    """description of class"""
    def __init__(self,ID=0): 
        self.ID=ID
        self.__framesize=None
        self.__track_window=None
        self.__hist=None
        self.prob=None
  
    @staticmethod
    def filte_color(hsv,lower_hsv=np.array((0., 85., 85.)),higher_hsv=np.array((179., 255., 255.)), iterations=3):
        #mask_area=cv2.inRange(hsv,np.array((100.,30.,30.)),np.array((124.,255.,255.)))
        #mask_area=cv2.morphologyEx(mask_area,cv2.MORPH_BLACKHAT,cv2.getStructuringElement(cv2.MORPH_RECT,(5,5)),iterations=iterations, borderType=cv2.BORDER_REPLICATE)
        #mask_area=cv2.bitwise_not(mask_area)
        #hsv=cv2.medianBlur(hsv,5)
        mask1 = cv2.inRange(hsv, lower_hsv, np.array((95.,higher_hsv[1],higher_hsv[2])))
        mask2=cv2.inRange(hsv, np.array((130.,lower_hsv[1],lower_hsv[2])), higher_hsv )
        mask=cv2.add(mask1,mask2)
        #mask=cv2.medianBlur(mask,5)
        #cv2.imshow('temp',mask)
        return mask

    def prProcess_light(self,frame):
        self.__framesize=(frame.shape[0],frame.shape[1])
        self.__track_window=(0,0,frame.shape[1],frame.shape[0])

    def preProcess(self,hsv,mask,selection,n=16):     
        if selection is None:
            return False
        x0, y0, x1, y1 = selection
        if x0==x1 or y0==y1:
            return False
        hsv_roi = hsv[y0:y1, x0:x1]
        mask_roi = mask[y0:y1, x0:x1]
        hist = cv2.calcHist( [hsv_roi], [0], mask_roi, [n], [0, 180] )
        cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)
        self.__hist = hist.reshape(-1)       
        self.__track_window=(x0,y0,x1-x0,y1-y0)
        self.__framesize=(hsv.shape[0],hsv.shape[1])
        return True

    def getHist(self):
        if self.__hist is None:
            return None
        bin_count = self.__hist.shape[0]
        bin_w = 24
        img = np.zeros((256, bin_count*bin_w, 3), np.uint8)
        for i in xrange(bin_count):
            h = int(self.__hist[i])
            cv2.rectangle(img, (i*bin_w+2, 255), ((i+1)*bin_w-2, 255-h), (int(180.0*i/bin_count), 255, 255), -1)
        return cv2.cvtColor(img, cv2.COLOR_HSV2BGR)


    def adj_window(self,win,n):
        x=win[0]-win[2]*n
        y=win[1]-win[3]*n
        dx=win[2]*(n*2+1)
        dy=win[3]*(n*2+1)
        if x<0:
            x=0
        if y<0:
            y=0
        if x+dx>self.__framesize[1]:
            dx=self.__framesize[1]-x
        if y+dy>self.__framesize[0]:
            dy=self.__framesize[0]-y
        return (x,y,dx,dy)


    def go_once(self,hsv,mask):
        if not(self.__track_window and self.__track_window[2] > 0 and self.__track_window[3] > 0):
            raise Exception('跟踪窗未定义或者出错')
        self.prob = cv2.calcBackProject([hsv], [0], self.__hist, [0, 180], 1)
        self.prob &= mask
        term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )
        track_box, self.__track_window = cv2.CamShift(self.prob, self.__track_window, term_crit)
        area=track_box[1][0]*track_box[1][1];
        self.__track_window=self.adj_window(self.__track_window,1)
        if(area<5):
            #print('Target %s is Lost' % self.ID)
            #self.__track_window=(0,0,self.__framesize[1],self.__framesize[0])
            return None
        return track_box

    def go_once_gray(self,img_gray):
        if not(self.__track_window and self.__track_window[2] > 0 and self.__track_window[3] > 0):
            raise Exception('跟踪窗未定义或者出错')
        
        #小心这条语句能过滤一些反光点，也能把灯滤掉，注意调节kernel大小和iterations
        img_gray=cv2.morphologyEx(img_gray,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_RECT,(3,3)),iterations=2, borderType=cv2.BORDER_REFLECT)     
        self.prob = img_gray
        term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )
        track_box, self.__track_window = cv2.CamShift(self.prob, self.__track_window, term_crit)
        area=track_box[1][0]*track_box[1][1];
        if(area<5):
            #print('Target %s is Lost' % self.ID)
            #self.__track_window=(0,0,self.__framesize[1],self.__framesize[0])
            return None
        return track_box




