#!flask/bin/python

from neopixel import *
import argparse

from flask import Flask, request, jsonify
import threading
import time
from Queue import Queue
from enum import Enum

LED_COUNT = 120
LED_PIN = 18
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 255
LED_INVERT = False
LED_CHANNEL = 0

class LightType(Enum):
    WIPE = 1
    SOLID = 2
    RAINBOW = 3
    LOADING = 4

class Type:
    def __init__(self, lightType, color=Color(0, 0, 0), speed=10):
        self.lightType = lightType
        self.color = color
        self.speed = speed

threads = []
helperThreads = []

def color(red, green, blue):
    return Color(blue, red, green)


def wheel(pos):
    if pos < 85:
        return color(pos *3, 255 - pos * 3, 0)
    if pos < 170:
        pos -= 85
        return color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return color(0, pos * 3, 255 - pos * 3)


print_lock = threading.Lock()
class MyThread(threading.Thread):

    def colorWipe(self, strip, color, wait_ms=20):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, color)
            strip.show()
            time.sleep(wait_ms/1000.0)

    def solidColor(self, strip, color):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, color)
        strip.show()


    def __init__(self, queue, strip, args=None, kwargs=None):
        threading.Thread.__init__(self, args=None, kwargs=None)
        self.queue = queue
        self.strip = strip
        self.daemon = True

    def run(self):
        print(threading.currentThread().getName())
        while True:
            typ = self.queue.get()
            self.do_thing_with_message(typ)
            time.sleep(0.1)


    def do_thing_with_message(self, typ):
        if len(helperThreads) > 0:
            helperThreads[0].kill()
            helperThreads[0].join()
            helperThreads.pop(0)

        if typ.lightType == LightType.WIPE:
            self.colorWipe(self.strip, typ.color)
        elif typ.lightType == LightType.SOLID:
            self.solidColor(self.strip, typ.color)
        elif typ.lightType == LightType.RAINBOW:
            helperThreads.append(AnimationThread(self.strip, typ.lightType))
            helperThreads[0].start()
            time.sleep(0.1)
        elif typ.lightType == LightType.LOADING:
            helperThreads.append(AnimationThread(self.strip, typ.lightType, typ.speed, typ.color))
            helperThreads[0].start()
            time.sleep(0.1)


class AnimationThread(threading.Thread):
    def __init__(self, strip, lightType, speed=10, color=color(0, 0, 0), args=None, kwargs=None):
        threading.Thread.__init__(self, args=None, kwargs=None)
        self.daemon = True
        self.strip = strip
        self.lightType = lightType
        self.speed = speed
        self.color = color
        self.killed = False

    def kill(self):
        self.killed = True

    def run(self):
        while not self.killed:
            if self.lightType == LightType.RAINBOW:
                self.rainbowCycle(self.strip)
            elif self.lightType == LightType.LOADING:
                self.loading(self.strip, self.speed)


    def rainbowCycle(self, strip, waitMs=10):
        for j in range(256):
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
                if self.killed == True:
                    return
            self.strip.show()
            time.sleep(waitMs/1000.0)
    

    def loading(self, strip, speed, waitMs=10.0):
        for i in range(self.strip.numPixels()) + range(self.strip.numPixels() - 2, 0, -1):
            for j in range(self.strip.numPixels()):
                if self.killed == True:
                    return
                self.strip.setPixelColor(j, color(0, 0, 0))
            self.strip.setPixelColor(i, self.color)
            self.strip.show()
            time.sleep(waitMs/self.speed)
            

app = Flask(__name__)

@app.route('/color-wipe')
def colorWipeRest():
    red = request.args.get('red')
    green = request.args.get('green')
    blue = request.args.get('blue')
    threads[0].queue.put(Type(LightType.WIPE, color(int(red), int(green), int(blue))))

    return "wipe"


@app.route('/color-solid')
def colorSolidRest():
    red = request.args.get('red')
    green = request.args.get('green')
    blue = request.args.get('blue')

    threads[0].queue.put(Type(LightType.SOLID, color(int(red), int(green), int(blue))))
    return "solid"


@app.route('/rainbow')
def rainbow():
    threads[0].queue.put(Type(LightType.RAINBOW))
    return "rainbow"


@app.route('/loading')
def loading():
    red = request.args.get('red')
    green = request.args.get('green')
    blue = request.args.get('blue')
    speed = request.args.get('speed')
    threads[0].queue.put(Type(LightType.LOADING, color(int(red), int(green), int(blue)), int(speed)))
    return "loading"


@app.route('/')
def index():
    threads[0].queue.put(Type(LightType.WIPE, color(127, 127, 127)))
    return "Hello m8"

if __name__ == '__main__':
    strip = Adafruit_NeoPixel(33, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()

    q = Queue()
    threads.append(MyThread(q, strip))
    threads[0].start()
    time.sleep(0.1)

    app.run(debug=True, host='0.0.0.0')