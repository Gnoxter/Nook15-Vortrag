#!/usr/bin/env python3
from pylibftdi import Device
import time
import numpy as np
import subprocess
from math import *
from PIL import Image
import sys
#
# Script to interface with a WS2812b LED Strip via a ftdi
# by jix
#
# SerialDisplay interfaces with the FTDI 
# MPVDisplay interfaces with mpv (mplayer fork) to display and test effect generators 
#
# Both take np.arrays with the form [width][height][color]
#
# Example to compose image from color arrays:
#
#    r = np.zeros([16,14])
#    g = np.zeros([16,14])
#    b = np.zeros([16,14])
#    image = np.transpose([r, g, b], [1, 2, 0])

 


class MPVDisplay:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.process = subprocess.Popen(
            'mpv --vo=opengl:scale=nearest --demuxer-rawvideo-w %i '
            '--demuxer-rawvideo-h %i --demuxer-rawvideo-mp-format=rgb24 '
            '--demuxer-rawvideo-fps 100 --no-cache '
            '--demuxer-thread=no --framedrop decoder '
            '--demuxer rawvideo -' % (width, height),
            shell=True, stdin=subprocess.PIPE)

        xcors = []
        ycors = []
        zcors = []
        for y in range(height):
            for x in range(width):
                for z in range(3):
                    xcors.append(x)
                    ycors.append(y)
                    zcors.append(z)

        self.xcors = np.array(xcors)
        self.ycors = np.array(ycors)
        self.zcors = np.array(zcors)

    def display(self, image):
        data = image[self.xcors, self.ycors, self.zcors]
        data = np.array(np.clip(data * 256, 0, 255), dtype=np.uint8)
        self.process.stdin.write(bytes(data.data))
        self.process.stdin.flush()


class SerialDisplay:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.codebook = SerialDisplay.create_codebook()

        self.xcors = []
        self.ycors = []
        self.pcors = []

        for y in range(height):
            for x in range(width):
                for p in range(8):
                    self.xcors.append(x if not (y & 1) else (width - 1 - x))
                    self.ycors.append(y)
                    self.pcors.append(p)


        self.dev = Device()
        self.dev.baudrate = 3010000
        self.dev.ftdi_fn.ftdi_set_line_property(7, 0, 0)

    def display(self, image):
        data = np.zeros([self.width * self.height * 8], dtype=np.uint8)
        data[:] = 0xFF
        image = np.array(np.clip(image * 255, 0, 255), dtype=np.uint8)

        for c in range(3):
            data &= self.codebook[c, image[self.xcors, self.ycors, c], self.pcors]

        self.dev.write(bytes(data.data))

    @staticmethod
    def format_byte(b0, b1, b2):
        return [(not b0) | (1 << 1) | ((not b1) << 3) | (1 << 4) | ((not b2) << 6)]

    @staticmethod
    def format_color(r, g, b):
        color = ((g & 0xFF) << 16) | ((r & 0xFF) << 8) | (b & 0xFF)

        result = []
        for i in range(8):
            trip = (color >> (24 - 3 * (i + 1))) & 7
            result += SerialDisplay.format_byte(trip & 4, trip & 2, trip & 1)
        return bytes(result)

    @staticmethod
    def create_codebook():
        codebook = np.zeros([3, 256, 8], dtype=np.uint8)
        for c in range(3):
            for p in range(8):
                for v in range(256):
                    m = [0, 0, 0]
                    m[c] = v
                    codebook[c, v, p] = SerialDisplay.format_color(*m)[p]
        return codebook




def rotor():
    x = np.ones([16,14])
    x[:,:] = np.reshape(np.arange(16) - 7.5, [16, 1])
    y = np.ones([16,14])
    y[:,:] = np.reshape(np.arange(14) - 6.5, [1, 14])

    q = 0
    t = 0

    while True:
        lt = t % 40
        pwr1 = pwr = 1 - lt / 40
        pwr **= 5
        pwr *= 2
        pwr = pwr + 0.5
        t += 1
        cx = sin(t * pi * 2 / 64 / 3) * 3
        cy = cos(t * pi * 2 / 64 / 3) * 3

        sgn = [1, -1][q % 2]

        df = np.hypot(x + cx, y + cy) / 32

        img = ((np.arctan2(x + cx, y + cy) / (pi * 2)) + ((sgn) * t / 64) + df * sgn * (0.4 - pwr1) ) % 1

        r = (1 - np.minimum(1, img * 12 % 4)) * pwr
        g = (1 - np.minimum(1, (img * 12 % 4) * 0.5)) * pwr
        b = (1 - np.minimum(1, (img * 12 % 4) * 0.3)) * pwr

        for i in range(q % 3):
            r, g, b = g, b, r
        if (q % 6) & 1 != ((q % 6) < 3):
            r, g = g, r

        if t % 40 == 0:
            q += 1


        img = np.transpose([r, g, b], [1, 2, 0])
        yield img, 0.015

def hsv_to_rgb(h, s, v):
    hi = np.floor_divide(h, 60)
    f = (h/60)-hi
    p = v*(1-s)
    q = v*(1-s*f)
    t = v*(1-s*(1-f))

    if hi == 0 or hi == 6:
        return v, t, p

    if hi == 1:
        return q, v, p

    if hi == 2:
        return p, v, t

    if hi == 3:
        return p, q, v

    if hi == 4:
        return t, p, v

    if hi == 5:
        return v, p, q


def simple():
    r = np.zeros([16,14])
    b = np.zeros([16,14])
    g = np.zeros([16,14])

    hue = 0
    while True:
        hue = (hue + 1) % 360
        r[:], g[:] , b[:]  = hsv_to_rgb(hue, 1,1)

        img = np.transpose([r, g, b], [1, 2, 0])
        yield img, 0.01



if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'mpv':
        gamma = 1.0
        disp = MPVDisplay(16, 14)
    else:
        gamma = 1.0
        disp = SerialDisplay(16, 14)

    next_time = time.time()
    #effect = rotor()
    effect = simple()

    for image, time_delta in effect:
        disp.display(image  ** gamma)
        next_time += time_delta
        time.sleep(max(0, next_time - time.time()))

