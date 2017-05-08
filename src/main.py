# -*- coding: UTF-8 -*- 
import cv2
import numpy as np
# local module
from udp.myudp import MyUdp
from camshift.mycamshift import mycamshift
from camshift.analyze import get_direction
import camshift.video as video

class find_light(object):
    def __init__(self, img):
        x0, y0, x1, y1=(0,0,img.shape[1],img.shape[0])
        hsv,mask=self.__pre(img,np.array((0., 0., 0.)),np.array((179., 255., 255.))) 
        hist = cv2.calcHist( [hsv], [0], mask, [16], [0, 180] )
        cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)
        self.__hist = hist.reshape(-1) 

        

    def __pre(self,frame,lower_hsv=np.array((0., 0., 221.)),higher_hsv=np.array((179., 30., 255.))):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv,lower_hsv,higher_hsv)
        return hsv,mask


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

    def find_light(self,frame,lower_hsv,higher_hsv):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask=cv2.inRange(hsv,lower_hsv,higher_hsv)
        mask=cv2.medianBlur(mask,5)
        cv2.imshow('light',mask)
        camshift_light=mycamshift()
        camshift_light.preProcess(hsv,mask)


    def find_light(self,frame,lower_hsv,higher_hsv):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask=cv2.inRange(hsv,lower_hsv,higher_hsv)
        mask=cv2.medianBlur(mask,5)
        cv2.imshow('light',mask)
        camshift_light=mycamshift()
        camshift_light.preProcess(hsv,mask)



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
        self.mdp=MyUdp()
        #wifi模块IP
        self.mdp.client_address=('192.168.1.103',8899)
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
            hsv,mask=mycamshift.filte_color(self.frame,np.array((0.,80.,80.)),np.array((179.,255.,255.)))
            if self.newcamshift is not None:
                if self.newcamshift.preProcess(hsv,mask,self.selection,16):
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
                n=len(track_box)
                if n>2:
                    p1,p2,p3=track_box[n-3:]
                    if p1[0] and p2[0] and p3[0]:
                        try:
                            mes=get_direction(p1[0],p2[0],p3[0])
                        except:
                            pass
                        else:
                            self.mdp.send_message('guidance',mes)
                            print mes

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


if __name__=='__main__':
    App(0).run()