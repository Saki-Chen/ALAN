import picamera.Picamera
class mypicamera(Picamera):
    def __init__(
            self, camera_num=0, stereo_mode='none', stereo_decimate=False,
            resolution=None, framerate=None, sensor_mode=0, led_pin=None,
            clock_mode='reset', framerate_range=None):
        Picamera.__init__(
            self, camera_num=camera_num, stereo_mode=stereo_mode, stereo_decimate=stereo_decimate,
            resolution=resolution, framerate=framerate, sensor_mode=sensor_mode, led_pin=led_pin,
            clock_mode=clock_mode, framerate_range=framerate)
    def read(self):
        #你实现下树莓派读一张图，存到numpy数组，并返回
        pass
    
def create_capture(source = 0):
    return mypicamera(source)