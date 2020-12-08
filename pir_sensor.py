#!/usr/bin/env python3

import sys
import RPi.GPIO as GPIO
import time
import os
import django
import pytz
from django.utils import timezone
from datetime import datetime, timedelta
from dateutil.parser import parse as parseDate
from threading import Thread
import logger as logger
import redis
from picamera import PiCamera
import signal
import subprocess
# from notify import notify

# setup django in order to use models
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "raspberry.settings")
django.setup()
from automation.models import LightState, Relay, RelayAction, PirSensor, Alarm

pirSensors = []
timeZone = pytz.timezone("America/Montevideo")
sharedMemory = redis.Redis(host='127.0.0.1', port=6379, db=0)
mediaPath = "/var/www/html/camera/"

def isLit():
    try:
        light_state = LightState.objects.latest()
    except LightState.DoesNotExist:
        light_state = None
    return light_state is None or not light_state.isDark

def saveDeviceAction(device, status, tmstmp):
    action = RelayAction()
    action.dateOfUse = tmstmp
    action.status = status
    action.isAutomatic = True
    action.relay = device
    action.save()
    # set device status
    device.status = status
    device.save()

def initSensors():
    global pirSensors
    pirSensors = PirSensor.objects.filter(enabled=True, address='127.0.0.1')
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    for d in pirSensors:
        # set the pin as output and value to off 
        GPIO.setup(d.pinNumber, GPIO.OUT)
        GPIO.output(d.pinNumber, GPIO.LOW)
        time.sleep(0.1)
        # change the pin back to input
        GPIO.setup(d.pinNumber, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

class DevicesTimer(Thread):
    def run(self):
        global timeZone
        while True:
            logger.debug("Let's check what to turn off")
            devices = Relay.objects.filter(enabled=True, autoEnabled=True, address='127.0.0.1', status=True)
            now = datetime.now(tz=timeZone)
            for d in devices:
                turnOffSavedDatetime = sharedMemory.get(d.address + '-' + str(d.id))
                if turnOffSavedDatetime:
                    turnOffDatetime = parseDate(str(turnOffSavedDatetime, 'UTF-8'))
                    if now >= turnOffDatetime:
                        logger.debug("Turning off and removing automated device: " + str(d))
                        GPIO.setup(d.pinNumber, GPIO.OUT)
                        GPIO.output(d.pinNumber, GPIO.LOW)
                        saveDeviceAction(d, False, now)
                        # remove automated device
                        sharedMemory.delete(d.address + '-' + str(d.id))
                else:
                    logger.debug("Automated device is not in shared memory:" + str(d))
            time.sleep(2)

class PIRSensorMonitor(Thread):
   
    def __init__(self, sensor):
        super(PIRSensorMonitor, self).__init__()
        self.sensor = sensor
       
    def toggleRelays(self):
        if not self.sensor.checkLighting or not isLit():
            if self.sensor.checkLighting:
                logger.debug("The environment is dark")
            
            devices = Relay.objects.filter(enabled=True, autoEnabled=True, address='127.0.0.1')
            now = datetime.now(tz=timeZone)
            for d in devices:
                # turn on device
                GPIO.setup(d.pinNumber, GPIO.OUT)
                GPIO.output(d.pinNumber, GPIO.HIGH)
                # save event
                saveDeviceAction(d, True, now)
                # set automatic turn off
                longTimeStart = timeZone.localize(datetime.combine(now, d.longTimeStart))
                longTimeEnd = timeZone.localize(datetime.combine(now, d.longTimeEnd)) if d.longTimeEnd > d.longTimeStart else timeZone.localize(datetime.combine(now + timedelta(days=1), d.longTimeEnd))
                if now >= longTimeStart and now < longTimeEnd:
                    turnOffDatetime = now + timedelta(seconds=d.longTimeDuration)
                else:
                    turnOffDatetime = now + timedelta(seconds=d.shortTimeDuration)
                if sharedMemory.set(d.address + '-' + str(d.id), str(turnOffDatetime)):
                    logger.debug("Set automatic turn off for device: {} longTimeStart: {} longTimeEnd: {} Off: {}".format(d.name,  
                                                                                                                          longTimeStart.strftime("%Y-%m-%d %H:%M:%S"), 
                                                                                                                          longTimeEnd.strftime("%Y-%m-%d %H:%M:%S"),
                                                                                                                          turnOffDatetime.strftime("%Y-%m-%d %H:%M:%S")))
                else:
                    logger.error("Set automatic turn off failed for device {}".format(d.name))
        else:
            if self.sensor.checkLighting:
                logger.debug("The environment is lit")
            #             alarm = Alarm.objects.last()
            #             if alarm.armed:
            #                 triggerAlarm()
          
    def triggerAlarm(self, alarm):
        logger.debug("Alarm triggered")
        alarm.fired = True
        alarm.save()
        if alarm.useCamera:
            camera = PiCamera()
            fileName = datetime.now(tz=timeZone).strftime("%Y_%m_%d_%H_%M_%S")
            # photos
            for i in range(3):
                logger.debug("Take picture {}".format(i))
                camera.capture("{}{}-{}.jpg".format(mediaPath, fileName, i))
                time.sleep(1)
            # video
            logger.debug("Start recording video")
            camera.start_recording("{}{}.h264".format(mediaPath, fileName))
            time.sleep(30)
            camera.stop_recording()
            logger.debug("Stop recording video")
            camera.close()
            logger.debug("Release camera")
            subprocess.run(["MP4Box", "-add", "{}{}.h264".format(mediaPath, fileName), "{}{}.mp4".format(mediaPath, fileName)], stdout=subprocess.DEVNULL)
            os.remove("{}{}.h264".format(mediaPath, fileName))

    def run(self):
        global timeZone
        previous_state = False
        while True:
            # turn off the led
            if self.sensor.led:
                GPIO.setup(self.sensor.led.pinNumber, GPIO.OUT)
                GPIO.output(self.sensor.led.pinNumber, GPIO.LOW)
            movement = GPIO.input(self.sensor.pinNumber) == 1
            if movement:
                if movement != previous_state:  # avoid repeating the same signal
                    logger.debug("Movement detected in " + str(self.sensor.pinNumber))
                    # turn on the led
                    if self.sensor.led:
                        GPIO.output(self.sensor.led.pinNumber, GPIO.HIGH)
                    self.toggleRelays()
                    alarm = Alarm.objects.last()
                    if alarm and alarm.armed:
                        self.triggerAlarm(alarm)
                else:
                    logger.debug("Movement ignored")
            else:
                logger.debug("No movement")
            previous_state = movement
            time.sleep(1)

def main():
    initSensors()
    
    for d in pirSensors:
        pirSensorMonitor = PIRSensorMonitor(d)
        pirSensorMonitor.setDaemon(True)
        pirSensorMonitor.start()
    
    devicesTimer = DevicesTimer()
    devicesTimer.setDaemon(True)
    devicesTimer.start()
    
    devicesTimer.join()

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

# def triggerAlarm():
#     if notify("Alarma disparada"):
#         alarm = Alarm()
#         alarm.fired = True
#         alarm.save()

