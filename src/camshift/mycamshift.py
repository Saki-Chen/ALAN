# -*- coding: UTF-8 -*-  
import cv2
import numpy as np
import copy  
import time
# local module
import video

class mycamshift(object):
    """description of class"""
    def __init__(self,lower_hsv=np.array((0., 85., 85.)),higher_hsv=np.array((180., 255., 255.))):
        self.lower_hsv=lower_hsv
        self.higher_hsv=higher_hsv   
        self.__framesize=None
        self.show_backproj = False
        self.__track_window=None
        self.__hist=None

    def getTrack_window(self):
        return self.__track_window

    def __preCamshift(self,frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_hsv, self.higher_hsv)
        return [hsv,mask]

    def preProcess(self,frame,selection,n=32):     
        hsv,mask=self.__preCamshift(frame)
        x0, y0, x1, y1 = selection
        hsv_roi = hsv[y0:y1, x0:x1]
        mask_roi = mask[y0:y1, x0:x1]
        hist = cv2.calcHist( [hsv_roi], [0], mask_roi, [n], [0, 180] )
        cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)
        self.__hist = hist.reshape(-1)
       
        self.__track_window=(x0,y0,x1-x0,y1-y0)
        self.__framesize=(frame.shape[0],frame.shape[1])

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


    def go_once(self,inputframe):
        if not(self.__track_window and self.__track_window[2] > 0 and self.__track_window[3] > 0):
            return inputframe

        #选这句会黑，但其实是显示问题
        frame=copy.deepcopy(inputframe)
        #选这句显示正常，但两个框以上反向投影会黑
        #frame=inputframe


        hsv,mask=self.__preCamshift(frame)
        prob = cv2.calcBackProject([hsv], [0], self.__hist, [0, 180], 1)
        prob &= mask
        term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )
        track_box, self.__track_window = cv2.CamShift(prob, self.__track_window, term_crit)
        area=track_box[1][0]*track_box[1][1];
        if(area<5):
            print("Lost")
            self.__track_window=(0,0,self.__framesize[1],self.__framesize[0])
        if self.show_backproj:
            frame[:] = prob[...,np.newaxis]
        try:
            cv2.ellipse(frame, track_box, (0, 0, 255), 2)          
        except:
            print(track_box)
        return frame


class App(object):
    def __init__(self, video_src):
        self.cam = video.create_capture(video_src)
        ret, self.frame = self.cam.read()
        self.drag_start = None
        self.list_camshift=[]
        self.show_backproj = False
        self.newcamshift=None
        self.selection=None
        cv2.namedWindow('TUCanshift')
        cv2.setMouseCallback('TUCanshift', self.onmouse)

    def onmouse(self, event, x, y, flags, param):
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
            if self.newcamshift.getHist() is not None:
                self.list_camshift.append(self.newcamshift)
                self.newcamshift=None

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
            ll=len(self.list_camshift)
            if self.newcamshift is not None:
                self.newcamshift.preProcess(self.frame,self.selection)
                cv2.imshow(str(ll),self.newcamshift.getHist())   
                x0, y0, x1, y1 = self.selection
                vis_roi = self.frame[y0:y1, x0:x1]
                cv2.bitwise_not(vis_roi, vis_roi)
                cv2.imshow('TUCanshift',self.frame)       
            elif ll>0:
                #for x in self.list_camshift:  
                #    cv2.imshow('TUCanshift',x.go_once(self.frame))
                cv2.imshow('TUCanshift',self.frame)
                for i in xrange(len(self.list_camshift)):
                    #cv2.imshow('%s%s' % ('cam',str(i)),cv2.resize(self.list_camshift[i].go_once(self.frame),(640,480),interpolation=cv2.INTER_CUBIC))
                    cv2.imshow('%s%s' % ('cam',str(i)),self.list_camshift[i].go_once(self.frame))           
            else:
                cv2.imshow('TUCanshift',self.frame)
            ch = cv2.waitKey(5)
            if ch == 27:
                break
            if ch==ord('b'):
                self.show_backproj=not self.show_backproj
                for x in self.list_camshift:
                    x.show_backproj=self.show_backproj
 
        cv2.destroyAllWindows()
        self.cam.release()


App(0).run()


