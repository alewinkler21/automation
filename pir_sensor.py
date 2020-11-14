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
# from notify import notify

# setup django in order to use models
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "raspberry.settings")
django.setup()
from automation.models import LightState, GPIOOutputDevice, GPIODeviceAction, GPIOInputDevice

pirSensors = []
timeZone = pytz.timezone("America/Montevideo")
sharedMemory = redis.Redis(host='127.0.0.1', port=6379, db=0)

def isLit():
    try:
        light_state = LightState.objects.latest()
    except LightState.DoesNotExist:
        light_state = None
    return light_state is None or not light_state.isDark

def saveDeviceAction(device, status, tmstmp):
    action = GPIODeviceAction()
    action.dateOfUse = tmstmp
    action.status = status
    action.isAutomatic = True
    action.device = device
    action.save()
    # set device status
    device.status = status
    device.save()

def initSensors():
    global pirSensors
    pirSensors = GPIOInputDevice.objects.filter(enabled=True, address='127.0.0.1', type__name = 'PIR Sensor')
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
            devices = GPIOOutputDevice.objects.filter(enabled=True, autoEnabled=True, address='127.0.0.1', type__name = 'Relay', status=True)
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
       
    def run(self):
        global timeZone
        previous_state = False
        while True:
            movement = GPIO.input(self.sensor.pinNumber) == 1
            if movement:
                if movement != previous_state:  # avoid repeating the same signal
                    logger.debug("Movement detected in " + str(self.sensor.pinNumber))
                    # turn on devices only if it's dark
                    if not isLit():
                        logger.debug("The environment is dark")
                        devices = GPIOOutputDevice.objects.filter(enabled=True, autoEnabled=True, address='127.0.0.1', type__name = 'Relay')
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
                        logger.debug("The environment is lit")
                        #             alarm = Alarm.objects.last()
                        #             if alarm.armed:
                        #                 triggerAlarm()
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
    GPIO.cleanup()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()

# def triggerAlarm():
#     if notify("Alarma disparada"):
#         alarm = Alarm()
#         alarm.fired = True
#         alarm.save()

