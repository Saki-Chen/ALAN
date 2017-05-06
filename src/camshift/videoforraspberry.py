# -*- coding: UTF-8 -*-  
#树莓派用，使用时请改名video
from picamera import PiCamera
import numpy as np
class mypicamera(PiCamera):
    def __init__(
            self, camera_num=0, stereo_mode='none', stereo_decimate=False,
            resolution=None, framerate=None, sensor_mode=0, led_pin=None,
            clock_mode='reset', framerate_range=None):
        super(mypicamera,self).__init__(
            camera_num, stereo_mode, stereo_decimate,resolution, framerate, sensor_mode, led_pin,
            clock_mode, framerate)
    def read(self, format='bgr', use_video_port=True, resize=None, splitter_port=0, bayer=False, **options):
        img=np.empty((self.resolution[1]*self.resolution[0]*3,), dtype=np.uint8)
        flag=False
        try:
            self.capture(img,format, use_video_port, resize, splitter_port, bayer, **options)
        except:
            raise Exception('摄像头读取失败')
        else:
            img=img.reshape((self.resolution[1],self.resolution[0],3))
            flag=not flag
        return (flag,img)

    def release(self):
        self.close()
        del self

def create_capture(source = 0):
    pcam=mypicamera(source)
    pcam.resolution=(1280,720)
    pcam.framerate=60
    return mypicamera(source)