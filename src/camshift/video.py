# -*- coding: UTF-8 -*- 

import numpy as np
import cv2


def create_capture(source = 0):
    cap = cv2.VideoCapture('http://172.27.35.2:8080/?action=stream?dummy=param.mjpg')
    #cap = cv2.VideoCapture(source)
    #cap = cv2.VideoCapture('http://192.168.40.146:8080/?action=stream?dummy=param.mjpg')
    return cap