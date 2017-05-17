# -*- coding: UTF-8 -*- 
import cv2
import numpy as np
# local module
from udp.myudp import MyUdp
from camshift.mycamshift import mycamshift
from camshift.analyze import *
import camshift.video as video
import time
class App(object):
    def __init__(self, video_src):
        #树莓派ip
        self.server_address='http://192.168.40.146:8000/stream.mjpg'
        #self.server_address='udp://@:8000 --demux=h264'
        self.cam = video.create_capture(self.server_address)
        ret, self.frame = self.cam.read()
        self.drag_start = None
        self.list_camshift=[]
        self.show_backproj = False
        self.newcamshift=None
        self.selection=None
        self.lock=False
        self.mdp=MyUdp()
        #self.count=0
        self.light=self.get_light()

        #self.list_camshift.append(self.get_car('red.jpg',0))
        #self.list_camshift.append(self.get_car('green.jpg',1))

        #wifi模块IP
        self.mdp.client_address=('192.168.40.31', 8899)  
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
    
    @staticmethod
    def creat_camshift_from_img(hsv):
        camshift=mycamshift()
        mask=np.ones((hsv.shape[0],hsv.shape[1]),dtype=np.uint8)
        camshift.preProcess(hsv,mask,(0,0,hsv.shape[1],hsv.shape[0]),32)
        return camshift

    def get_light(self):
        temp=mycamshift()
        temp.prProcess_light(self.frame)
        temp.ID=99
        return temp
    
    def get_car(self,file,ID):
        img=cv2.imread(file,cv2.IMREAD_UNCHANGED)
        img=cv2.resize(img,(self.frame.shape[1],self.frame.shape[0]))       
        hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
        temp=App.creat_camshift_from_img(hsv)
        cv2.imshow(str(ID),temp.getHist())
        temp.ID=ID

        return temp

        
    def run(self):
        while True:  
            while True:
                ret, self.frame = self.cam.read()
                if ret:
                    break
                else:
                    self.cam.release()
                    self.cam=video.create_capture(self.server_address)
                    print('connection break')
            hsv=cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)
            mask,mask_car=mycamshift.filte_background_color(hsv,iterations=3)

            if self.newcamshift is not None:
                if self.newcamshift.preProcess(hsv,mask,self.selection,32):
                    cv2.imshow(str(ll),self.newcamshift.getHist())   

            self.lock=False
            ll=len(self.list_camshift) 
            if ll>0:
                light_gray=cv2.cvtColor(self.frame,cv2.COLOR_BGR2GRAY)
                mean,temp = cv2.threshold(light_gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

                _,light_gray=cv2.threshold(light_gray,(255-mean)*0.8+mean,255,cv2.THRESH_BINARY)
                light_gray=cv2.morphologyEx(light_gray,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)),iterations=2, borderType=cv2.BORDER_REPLICATE)
        
                cv2.imshow('light',light_gray)
                
                track_box=[self.light.go_once_gray(light_gray)]
                
                for x in self.list_camshift:
                    track_box.append(x.go_once(hsv,mask_car))             

                n=len(track_box)
                if n>2:
                    p3=track_box[0]
                    p1,p2=track_box[n-2:]
                    try:
                        p1=p1[0]
                    except:
                        p1=None
                    try:
                        p2=p2[0]
                    except:
                        p2=None
                    try:
                        p3=p3[0]
                    except:
                        p3=None
                    if p1 and p2:
                        try:
                            #snap(img,p1,p2,障碍侦测范围，障碍侦测宽度，微调：避免将车头识别为障碍)
                            theta,D,dst=snap(mask,p1,p2,4.5,1.0,1.53)
                            dst=cv2.resize(dst,(400,200))
                            cv2.imshow('snap',dst)
                            if theta is not None:
                                print('Block ahead')
                                print((theta,D))
                                self.mdp.send_message('avoid',(theta,D))

                            elif p3:
                                t,d=get_direction(p1,p2,p3)
                                mes=(int(t),int(d))
                                self.mdp.send_message('guidance',mes)
                                print('guidance')
                                print mes
                        except:
                            print('0/0 is error')
                            self.mdp.send_message('lost')
                    else:
                        print('lost')
                        self.mdp.send_message('lost')

                else:
                    print('lost')
                    self.mdp.send_message('lost')
                prob=self.list_camshift[ll-1].prob
                if self.show_backproj and prob is not None:
                    self.frame=prob[...,np.newaxis]

                for x in track_box:
                    try:
                        cv2.ellipse(self.frame, x, (0, 0, 255), 2) 
                    except:
                        pass
                        #print(track_box)

            else:
                print('lost')
                self.mdp.send_message('lost')
            self.lock=True  
            
            if self.selection is not None:
                x0, y0, x1, y1 = self.selection
                vis_roi = self.frame[y0:y1, x0:x1]
                cv2.bitwise_not(vis_roi, vis_roi)
              
            cv2.imshow('TUCanshift',self.frame)
            #print (str(self.count))
            #self.count=self.count+1
            ch = cv2.waitKey(2)
            if ch == 27:
                break
            if ch==ord('b'):
                self.show_backproj=not self.show_backproj


            #data, addr = self.mdp.recv_message()
            #data=MyUdp.getdata(data)
            #if data:
            #    print "received:", data, "from", addr

        cv2.destroyAllWindows()
        self.cam.release()
        self.mdp.close()


if __name__=='__main__':
    App(0).run()