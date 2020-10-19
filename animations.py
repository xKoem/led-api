from neopixel import *
from enum import Enum
import time

class LedColor:
    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue
    
    def neoPixelColor(self):
        return Color(self.blue, self.red, self.green)

class LightType(Enum):
    WIPE = 1
    SOLID = 2
    RAINBOW = 3
    LOADING = 4
    JOIN = 5

def getAnimation(strip, lightType, color, speed):
    if lightType is LightType.WIPE:
        return Wipe(strip, color)
    elif lightType is LightType.SOLID:
        return Solid(strip, color)
    elif lightType is LightType.JOIN:
        return Join(strip, color)
    elif lightType is LightType.RAINBOW:
        return Rainbow(strip)
    elif lightType is LightType.LOADING:
        return Loading(strip, color, speed)

def wheel(pos):
    if pos < 85:
        return LedColor(pos *3, 255 - pos * 3, 0)
    if pos < 170:
        pos -= 85
        return LedColor(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return LedColor(0, pos * 3, 255 - pos * 3)


class Animation:
    def __init__(self, strip, color = LedColor(0, 0, 0), speed = 5):
        self.strip = strip
        self.color = color
        self.speed = speed
        self.killed = False
        self.wait_ms = 20

    def kill(self):
        self.killed = True

    def animate(self):
        pass

class Solid(Animation, object): 
    def __init__(self, strip, color):
        super(Solid, self).__init__(strip, color)

    def animate(self):
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, self.color.neoPixelColor())
        self.strip.show()


class Wipe(Animation, object): 
    def __init__(self, strip, color):
        super(Wipe, self).__init__(strip, color)

    def animate(self):
          for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, self.color.neoPixelColor())
            self.strip.show()
            time.sleep(self.wait_ms/1000.0)


class Join(Animation, object): 
    def __init__(self, strip, color):
        super(Join, self).__init__(strip, color)

    def animate(self):
        for i in range(self.strip.numPixels()):
            if self.killed:
                return
            for j in range (self.strip.numPixels() - i):
                for k in range(j):
                    self.strip.setPixelColor(k, Color(0,0,0))
                self.strip.setPixelColor(j, self.color.neoPixelColor())
                self.strip.show()
                time.sleep(self.wait_ms/1000.0)


class Rainbow(Animation, object): 
    def __init__(self, strip):
        super(Rainbow, self).__init__(strip)

    def animate(self):
        while True:
            for j in range(256):
                for i in range(self.strip.numPixels()):
                    self.strip.setPixelColor(i, wheel((int(i * 256 / self.strip.numPixels()) + j)& 255).neoPixelColor())
                    if self.killed == True:
                        return
                self.strip.show()
                time.sleep(self.wait_ms/1000.0)


class Loading(Animation, object): 
    def __init__(self, strip, color, speed):
        super(Loading, self).__init__(strip, color, speed)

    def animate(self):
        while True:
            for i in range(self.strip.numPixels()) + range(self.strip.numPixels() - 2, 0, -1):
                    for j in range(self.strip.numPixels()):
                        if self.killed == True:
                            return
                        self.strip.setPixelColor(j, Color(0, 0, 0))
                    self.strip.setPixelColor(i, self.color.neoPixelColor())
                    self.strip.show()
                    time.sleep(float(self.wait_ms)/self.speed)
