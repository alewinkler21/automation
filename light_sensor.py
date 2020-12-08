#!/usr/bin/env python3

import sys
import RPi.GPIO as GPIO
import time
import os
import django
from queue import Queue
from threading import Thread
import logger as logger
import indicator as indicator
import signal

#setup django in order to use models
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "raspberry.settings")
django.setup()
from automation.models import LightState, LightSensor

lightSensors = []
queue = Queue()

def init():
    global lightSensors
    lightSensors = LightSensor.objects.filter(enabled=True, address='127.0.0.1')
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

def getLightSensorValue(pinLightSensor):
    # output on the pin for 
    GPIO.setup(pinLightSensor, GPIO.OUT)
    GPIO.output(pinLightSensor, GPIO.LOW)
    time.sleep(0.1)
    # change the pin back to input
    GPIO.setup(pinLightSensor, GPIO.IN)
    # count until the pin goes high or timeout
    count = 0
    sensorTimeOut = 10
    timedOut = False
    ts = time.time()
    while (GPIO.input(pinLightSensor) == GPIO.LOW and not timedOut):
        count += 1
        timedOut = (time.time() - ts) > sensorTimeOut
        time.sleep(0.1)
    if timedOut:
        logger.warning("Sensor timed out. Count is " + str(count))
    return count

class LightSensorMonitor(Thread):

    def __init__(self, sensor):
        super(LightSensorMonitor, self).__init__()
        self.sensor = sensor

    def run(self):
        global queue
        while True:
            brightness = getLightSensorValue(self.sensor.pinNumber)
            isDark = brightness > self.sensor.threshold
            try:
                lastLightState = LightState.objects.latest()
                logger.debug('Darkness last state:' + str(lastLightState.isDark) + ' ' + str(brightness))
                logger.debug('Darkness now:' + str(isDark) + ' ' + str(brightness))
            except LightState.DoesNotExist:
                lastLightState = None
            if lastLightState is None or lastLightState.isDark != isDark:
                # fire state changed event
                lightState = LightState()
                lightState.isDark = isDark
                lightState.brightness = brightness
                queue.put(lightState)
            time.sleep(1)
      
class LightSensorConsumer(Thread):
    def run(self):
        global queue
        while True:
            lightState = queue.get()
            queue.task_done()
            lightState.save()
            if lightState.isDark:
                indicator.setColor('blue')
            else:
                indicator.setColor('yellow')
            time.sleep(1)

def main():
    init()
    
    for d in lightSensors:
        lightSensorMonitor = LightSensorMonitor(d)
        lightSensorMonitor.setDaemon(True)
        lightSensorMonitor.start()
    
    lightSensorConsumer = LightSensorConsumer()
    lightSensorConsumer.setDaemon(True)
    lightSensorConsumer.start()
    
    lightSensorConsumer.join()

def terminateProcess(signalNumber, frame):
    print ('(SIGTERM) terminating the process')
    GPIO.cleanup()
    sys.exit()

if __name__ == '__main__':
    signal.signal(signal.SIGTERM, terminateProcess)
    try:
        main()
    except KeyboardInterrupt:
        GPIO.cleanup()
        sys.exit()
