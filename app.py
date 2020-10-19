#!flask/bin/python

from neopixel import *
import argparse
from led import *

from flask import Flask, request, jsonify


app = Flask(__name__)
global led

@app.route('/color-solid')
def colorSolidRest():
    return led.animate(LightType.SOLID, getColor())

@app.route('/color-wipe')
def colorWipeRest():
    return led.animate(LightType.WIPE, getColor())

@app.route('/color-join')
def colorJoinRest():
    return led.animate(LightType.JOIN, getColor())

@app.route('/rainbow')
def rainbowRest():
    return led.animate(LightType.RAINBOW)

@app.route('/loading')
def loadingRest():
    return led.animate(LightType.LOADING, getColor(), getSpeed())


def getColor():
    red = request.args.get('red')
    green = request.args.get('green')
    blue = request.args.get('blue')
    return LedColor(int(red), int(green), int(blue))

def getSpeed():
    return int(request.args.get('speed'))


LED_COUNT = 33
LED_PIN = 18
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 255
LED_INVERT = False
LED_CHANNEL = 0


if __name__ == '__main__':
    strip = Adafruit_NeoPixel(33, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    led = Led(strip)
    app.run(debug=True, host='0.0.0.0')
