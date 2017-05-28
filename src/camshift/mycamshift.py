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
        self.HSV_CHANNELS = (
            (24, [0, 180], "hue"),  # Hue
            (8, [0, 256], "sat"),  # Saturation
            (8, [0, 256], "val")  # Value
        )
        self.kernel_erode = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,
                                                                          3))
        self.kernel_dilate = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7,
                                                                           7))

    def calcHSVhist(self, hsvRoi,mask_roi):
        self.histHSV = []
        for channel, param in enumerate(self.HSV_CHANNELS):
            # Init HSV histogram
            hist = cv2.calcHist([hsvRoi], [channel], mask_roi, [param[0]],
                                param[1])
            hist = cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)
            self.histHSV.append(hist)
            # Show hist of each channel separately
            #self.show_hist(hist, param[2])
 

    def calcBackProjection(self,hsv):
        ch_prob = []
        ch_back_proj_prob = []
        # back_proj_prob = np.ones(shape=(self.height, self.width), dtype=np.uint8) * 255
        # back_proj_prob = np.zeros(shape=(self.height, self.width), dtype=np.uint8)

        for channel, param in enumerate(self.HSV_CHANNELS):
            prob = cv2.calcBackProject([hsv], [channel],
                                       self.histHSV[channel], param[1], 1)
            #cv2.imshow('Back projection ' + str(param[2]), prob)
            
            # ret, prob = cv2.threshold(prob, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            ret, prob = cv2.threshold(prob, 100, 255, cv2.THRESH_BINARY)
            #cv2.imshow('Back projection thresh ' + str(param[2]), prob)
            
            # prob = cv2.morphologyEx(prob, cv2.MORPH_ERODE, self.kernel_erode, iterations=2)
            # prob = cv2.morphologyEx(prob, cv2.MORPH_DILATE, self.kernel_dilate, iterations=3)
            # back_proj_prob = cv2.bitwise_and(back_proj_prob, prob)
            # back_proj_prob = cv2.addWeighted(back_proj_prob, 0.4, prob, 0.6, 0)
            ch_prob.append(prob)

        ch_back_proj_prob.append(
            cv2.addWeighted(ch_prob[0], 0.5, ch_prob[1], 0.5, 0))
        cv2.imshow('cb1', ch_back_proj_prob[0])
        ch_back_proj_prob.append(
            cv2.addWeighted(ch_prob[0], 0.6, ch_prob[2], 0.4, 0))
        cv2.imshow('cb2', ch_back_proj_prob[1])




        #_,ch_back_proj_prob[0] = cv2.threshold(ch_back_proj_prob[0], 70, 255,
        #                                    cv2.THRESH_BINARY)
        #_,ch_back_proj_prob[1] = cv2.threshold(ch_back_proj_prob[1], 70, 255,
        #                                    cv2.THRESH_BINARY)


        #back_proj_prob = cv2.bitwise_and(ch_back_proj_prob[0],
        #                                 ch_back_proj_prob[1])


        #back_proj_prob = cv2.addWeighted(ch_prob[0], 0.5, ch_prob[2], 0.2, 0)
        #back_proj_prob = cv2.addWeighted(back_proj_prob,1,ch_prob[1],0.3,0)
        #back_proj_prob= cv2.medianBlur(back_proj_prob,5)
        #min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(back_proj_prob)
        #max_val=int(max_val/2)
        #if max_val<120:
        #    max_val=120
        
        #print('max:%s  avg:%s' % (max_val,avg))
        #_,back_proj_prob = cv2.threshold(back_proj_prob,max_val,255,cv2.THRESH_BINARY)
        #cv2.imshow('expe',back_proj_prob)

        back_proj_prob=cv2.add(ch_back_proj_prob[0],ch_back_proj_prob[1])
        cv2.imshow('pre',back_proj_prob)




        #back_proj_prob=cv2.addWeighted(ch_prob[0], 0.7, ch_prob[2], 0.3, 0)
        #back_proj_prob=cv2.addWeighted(ch_back_proj_prob[0],0.6,ch_back_proj_prob[1],0.4,0)
        #back_proj_prob=ch_back_proj_prob[0]
        #back_proj_prob=ch_prob[2]
        #Acht!
        ret, back_proj_prob = cv2.threshold(back_proj_prob,230, 255,
                                            cv2.THRESH_BINARY)

        back_proj_prob = cv2.morphologyEx(
            back_proj_prob, cv2.MORPH_ERODE, self.kernel_erode, iterations=4)
        back_proj_prob = cv2.morphologyEx(
            back_proj_prob, cv2.MORPH_DILATE, self.kernel_erode, iterations=4)

        return back_proj_prob    
        
             

    @staticmethod
    def filte_background_color(hsv,offset1=30.,offset2=256., iterations=3):
        #mask_area=cv2.inRange(hsv,np.array((100.,30.,30.)),np.array((124.,255.,255.)))
        #mask_area=cv2.morphologyEx(mask_area,cv2.MORPH_BLACKHAT,cv2.getStructuringElement(cv2.MORPH_RECT,(5,5)),iterations=iterations, borderType=cv2.BORDER_REPLICATE)
        #mask_area=cv2.bitwise_not(mask_area)
        #hsv=cv2.medianBlur(hsv,5)
        H_hist = cv2.calcHist([hsv],[0], None,[180],[0,180])
        H = H_hist.argmax(axis=None, out=None)
        S_hist = cv2.calcHist([hsv],[1], None,[255],[0,255])
        S = S_hist.argmax(axis=None, out=None)
        #V_hist = cv2.calcHist([hsv],[2], None,[255],[0,255])
        #V = V_hist.argmax(axis=None, out=None)

        mask = cv2.inRange(hsv, np.array((H-offset1,S-offset2,0.)), np.array((H+offset1,S+offset2,255.)))

        #mask_rid=cv2.morphologyEx(mask,cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_CROSS,(5,5)), iterations=10, borderType=cv2.BORDER_REPLICATE)
        #cv2.imshow('mask_rid',mask_rid)
        mask,contours,_hierary=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        mask_rid=mask.copy()
        mask_rid[:,:]=0
        cv2.drawContours(mask_rid,contours,-1,255,thickness=-1)  
        #cv2.imshow('rid',mask_rid)

        #area=0
        #cnt=None
        #con=cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)
        #l=len(contours)
        #for i in xrange(l):
        #    temp=con.copy()
        #    cv2.drawContours(temp,contours,i,(0,0,255),thickness=cv2.FILLED) 
        #    cv2.imshow('c%s'%str(i),temp) 
        #for c in contours:
        #    temp=cv2.contourArea(c)
        #    if temp > area:
        #        area=temp
        #        cnt=c
        #if cnt is not None:
        #    con=cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)
        #    cv2.drawContours(con,contours,-1,(255,255,255),thickness=-1)  
        #    cv2.imshow('con',con)
            #mask_rid=mask.copy()
            #cv2.drawContours(mask_rid,cnt,-1,255,-1)  
            #cv2.imshow('mr',mask_rid)






        
        mask=cv2.bitwise_not(mask)
        mask&=mask_rid
        #mask=cv2.medianBlur(mask,5)
        mask=cv2.morphologyEx(mask,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_RECT,(2,2)),iterations=iterations, borderType=cv2.BORDER_REPLICATE)

       
        #hsv_mask=cv2.bitwise_and(hsv,hsv,mask=mask)
        #mask_car=cv2.inRange(hsv_mask,np.array((0.,0.,5.)),np.array((180.,255.,255.)))
        #mask_car=cv2.morphologyEx(mask_car,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_RECT,(4,4)),iterations=iterations, borderType=cv2.BORDER_REPLICATE)


        #mask1 = cv2.inRange(hsv, np.array((0.,30.,10.)), np.array((H-offset1,255.,255.)))
        #mask2=cv2.inRange(hsv, np.array((H+offset1,30.,10.)), np.array((180.,255.,255.)) )
        #mask_car=cv2.add(mask1,mask2)
        #mask_car=cv2.morphologyEx(mask_car,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_RECT,(3,3)),iterations=iterations-1, borderType=cv2.BORDER_REPLICATE)


        #cv2.imshow('hsv_mask',hsv_mask)
        #cv2.imshow('mask_car',mask_car)
        cv2.imshow('fore_ground',mask)
        #return mask,mask_car
        return mask

    def prProcess_light(self,frame):
        self.__framesize=(frame.shape[0],frame.shape[1])
        self.__track_window=(0,0,frame.shape[1],frame.shape[0])

    def preProcess(self,hsv,mask,selection,n=32):     
        if selection is None:
            return False
        x0, y0, x1, y1 = selection
        if x0==x1 or y0==y1:
            return False
        hsv_roi = hsv[y0:y1, x0:x1]
        mask_roi = mask[y0:y1, x0:x1]

        self.calcHSVhist( hsv_roi,mask_roi)
        
        hist=self.histHSV[0]
        h_max=hist.argmax(axis=None, out=None)
        h_max_left=h_max-1
        h_max_right=h_max+1
        if h_max_left<0:
            h_max_left=self.HSV_CHANNELS[0][0]-1
        if h_max_right>self.HSV_CHANNELS[0][0]-1:
            h_max_right=0
        hist[h_max_left]=hist[h_max]
        hist[h_max_right]=hist[h_max]

        #hist = cv2.calcHist( [hsv_roi], [0], mask_roi, [n], [0, 180] )
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
        #self.prob = cv2.calcBackProject([hsv], [0], self.__hist, [0, 180], 1)
        self.prob=self.calcBackProjection(hsv)
        self.prob &= mask
        #_,self.prob=cv2.threshold(self.prob,10,255,cv2.THRESH_BINARY)
        cv2.imshow('prob',self.prob)
        term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )
        track_box, self.__track_window = cv2.CamShift(self.prob, self.__track_window, term_crit)
        area=track_box[1][0]*track_box[1][1];
        #self.__track_window=self.adj_window(self.__track_window,3)
        if(area<25):
            print('Target %s is Lost' % self.ID)
            self.__track_window=(0,0,self.__framesize[1],self.__framesize[0])
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
        if(area<45):
            print('Target %s is Lost' % self.ID)
            self.__track_window=(0,0,self.__framesize[1],self.__framesize[0])
            return None
        return track_box




