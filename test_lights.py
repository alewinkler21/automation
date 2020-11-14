#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import sys

pins = [23]

def test():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    for p in pins:
        print("prendemos led " + `p`)
        GPIO.setup(p, GPIO.OUT)
        GPIO.output(p, GPIO.HIGH)
        time.sleep(3)

    for p in pins:
        print("apagamos led " + `p`)
        GPIO.output(p, GPIO.LOW)
        time.sleep(3)

    GPIO.cleanup()

try:
    test()
except KeyboardInterrupt:
    GPIO.cleanup()
    sys.exit()
