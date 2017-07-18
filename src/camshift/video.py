# -*- coding: UTF-8 -*- 

import numpy as np
import cv2
import time

def create_capture(source = 0):
    #cap = cv2.VideoCapture('http://192.168.40.146:8000/stream.mjpg')
    #cap = cv2.VideoCapture(source)
    cap = cv2.VideoCapture(source)
    time.sleep(2)
    
    cap.set(cv2.CAP_PROP_SETTINGS, 1)
    #AWC=cap.get(cv2.CAP_PROP_AUTOFOCUS)
    
    #AWC=cap.get(cv2.CAP_PROP_IOS_DEVICE_WHITEBALANCE)
    #print AWC
    return cap

if __name__=='__main__':
    from fps import FPS
    fps = FPS().start()
    cap = cv2.VideoCapture(1)
    #cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640);  
    #cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480);  
    time.sleep(2)
    #print cap.set(cv2.CAP_PROP_WHITE_BALANCE_BLUE_U,4000)
    
    
    #AWC=cap.set(cv2.CAP_PROP_FPS,0)
    while True:
        _,frame=cap.read()
        #print cap.get(cv2.CAP_PROP_XI_AUTO_WB)
        f = fps.approx_compute()
        cv2.putText(frame, 'FPS {:.3f}'.format(f), (10, 10),cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255),1, cv2.LINE_AA) 
        cv2.imshow('test',frame)
        ch = cv2.waitKey(2)
        if ch == 27:
            break
        if ch==ord('r'):
            fps.reset()
    cap.release()