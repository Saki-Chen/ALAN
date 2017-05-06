# -*- coding: UTF-8 -*-  
import cv2
import numpy as np
import copy  
import time
# local module
import video

class mycamshift(object):
    """description of class"""
    def __init__(self,ID=0): 
        self.ID=ID
        self.__framesize=None
        self.__track_window=None
        self.__hist=None
        self.prob=None
  
    @staticmethod
    def filte_color(frame,lower_hsv=np.array((0., 85., 85.)),higher_hsv=np.array((180., 255., 255.))):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_hsv, higher_hsv)
        return (hsv,mask)

    def preProcess(self,hsv,mask,selection,n=32):     
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


    def go_once(self,hsv,mask):
        if not(self.__track_window and self.__track_window[2] > 0 and self.__track_window[3] > 0):
            raise Exception('跟踪窗未定义或者出错')
        self.prob = cv2.calcBackProject([hsv], [0], self.__hist, [0, 180], 1)
        self.prob &= mask
        term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )
        track_box, self.__track_window = cv2.CamShift(self.prob, self.__track_window, term_crit)
        area=track_box[1][0]*track_box[1][1];
        if(area<5):
            print('Target %s is Lost' % self.ID)
            self.__track_window=(0,0,self.__framesize[1],self.__framesize[0])
        return track_box


class App(object):
    def __init__(self, video_src):
        self.cam = video.create_capture(video_src)
        ret, self.frame = self.cam.read()
        self.drag_start = None
        self.list_camshift=[]
        self.show_backproj = False
        self.newcamshift=None
        self.selection=None
        self.lock=False
        cv2.namedWindow('TUCanshift')
        cv2.setMouseCallback('TUCanshift', self.onmouse)

    def onmouse(self, event, x, y, flags, param):
        if self.lock:
            if event == cv2.EVENT_RBUTTONDOWN:
                self.pop_camshift()
                return
            if event == cv2.EVENT_LBUTTONDOWN:
                self.drag_start = (x, y)
                self.newcamshift=mycamshift()
            if self.drag_start:                  
                xmin = min(x, self.drag_start[0])
                ymin = min(y, self.drag_start[1])
                xmax = max(x, self.drag_start[0])
                ymax = max(y, self.drag_start[1])
                self.selection=(xmin, ymin, xmax, ymax)
            if event == cv2.EVENT_LBUTTONUP:
                self.drag_start = None
                if self.newcamshift is not None and self.newcamshift.getHist() is not None:
                    self.newcamshift.ID=len(self.list_camshift)
                    self.list_camshift.append(self.newcamshift)
                self.newcamshift=None
                self.selection=None

    def pop_camshift(self):
        if(len(self.list_camshift)<1):
            return True
        cv2.destroyWindow(str(len(self.list_camshift)-1))
        cv2.destroyWindow('%s%s' % ('cam',str(len(self.list_camshift)-1)))
        self.list_camshift.pop()
        return False
               
    def run(self):
        while True:  
            ret, self.frame = self.cam.read()
            hsv,mask=mycamshift.filte_color(self.frame)
            if self.newcamshift is not None:
                if self.newcamshift.preProcess(hsv,mask,self.selection):
                    cv2.imshow(str(ll),self.newcamshift.getHist())   

            self.lock=False
            ll=len(self.list_camshift) 
            if ll>0:
                track_box=[]
                for x in self.list_camshift:
                    track_box.append(x.go_once(hsv,mask))             

                prob=self.list_camshift[ll-1].prob
                if self.show_backproj and prob is not None:
                    self.frame=prob[...,np.newaxis]

                for x in track_box:
                    try:
                        cv2.ellipse(self.frame, x, (0, 0, 255), 2) 
                    except:
                        print(track_box)
            self.lock=True  
            
            if self.selection is not None:
                x0, y0, x1, y1 = self.selection
                vis_roi = self.frame[y0:y1, x0:x1]
                cv2.bitwise_not(vis_roi, vis_roi)
              
            cv2.imshow('TUCanshift',self.frame)
            ch = cv2.waitKey(2)
            if ch == 27:
                break
            if ch==ord('b'):
                self.show_backproj=not self.show_backproj

        cv2.destroyAllWindows()
        self.cam.release()


App(0).run()


