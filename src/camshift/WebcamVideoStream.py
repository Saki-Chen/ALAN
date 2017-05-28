# import the necessary packages
from threading import Thread
import cv2

class WebcamVideoStream:
    def __init__(self, src=0):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.address=src
        self.stream = cv2.VideoCapture(src)
        #self.stream.set(3, resolution[0])
        #self.stream.set(4, resolution[1])
        (self.grabbed, self.frame) = self.stream.read()
        self.renew=False
        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return

            # otherwise, read the next frame from the stream        
            while True:
                (self.grabbed, self.frame) = self.stream.read()
                if self.grabbed:
                    self.renew=True
                    break
                else:
                    self.stream.release()       
                    self.stream=cv2.VideoCapture(self.address)
                    print('connection break')

    def read(self):
        # return the frame most recently read
        self.renew=False
        return self.grabbed, self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
    def release(self):
        self.stop()
       
