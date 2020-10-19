from neopixel import *
import threading
from animations import *

class Led:
    def __init__(self, strip, args=None, kwargs=None): 
        self.strip = strip
        self.strip.begin()
        self.thread = None
    
    def animate(self, lightType, color = LedColor(0, 0, 0), speed = 5):
        self.stopProcessing()
        self.thread = StandardThread(getAnimation(self.strip, lightType, color, speed))
        self.thread.start()
        return lightType.name

    def stopProcessing(self):
        if self.thread is not None:
            self.thread.kill()
            self.thread.join()
            self.thread = None


class StandardThread(threading.Thread):
    def __init__(self, animation, args=None, kwargs=None):
        threading.Thread.__init__(self, args=None, kwargs=None)
        self.animation = animation
        self.daemon = True

    def kill(self):
        self.animation.kill()

    def run(self):
        self.animation.animate()
    
