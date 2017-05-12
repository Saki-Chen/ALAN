# -*- coding: UTF-8 -*- 
import cv2
import numpy as np
# local module
from udp.myudp import MyUdp
from camshift.mycamshift import mycamshift
from camshift.analyze import get_direction
import camshift.video as video

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
        
        self.light=self.get_light()
        
        self.list_camshift.append(self.get_car('red.jpg',0))
        self.list_camshift.append(self.get_car('green.jpg',1))

        #wifi模块IP
        self.mdp.client_address=(MyUdp.getlocalIP(), 8899)  
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
        #hsv尺寸应和视频尺寸一致
        camshift=mycamshift()
        mask=mycamshift.filte_color(hsv,np.array((0.,0.,0.)),np.array((180.,255.,255.)))
        camshift.preProcess(hsv,mask,(0,0,hsv.shape[1],hsv.shape[0]),32)
        return camshift

    def get_light(self):
        #img=cv2.imread('light.jpg',cv2.IMREAD_UNCHANGED)
        #img=cv2.resize(img,(self.frame.shape[1],self.frame.shape[0]))
        #hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
        #hsv=cv2.resize(hsv,(self.frame.shape[1],self.frame.shape[0]))
        #temp=App.creat_camshift_from_img(hsv)
        temp=mycamshift()
        temp.prProcess_light(self.frame)
        temp.ID=99
        return temp
    
    def get_car(self,file,ID):
        img=cv2.imread(file,cv2.IMREAD_UNCHANGED)
        img=cv2.resize(img,(self.frame.shape[1],self.frame.shape[0]))
        
        hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
        #hsv=cv2.resize(hsv,(self.frame.shape[1],self.frame.shape[0]))
        temp=App.creat_camshift_from_img(hsv)
        cv2.imshow(str(ID),temp.getHist())
        temp.ID=ID

        return temp

        
    def run(self):
        while True:  
            ret, self.frame = self.cam.read()
            hsv=cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)
            #hsv=cv2.pyrDown(hsv,dstsize=(self.frame.shape[1]/2,self.frame.shape[0]/2))
            #hsv=cv2.pyrUp(hsv,dstsize=(self.frame.shape[1],self.frame.shape[0]))
            mask=mycamshift.filte_color(hsv,np.array((0.,80.,80.)),np.array((179.,255.,255.)))
            if self.newcamshift is not None:
                if self.newcamshift.preProcess(hsv,mask,self.selection,32):
                    cv2.imshow(str(ll),self.newcamshift.getHist())   

            self.lock=False
            ll=len(self.list_camshift) 
            if ll>0:
                light_mask=mycamshift.filte_color(hsv,np.array((0., 0., 250.)),np.array((179., 255., 255.)))
                track_box=[self.light.go_once_gray(light_mask)]
                cv2.imshow('light',self.light.prob)
                for x in self.list_camshift:
                    track_box.append(x.go_once(hsv,mask))             

                prob=self.list_camshift[ll-1].prob
                if self.show_backproj and prob is not None:
                    self.frame=prob[...,np.newaxis]

                for x in track_box:
                    try:
                        cv2.ellipse(self.frame, x, (0, 0, 255), 2) 
                    except:
                        pass
                        #print(track_box)
                n=len(track_box)
                if n>2:
                    p1,p2=track_box[n-2:]
                    p3=track_box[0]
                    if p1 and p2 and p3 and not p1[0]==(0,0):
                        try:
                            mes=get_direction(p1[0],p2[0],p3[0])
                        except:
                            raise Exception('坐标数值错误')
                        else:
                            self.mdp.send_message('guidance',mes)
                            print mes
                    else:
                        self.mdp.send_message('lost')

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


            #data, addr = self.mdp.recv_message()
            #data=MyUdp.getdata(data)
            #if data:
            #    print "received:", data, "from", addr

        cv2.destroyAllWindows()
        self.cam.release()
        self.mdp.close()


if __name__=='__main__':
    App(0).run()